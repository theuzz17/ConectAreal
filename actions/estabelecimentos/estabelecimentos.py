from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from flask_login import login_required, current_user
from models import db, Estabelecimento, Avaliacao, User
from sqlalchemy import or_, and_
from datetime import datetime

estabelecimentos_bp = Blueprint('estabelecimentos', __name__, url_prefix='/estabelecimentos')


@estabelecimentos_bp.route('/', methods=['GET'])
def listar_estabelecimentos():
    pagina = request.args.get('pagina', 1, type=int)
    categoria = request.args.get('categoria', '', type=str)
    busca = request.args.get('busca', '', type=str)
    
    query = Estabelecimento.query.filter_by(ativo=True)
    
    if categoria:
        query = query.filter_by(categoria=categoria)
    
    if busca:
        query = query.filter(
            or_(
                Estabelecimento.nome.ilike(f'%{busca}%'),
                Estabelecimento.descricao.ilike(f'%{busca}%'),
                Estabelecimento.localizacao.ilike(f'%{busca}%')
            )
        )
    
    estabelecimentos = query.paginate(page=pagina, per_page=12)
    
    return render_template('estabelecimentos.html', estabelecimentos=estabelecimentos)


@estabelecimentos_bp.route('/api/listar', methods=['GET'])
def api_listar():
    try:
        pagina = request.args.get('pagina', 1, type=int)
        categoria = request.args.get('categoria', '', type=str)
        busca = request.args.get('busca', '', type=str)
        por_pagina = request.args.get('por_pagina', 12, type=int)
        
        query = Estabelecimento.query.filter_by(ativo=True)
        
        if categoria:
            query = query.filter_by(categoria=categoria)
        
        if busca:
            query = query.filter(
                or_(
                    Estabelecimento.nome.ilike(f'%{busca}%'),
                    Estabelecimento.descricao.ilike(f'%{busca}%'),
                    Estabelecimento.localizacao.ilike(f'%{busca}%')
                )
            )
        
        estabelecimentos = query.order_by(Estabelecimento.criado_em.desc()).paginate(
            page=pagina, 
            per_page=por_pagina
        )
        
        dados = {
            'sucesso': True,
            'estabelecimentos': [e.to_dict() for e in estabelecimentos.items],
            'total': estabelecimentos.total,
            'paginas': estabelecimentos.pages,
            'pagina_atual': pagina
        }
        
        return jsonify(dados), 200
    
    except Exception as e:
        current_app.logger.error(f'Erro ao listar estabelecimentos: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao listar estabelecimentos'
        }), 500


@estabelecimentos_bp.route('/<int:id>', methods=['GET'])
def detalhes_estabelecimento(id):
    estabelecimento = Estabelecimento.query.get_or_404(id)
    
    if not estabelecimento.ativo:
        return redirect(url_for('estabelecimentos.listar_estabelecimentos'))
    
    avaliacoes = Avaliacao.query.filter_by(estabelecimento_id=id).all()
    
    return render_template(
        'detalhes_estabelecimento.html',
        estabelecimento=estabelecimento,
        avaliacoes=avaliacoes
    )


@estabelecimentos_bp.route('/api/<int:id>', methods=['GET'])
def api_detalhes(id):
    try:
        estabelecimento = Estabelecimento.query.get_or_404(id)
        
        if not estabelecimento.ativo:
            return jsonify({
                'sucesso': False,
                'erro': 'Estabelecimento não encontrado'
            }), 404
        
        avaliacoes = Avaliacao.query.filter_by(estabelecimento_id=id).all()
        
        nota_media = 0
        if avaliacoes:
            soma = sum(a.nota for a in avaliacoes)
            nota_media = soma / len(avaliacoes)
        
        dados_estabelecimento = estabelecimento.to_dict()
        dados_estabelecimento['nota_media'] = round(nota_media, 1)
        dados_estabelecimento['total_avaliacoes'] = len(avaliacoes)
        dados_estabelecimento['avaliacoes'] = [a.to_dict() for a in avaliacoes]
        dados_estabelecimento['usuario'] = {
            'id': estabelecimento.usuario.id,
            'username': estabelecimento.usuario.username
        }
        
        return jsonify({
            'sucesso': True,
            'estabelecimento': dados_estabelecimento
        }), 200
    
    except Exception as e:
        current_app.logger.error(f'Erro ao obter detalhes: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao obter detalhes do estabelecimento'
        }), 500


@estabelecimentos_bp.route('/criar', methods=['GET'])
@login_required
def criar_estabelecimento_page():
    return render_template('criar_estabelecimento.html')


@estabelecimentos_bp.route('/api/criar', methods=['POST'])
@login_required
def api_criar():
    try:
        dados = request.get_json() or {}
        
        nome = (dados.get('nome') or '').strip()
        categoria = (dados.get('categoria') or '').strip()
        descricao = (dados.get('descricao') or '').strip()
        telefone = (dados.get('telefone') or '').strip()
        email = (dados.get('email') or '').strip()
        endereco = (dados.get('endereco') or '').strip()
        localizacao = (dados.get('localizacao') or '').strip()
        website = (dados.get('website') or '').strip()
        horario = (dados.get('horario_funcionamento') or '').strip()
        
        if not nome or not categoria or not descricao:
            return jsonify({
                'sucesso': False,
                'erro': 'Nome, categoria e descrição são obrigatórios'
            }), 400
        
        if len(nome) < 3 or len(nome) > 255:
            return jsonify({
                'sucesso': False,
                'erro': 'Nome deve ter entre 3 e 255 caracteres'
            }), 400
        
        if len(descricao) < 10:
            return jsonify({
                'sucesso': False,
                'erro': 'Descrição deve ter no mínimo 10 caracteres'
            }), 400
        
        categorias_validas = ['profissionais', 'comercios', 'servicos', 'instituicoes']
        if categoria not in categorias_validas:
            return jsonify({
                'sucesso': False,
                'erro': f'Categoria inválida. Válidas: {", ".join(categorias_validas)}'
            }), 400
        
        novo_estabelecimento = Estabelecimento(
            usuario_id=current_user.id,
            nome=nome,
            categoria=categoria,
            descricao=descricao,
            telefone=telefone if telefone else None,
            email=email if email else None,
            endereco=endereco if endereco else None,
            localizacao=localizacao if localizacao else None,
            website=website if website else None,
            horario_funcionamento=horario if horario else None
        )
        
        db.session.add(novo_estabelecimento)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Estabelecimento criado com sucesso!',
            'estabelecimento': novo_estabelecimento.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao criar estabelecimento: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao criar estabelecimento'
        }), 500


@estabelecimentos_bp.route('/editar/<int:id>', methods=['GET'])
@login_required
def editar_estabelecimento_page(id):
    estabelecimento = Estabelecimento.query.get_or_404(id)
    
    if estabelecimento.usuario_id != current_user.id and not current_user.is_admin:
        return redirect(url_for('estabelecimentos.listar_estabelecimentos'))
    
    return render_template('editar_estabelecimento.html', estabelecimento=estabelecimento)


@estabelecimentos_bp.route('/api/editar/<int:id>', methods=['PUT'])
@login_required
def api_editar(id):
    try:
        estabelecimento = Estabelecimento.query.get_or_404(id)
        
        if estabelecimento.usuario_id != current_user.id and not current_user.is_admin:
            return jsonify({
                'sucesso': False,
                'erro': 'Sem permissão para editar'
            }), 403
        
        dados = request.get_json() or {}
        
        if 'nome' in dados:
            nome = (dados['nome'] or '').strip()
            if not nome or len(nome) < 3:
                return jsonify({
                    'sucesso': False,
                    'erro': 'Nome inválido'
                }), 400
            estabelecimento.nome = nome
        
        if 'categoria' in dados:
            categoria = (dados['categoria'] or '').strip()
            categorias_validas = ['profissionais', 'comercios', 'servicos', 'instituicoes']
            if categoria not in categorias_validas:
                return jsonify({
                    'sucesso': False,
                    'erro': 'Categoria inválida'
                }), 400
            estabelecimento.categoria = categoria
        
        if 'descricao' in dados:
            descricao = (dados['descricao'] or '').strip()
            if len(descricao) < 10:
                return jsonify({
                    'sucesso': False,
                    'erro': 'Descrição inválida'
                }), 400
            estabelecimento.descricao = descricao
        
        if 'telefone' in dados:
            estabelecimento.telefone = (dados['telefone'] or '').strip() or None
        
        if 'email' in dados:
            estabelecimento.email = (dados['email'] or '').strip() or None
        
        if 'endereco' in dados:
            estabelecimento.endereco = (dados['endereco'] or '').strip() or None
        
        if 'localizacao' in dados:
            estabelecimento.localizacao = (dados['localizacao'] or '').strip() or None
        
        if 'website' in dados:
            estabelecimento.website = (dados['website'] or '').strip() or None
        
        if 'horario_funcionamento' in dados:
            estabelecimento.horario_funcionamento = (dados['horario_funcionamento'] or '').strip() or None
        
        estabelecimento.atualizado_em = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Estabelecimento atualizado com sucesso!',
            'estabelecimento': estabelecimento.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao editar estabelecimento: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao editar estabelecimento'
        }), 500


@estabelecimentos_bp.route('/api/deletar/<int:id>', methods=['DELETE'])
@login_required
def api_deletar(id):
    try:
        estabelecimento = Estabelecimento.query.get_or_404(id)
        
        if estabelecimento.usuario_id != current_user.id and not current_user.is_admin:
            return jsonify({
                'sucesso': False,
                'erro': 'Sem permissão para deletar'
            }), 403
        
        db.session.delete(estabelecimento)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Estabelecimento deletado com sucesso!'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao deletar estabelecimento: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao deletar estabelecimento'
        }), 500


@estabelecimentos_bp.route('/api/avaliar/<int:id>', methods=['POST'])
@login_required
def api_avaliar(id):
    try:
        estabelecimento = Estabelecimento.query.get_or_404(id)
        dados = request.get_json() or {}
        
        nota = dados.get('nota')
        comentario = (dados.get('comentario') or '').strip()
        
        if not isinstance(nota, int) or nota < 1 or nota > 5:
            return jsonify({
                'sucesso': False,
                'erro': 'Nota deve ser um número entre 1 e 5'
            }), 400
        
        avaliacao_existente = Avaliacao.query.filter_by(
            estabelecimento_id=id,
            usuario_id=current_user.id
        ).first()
        
        if avaliacao_existente:
            avaliacao_existente.nota = nota
            avaliacao_existente.comentario = comentario if comentario else None
            mensagem = 'Avaliação atualizada com sucesso!'
        else:
            avaliacao = Avaliacao(
                estabelecimento_id=id,
                usuario_id=current_user.id,
                nota=nota,
                comentario=comentario if comentario else None
            )
            db.session.add(avaliacao)
            mensagem = 'Avaliação criada com sucesso!'
        
        db.session.commit()
        
        avaliacoes = Avaliacao.query.filter_by(estabelecimento_id=id).all()
        nota_media = sum(a.nota for a in avaliacoes) / len(avaliacoes) if avaliacoes else 0
        
        return jsonify({
            'sucesso': True,
            'mensagem': mensagem,
            'nota_media': round(nota_media, 1),
            'total_avaliacoes': len(avaliacoes)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao avaliar: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao registrar avaliação'
        }), 500


@estabelecimentos_bp.route('/api/meus', methods=['GET'])
@login_required
def api_meus_estabelecimentos():
    try:
        pagina = request.args.get('pagina', 1, type=int)
        
        estabelecimentos = Estabelecimento.query.filter_by(
            usuario_id=current_user.id
        ).order_by(Estabelecimento.criado_em.desc()).paginate(page=pagina, per_page=10)
        
        return jsonify({
            'sucesso': True,
            'estabelecimentos': [e.to_dict() for e in estabelecimentos.items],
            'total': estabelecimentos.total,
            'paginas': estabelecimentos.pages,
            'pagina_atual': pagina
        }), 200
    
    except Exception as e:
        current_app.logger.error(f'Erro ao listar meus estabelecimentos: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao listar estabelecimentos'
        }), 500


@estabelecimentos_bp.route('/api/categorias', methods=['GET'])
def api_categorias():
    return jsonify({
        'sucesso': True,
        'categorias': [
            {'id': 'profissionais', 'nome': 'Profissionais'},
            {'id': 'comercios', 'nome': 'Comércios'},
            {'id': 'servicos', 'nome': 'Serviços'},
            {'id': 'instituicoes', 'nome': 'Instituições'}
        ]
    }), 200
