from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import current_user, login_required
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import current_user, login_required
from functools import wraps
from models import db, User, ContactMessage, Newsletter, Estabelecimento, Avaliacao
from mail import enviar_resposta_mensagem
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
import re

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def requer_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@requer_admin
def painel():
    return render_template('admin_painel_novo.html')

@admin_bp.route('/api/dashboard')
@login_required
@requer_admin
def obter_dashboard():
    try:
        total_usuarios = User.query.count()
        usuarios_ativos = User.query.filter_by(is_active=True).count()
        usuarios_inativos = User.query.filter_by(is_active=False).count()
        admins = User.query.filter_by(is_admin=True).count()
        
        total_estabelecimentos = Estabelecimento.query.count()
        estabelecimentos_verificados = Estabelecimento.query.filter_by(verificado=True).count()
        estabelecimentos_ativos = Estabelecimento.query.filter_by(ativo=True).count()
        
        total_avaliacoes = Avaliacao.query.count()
        media_avaliacoes = db.session.query(func.avg(Avaliacao.nota)).scalar() or 0
        
        mensagens_nao_lidas = ContactMessage.query.filter_by(lido=False).count()
        total_mensagens = ContactMessage.query.count()
        
        usuarios_novos_7dias = User.query.filter(
            User.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        estabelecimentos_novos_7dias = Estabelecimento.query.filter(
            Estabelecimento.criado_em >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        usuarios_com_estabelecimento = db.session.query(
            func.count(func.distinct(Estabelecimento.usuario_id))
        ).scalar() or 0
        
        estatisticas_por_categoria = db.session.query(
            Estabelecimento.categoria,
            func.count(Estabelecimento.id).label('total')
        ).group_by(Estabelecimento.categoria).all()
        
        dados = {
            'usuarios': {
                'total': total_usuarios,
                'ativos': usuarios_ativos,
                'inativos': usuarios_inativos,
                'admins': admins,
                'novos_7dias': usuarios_novos_7dias,
                'com_estabelecimento': usuarios_com_estabelecimento
            },
            'estabelecimentos': {
                'total': total_estabelecimentos,
                'verificados': estabelecimentos_verificados,
                'nao_verificados': total_estabelecimentos - estabelecimentos_verificados,
                'ativos': estabelecimentos_ativos,
                'inativos': total_estabelecimentos - estabelecimentos_ativos,
                'novos_7dias': estabelecimentos_novos_7dias
            },
            'avaliacoes': {
                'total': total_avaliacoes,
                'media': round(float(media_avaliacoes), 2)
            },
            'mensagens': {
                'nao_lidas': mensagens_nao_lidas,
                'total': total_mensagens
            },
            'categorias': [
                {'categoria': cat, 'total': total}
                for cat, total in estatisticas_por_categoria
            ]
        }
        
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@admin_bp.route('/api/usuarios')
@login_required
@requer_admin
def listar_usuarios():
    try:
        pagina = request.args.get('pagina', 1, type=int)
        buscar = request.args.get('buscar', '', type=str)
        filtro = request.args.get('filtro', 'todos', type=str)
        
        query = User.query
        
        if buscar:
            query = query.filter(or_(
                User.username.ilike(f'%{buscar}%'),
                User.email.ilike(f'%{buscar}%'),
                User.nome_completo.ilike(f'%{buscar}%')
            ))
        
        if filtro == 'ativos':
            query = query.filter_by(is_active=True)
        elif filtro == 'inativos':
            query = query.filter_by(is_active=False)
        elif filtro == 'admins':
            query = query.filter_by(is_admin=True)
        elif filtro == 'com_estabelecimento':
            usuarios_com_estab = db.session.query(func.distinct(Estabelecimento.usuario_id)).all()
            ids = [u[0] for u in usuarios_com_estab]
            query = query.filter(User.id.in_(ids))
        
        usuarios = query.order_by(User.created_at.desc()).paginate(page=pagina, per_page=15)
        
        dados = {
            'usuarios': [
                {
                    'id': u.id,
                    'username': u.username,
                    'email': u.email,
                    'nome_completo': u.nome_completo,
                    'is_admin': u.is_admin,
                    'is_active': u.is_active,
                    'email_confirmed': u.email_confirmed,
                    'criado_em': u.created_at.strftime('%d/%m/%Y %H:%M') if u.created_at else '',
                    'ultimo_acesso': u.last_login.strftime('%d/%m/%Y %H:%M') if u.last_login else 'Nunca',
                    'estabelecimentos': len(u.estabelecimentos) if hasattr(u, 'estabelecimentos') else 0
                }
                for u in usuarios.items
            ],
            'total': usuarios.total,
            'paginas': usuarios.pages,
            'pagina_atual': pagina
        }
        
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@admin_bp.route('/api/usuarios/<int:usuario_id>/toggle-admin', methods=['POST'])
@login_required
@requer_admin
def toggle_admin(usuario_id):
    try:
        if usuario_id == current_user.id:
            return jsonify({'erro': 'Não pode alterar seu próprio status de admin'}), 400
        
        usuario = User.query.get(usuario_id)
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        usuario.is_admin = not usuario.is_admin
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Status de admin alterado com sucesso',
            'is_admin': usuario.is_admin
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500
