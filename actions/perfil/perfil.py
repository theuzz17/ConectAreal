from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from flask_login import login_required, current_user
from models import db, User, Estabelecimento, Avaliacao
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import re

perfil_bp = Blueprint('perfil', __name__, url_prefix='/perfil')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/uploads/perfil'

def arquivo_permitido(nome_arquivo):
    return '.' in nome_arquivo and nome_arquivo.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validar_email(email):
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None

def validar_telefone(telefone):
    padrao = r'^\(\d{2}\)\s?\d{4,5}-\d{4}$|^\d{10,11}$'
    return re.match(padrao, telefone) is not None if telefone else True


@perfil_bp.route('/', methods=['GET'])
@login_required
def perfil_page():
    user = current_user
    estabelecimentos = Estabelecimento.query.filter_by(usuario_id=user.id).count()
    avaliacoes = Avaliacao.query.filter_by(usuario_id=user.id).count()
    
    return render_template('perfil.html', 
                         user=user,
                         total_estabelecimentos=estabelecimentos,
                         total_avaliacoes=avaliacoes)


@perfil_bp.route('/api', methods=['GET'])
@login_required
def api_obter_perfil():
    try:
        user = current_user
        
        estabelecimentos = Estabelecimento.query.filter_by(usuario_id=user.id).count()
        avaliacoes = Avaliacao.query.filter_by(usuario_id=user.id).count()
        
        return jsonify({
            'sucesso': True,
            'usuario': user.to_dict(),
            'total_estabelecimentos': estabelecimentos,
            'total_avaliacoes': avaliacoes
        }), 200
    
    except Exception as e:
        current_app.logger.error(f'Erro ao obter perfil: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao obter perfil'
        }), 500


@perfil_bp.route('/api/atualizar', methods=['PUT'])
@login_required
def api_atualizar_perfil():
    try:
        dados = request.get_json() or {}
        user = current_user
        
        if 'nome_completo' in dados:
            nome_completo = (dados['nome_completo'] or '').strip()
            if nome_completo and len(nome_completo) > 255:
                return jsonify({
                    'sucesso': False,
                    'erro': 'Nome completo pode ter no máximo 255 caracteres'
                }), 400
            user.nome_completo = nome_completo if nome_completo else None
        
        if 'telefone' in dados:
            telefone = (dados['telefone'] or '').strip()
            if telefone and not validar_telefone(telefone):
                return jsonify({
                    'sucesso': False,
                    'erro': 'Telefone inválido. Use o formato (XX) XXXXX-XXXX'
                }), 400
            user.telefone = telefone if telefone else None
        
        if 'data_nascimento' in dados:
            data_nasc = dados['data_nascimento']
            if data_nasc:
                try:
                    datetime.strptime(data_nasc, '%Y-%m-%d')
                    user.data_nascimento = data_nasc
                except ValueError:
                    return jsonify({
                        'sucesso': False,
                        'erro': 'Data inválida. Use o formato YYYY-MM-DD'
                    }), 400
            else:
                user.data_nascimento = None
        
        if 'bio' in dados:
            bio = (dados['bio'] or '').strip()
            if bio and len(bio) > 500:
                return jsonify({
                    'sucesso': False,
                    'erro': 'Bio pode ter no máximo 500 caracteres'
                }), 400
            user.bio = bio if bio else None
        
        if 'endereco' in dados:
            endereco = (dados['endereco'] or '').strip()
            if endereco and len(endereco) > 255:
                return jsonify({
                    'sucesso': False,
                    'erro': 'Endereço pode ter no máximo 255 caracteres'
                }), 400
            user.endereco = endereco if endereco else None
        
        if 'bairro' in dados:
            bairro = (dados['bairro'] or '').strip()
            if bairro and len(bairro) > 100:
                return jsonify({
                    'sucesso': False,
                    'erro': 'Bairro pode ter no máximo 100 caracteres'
                }), 400
            user.bairro = bairro if bairro else None
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Perfil atualizado com sucesso!',
            'usuario': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao atualizar perfil: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao atualizar perfil'
        }), 500


@perfil_bp.route('/api/alterar-email', methods=['PUT'])
@login_required
def api_alterar_email():
    try:
        dados = request.get_json() or {}
        senha = dados.get('senha') or ''
        novo_email = (dados.get('novo_email') or '').strip()
        
        if not novo_email:
            return jsonify({
                'sucesso': False,
                'erro': 'Email obrigatório'
            }), 400
        
        if not current_user.check_password(senha):
            return jsonify({
                'sucesso': False,
                'erro': 'Senha incorreta'
            }), 401
        
        if not validar_email(novo_email):
            return jsonify({
                'sucesso': False,
                'erro': 'Email inválido'
            }), 400
        
        email_existente = User.query.filter_by(email=novo_email).first()
        if email_existente and email_existente.id != current_user.id:
            return jsonify({
                'sucesso': False,
                'erro': 'Este email já está em uso'
            }), 400
        
        current_user.email = novo_email
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Email alterado com sucesso!',
            'usuario': current_user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao alterar email: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao alterar email'
        }), 500


@perfil_bp.route('/api/alterar-senha', methods=['PUT'])
@login_required
def api_alterar_senha():
    try:
        dados = request.get_json() or {}
        senha_atual = dados.get('senha_atual') or ''
        nova_senha = dados.get('nova_senha') or ''
        confirmar_senha = dados.get('confirmar_senha') or ''
        
        if not senha_atual or not nova_senha or not confirmar_senha:
            return jsonify({
                'sucesso': False,
                'erro': 'Todos os campos são obrigatórios'
            }), 400
        
        if not current_user.check_password(senha_atual):
            return jsonify({
                'sucesso': False,
                'erro': 'Senha atual incorreta'
            }), 401
        
        if nova_senha != confirmar_senha:
            return jsonify({
                'sucesso': False,
                'erro': 'Novas senhas não coincidem'
            }), 400
        
        if len(nova_senha) < 6:
            return jsonify({
                'sucesso': False,
                'erro': 'Nova senha deve ter no mínimo 6 caracteres'
            }), 400
        
        if nova_senha == senha_atual:
            return jsonify({
                'sucesso': False,
                'erro': 'Nova senha deve ser diferente da atual'
            }), 400
        
        current_user.set_password(nova_senha)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Senha alterada com sucesso!'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao alterar senha: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao alterar senha'
        }), 500


@perfil_bp.route('/api/excluir-conta', methods=['DELETE'])
@login_required
def api_excluir_conta():
    try:
        dados = request.get_json() or {}
        senha = dados.get('senha') or ''
        
        if not senha:
            return jsonify({
                'sucesso': False,
                'erro': 'Senha é obrigatória'
            }), 400
        
        if not current_user.check_password(senha):
            return jsonify({
                'sucesso': False,
                'erro': 'Senha incorreta'
            }), 401
        
        user_id = current_user.id
        
        Avaliacao.query.filter_by(usuario_id=user_id).delete()
        
        estabelecimentos = Estabelecimento.query.filter_by(usuario_id=user_id).all()
        for estab in estabelecimentos:
            Avaliacao.query.filter_by(estabelecimento_id=estab.id).delete()
        Estabelecimento.query.filter_by(usuario_id=user_id).delete()
        
        User.query.filter_by(id=user_id).delete()
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Conta excluída com sucesso'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao excluir conta: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao excluir conta'
        }), 500


@perfil_bp.route('/api/historico-login', methods=['GET'])
@login_required
def api_historico_login():
    try:
        user = current_user
        
        return jsonify({
            'sucesso': True,
            'ultimo_login': user.last_login.isoformat() if user.last_login else None,
            'data_criacao': user.created_at.isoformat() if user.created_at else None
        }), 200
    
    except Exception as e:
        current_app.logger.error(f'Erro ao obter histórico: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao obter histórico'
        }), 500


@perfil_bp.route('/api/atividades', methods=['GET'])
@login_required
def api_atividades():
    try:
        user = current_user
        pagina = request.args.get('pagina', 1, type=int)
        
        estabelecimentos = Estabelecimento.query.filter_by(usuario_id=user.id)\
            .order_by(Estabelecimento.criado_em.desc())\
            .paginate(page=pagina, per_page=10)
        
        atividades = {
            'estabelecimentos_criados': [e.to_dict() for e in estabelecimentos.items],
            'total': estabelecimentos.total,
            'paginas': estabelecimentos.pages,
            'pagina_atual': pagina
        }
        
        avaliacoes = Avaliacao.query.filter_by(usuario_id=user.id)\
            .order_by(Avaliacao.criado_em.desc())\
            .all()
        
        atividades['avaliacoes'] = [a.to_dict() for a in avaliacoes[:5]]
        
        return jsonify({
            'sucesso': True,
            'atividades': atividades
        }), 200
    
    except Exception as e:
        current_app.logger.error(f'Erro ao obter atividades: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao obter atividades'
        }), 500
