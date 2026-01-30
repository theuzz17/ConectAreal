from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import current_user
from config import config
from models import db, User, ContactMessage, Newsletter
from auth import auth_bp, init_login_manager
from estabelecimentos import estabelecimentos_bp
from perfil import perfil_bp
from mail import mail, send_contact_notification, send_email_async
from admin import admin_bp
from flask_migrate import Migrate
from datetime import datetime
import re
import os
from mail import enviar_resposta_mensagem
from models import ContactMessage

app = Flask(__name__)

env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

db.init_app(app)
mail.init_app(app)
init_login_manager(app)

migrate = Migrate(app, db)

app.register_blueprint(auth_bp)
app.register_blueprint(estabelecimentos_bp)
app.register_blueprint(perfil_bp)
app.register_blueprint(admin_bp)

estabelecimentos = [
    {
        "id": 1,
        "titulo": "Encanador Profissional",
        "categoria": "profissionais",
        "descricao": "Serviços de encanamento residencial e comercial com garantia",
        "avaliacao": 4.8,
        "avaliacoes": 24,
        "localizacao": "Centro do Bairro"
    },
    {
        "id": 2,
        "titulo": "Padaria Artesanal",
        "categoria": "comercios",
        "descricao": "Pães frescos e bolos caseiros todos os dias",
        "avaliacao": 4.9,
        "avaliacoes": 45,
        "localizacao": "Rua Principal"
    },
    {
        "id": 3,
        "titulo": "Aulas de Reforço Escolar",
        "categoria": "servicos",
        "descricao": "Reforço em matemática, português e inglês para crianças",
        "avaliacao": 4.7,
        "avaliacoes": 18,
        "localizacao": "Próximo à Escola"
    },
    {
        "id": 4,
        "titulo": "Clínica de Saúde",
        "categoria": "instituicoes",
        "descricao": "Atendimento médico geral e especializado com agendamento",
        "avaliacao": 4.6,
        "avaliacoes": 52,
        "localizacao": "Avenida Central"
    },
    {
        "id": 5,
        "titulo": "Salão de Beleza",
        "categoria": "comercios",
        "descricao": "Cabelo, manicure, pedicure e estética facial",
        "avaliacao": 4.8,
        "avaliacoes": 36,
        "localizacao": "Rua das Flores"
    },
    {
        "id": 6,
        "titulo": "Aulas de Yoga",
        "categoria": "servicos",
        "descricao": "Bem-estar e equilíbrio corpo e mente para todas as idades",
        "avaliacao": 4.9,
        "avaliacoes": 28,
        "localizacao": "Parque do Bairro"
    },
    {
        "id": 7,
        "titulo": "Eletricista",
        "categoria": "profissionais",
        "descricao": "Instalações elétricas e manutenção com segurança",
        "avaliacao": 4.7,
        "avaliacoes": 31,
        "localizacao": "Zona Residencial"
    },
    {
        "id": 8,
        "titulo": "Supermercado Local",
        "categoria": "comercios",
        "descricao": "Alimentos frescos, bebidas e produtos de limpeza",
        "avaliacao": 4.5,
        "avaliacoes": 67,
        "localizacao": "Avenida Principal"
    },
    {
        "id": 9,
        "titulo": "Consultório Odontológico",
        "categoria": "instituicoes",
        "descricao": "Limpeza, restauração e tratamentos dentários",
        "avaliacao": 4.8,
        "avaliacoes": 43,
        "localizacao": "Centro"
    },
    {
        "id": 10,
        "titulo": "Aulas de Inglês",
        "categoria": "servicos",
        "descricao": "Inglês para crianças, adolescentes e adultos",
        "avaliacao": 4.6,
        "avaliacoes": 22,
        "localizacao": "Centro Educacional"
    }
]

prestadores = [
    {
        "id": 1,
        "nome": "João Silva",
        "profissao": "Encanador",
        "especialidades": ["Encanamento", "Hidráulica", "Manutenção"],
        "avaliacao": 4.8,
        "avaliacoes": 24,
        "localizacao": "Centro do Bairro",
        "telefone": "(11) 98765-4321",
        "descricao": "Profissional experiente em serviços de encanamento residencial e comercial com garantia de qualidade.",
        "verificado": True
    },
    {
        "id": 2,
        "nome": "Maria Santos",
        "profissao": "Eletricista",
        "especialidades": ["Instalações", "Manutenção", "Projetos"],
        "avaliacao": 4.7,
        "avaliacoes": 31,
        "localizacao": "Zona Residencial",
        "telefone": "(11) 5555-6666",
        "descricao": "Eletricista certificada com experiência em instalações elétricas seguras e eficientes.",
        "verificado": True
    },
    {
        "id": 3,
        "nome": "Carlos Oliveira",
        "profissao": "Pintor",
        "especialidades": ["Pintura Residencial", "Pintura Comercial", "Restauração"],
        "avaliacao": 4.6,
        "avaliacoes": 18,
        "localizacao": "Bairro Central",
        "telefone": "(11) 7777-8888",
        "descricao": "Pintor profissional especializado em acabamentos de qualidade e cores personalizadas.",
        "verificado": False
    },
    {
        "id": 4,
        "nome": "Ana Costa",
        "profissao": "Personal Trainer",
        "especialidades": ["Musculação", "Cardio", "Treinamento Funcional"],
        "avaliacao": 4.9,
        "avaliacoes": 42,
        "localizacao": "Parque do Bairro",
        "telefone": "(11) 9999-0000",
        "descricao": "Personal trainer certificada com foco em resultados e bem-estar do cliente.",
        "verificado": True
    },
    {
        "id": 5,
        "nome": "Roberto Ferreira",
        "profissao": "Carpinteiro",
        "especialidades": ["Móveis", "Reformas", "Acabamentos"],
        "avaliacao": 4.5,
        "avaliacoes": 22,
        "localizacao": "Rua Principal",
        "telefone": "(11) 4444-5555",
        "descricao": "Carpinteiro experiente em projetos personalizados e acabamentos refinados.",
        "verificado": True
    },
    {
        "id": 6,
        "nome": "Fernanda Lima",
        "profissao": "Professora Particular",
        "especialidades": ["Matemática", "Português", "Inglês"],
        "avaliacao": 4.8,
        "avaliacoes": 28,
        "localizacao": "Centro Educacional",
        "telefone": "(11) 3333-4444",
        "descricao": "Professora dedicada com metodologia comprovada para melhoria de desempenho escolar.",
        "verificado": True
    }
]

mensagens_contato = []

usuarios_admin = {
    'admin': {
        'senha': '123456',
        'nome': 'Administrador'
    }
}


@app.before_request
def require_login_admin():
    if request.path.startswith('/admin'):
        if request.path == '/admin/login' or request.path == '/api/admin/login':
            return
        if 'usuario_admin' not in session:
            return redirect(url_for('login_admin'))


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login_page'))

    return render_template('index.html', 
                         estabelecimentos=estabelecimentos,
                         prestadores=prestadores)


@app.route('/api/estabelecimentos', methods=['GET'])
def get_estabelecimentos():
    filtro = request.args.get('filtro', 'todos')
    termo_busca = request.args.get('busca', '').lower()
    
    filtrados = estabelecimentos
    
    if filtro != 'todos':
        filtrados = [e for e in filtrados if e['categoria'] == filtro]
    
    if termo_busca:
        filtrados = [e for e in filtrados if 
                    termo_busca in e['titulo'].lower() or 
                    termo_busca in e['descricao'].lower()]
    
    return jsonify(filtrados)


@app.route('/api/prestadores', methods=['GET'])
def get_prestadores():
    return jsonify(prestadores)


@app.route('/api/contato', methods=['POST'])
def enviar_contato():
    try:
        data = request.get_json()
        
        nome = (data.get('nome') or '').strip()
        email = (data.get('email') or '').strip()
        telefone = re.sub(r'\D', '', data.get('telefone', ''))
        assunto = (data.get('assunto') or '').strip()
        mensagem = (data.get('mensagem') or '').strip()
        
        if not nome or not email or not assunto or not mensagem:
            return jsonify({
                'sucesso': False,
                'erro': 'Todos os campos obrigatórios devem ser preenchidos.'
            }), 400
        
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return jsonify({
                'sucesso': False,
                'erro': 'Por favor, informe um email válido.'
            }), 400
        
        if telefone and len(telefone) != 11:
            return jsonify({
                'sucesso': False,
                'erro': 'Por favor, informe um telefone com exatamente 11 dígitos.'
            }), 400
        
        contact_msg = ContactMessage(
            nome=nome,
            email=email,
            telefone=telefone,
            assunto=assunto,
            mensagem=mensagem
        )
        
        db.session.add(contact_msg)
        db.session.commit()
        try:
            send_contact_notification({
                'nome': nome,
                'email': email,
                'telefone': telefone,
                'assunto': assunto,
                'mensagem': mensagem
            })
        except Exception as e:
            app.logger.error(f'Erro ao enviar notificação de contato: {str(e)}')
        # Enviar resposta automática para quem entrou em contato
        try:
            subject_auto = 'Recebemos sua mensagem - ConectAreal'
            text_auto = 'A Conectareal agradece o seu contato. Em breve, retornaremos com mais informações.'
            sender_addr = app.config.get('MAIL_USERNAME') or app.config.get('MAIL_DEFAULT_SENDER') or 'conectareal@gmail.com'
            sent = send_email_async(subject_auto, email, text_auto, None, sender=sender_addr)
            if not sent:
                app.logger.error('Envio do email automático de agradecimento retornou False')
        except Exception as e:
            app.logger.error(f'Erro ao enviar resposta automática ao usuário: {str(e)}')
        
        return jsonify({
            'sucesso': True,
            'mensagem': f'Obrigado {nome}! Sua mensagem foi enviada com sucesso. Responderemos em breve.'
        }), 201
    
    except Exception as e:
        app.logger.error(f'Erro ao processar contato: {str(e)}')
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao enviar mensagem. Tente novamente.'
        }), 500


@app.route('/api/newsletter', methods=['POST'])
def subscribe_newsletter():
    try:
        data = request.get_json()
        email = (data.get('email') or '').strip()
        
        if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return jsonify({
                'sucesso': False,
                'erro': 'Email inválido'
            }), 400
        
        if Newsletter.query.filter_by(email=email).first():
            return jsonify({
                'sucesso': False,
                'erro': 'Este email já está inscrito na newsletter'
            }), 400
        
        newsletter = Newsletter(email=email, confirmado=True)
        db.session.add(newsletter)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Obrigado por se inscrever na nossa newsletter!'
        }), 201
    
    except Exception as e:
        app.logger.error(f'Erro ao inscrever newsletter: {str(e)}')
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao inscrever. Tente novamente.'
        }), 500


@app.route('/admin/login')
def login_admin():
    return render_template('admin_login.html')


@app.route('/api/admin/login', methods=['POST'])
def autenticar_admin():
    data = request.get_json()
    usuario = data.get('usuario', '').strip()
    senha = data.get('senha', '')
    
    if usuario == 'admin' and senha == '123456':
        session['usuario_admin'] = usuario
        return jsonify({
            'sucesso': True,
            'mensagem': 'Login realizado com sucesso'
        })
    
    return jsonify({
        'sucesso': False,
        'erro': 'Usuário ou senha inválidos'
    }), 401


@app.route('/admin')
def painel_admin():
    return render_template('admin_painel.html')


@app.route('/api/admin/estabelecimentos', methods=['GET'])
def listar_estabelecimentos_admin():
    return jsonify(estabelecimentos)


@app.route('/api/admin/estabelecimentos', methods=['POST'])
def criar_estabelecimento():
    data = request.get_json()
    
    novo_id = max([e['id'] for e in estabelecimentos]) + 1 if estabelecimentos else 1
    
    novo_estabelecimento = {
        'id': novo_id,
        'titulo': data.get('titulo', ''),
        'categoria': data.get('categoria', ''),
        'descricao': data.get('descricao', ''),
        'avaliacao': data.get('avaliacao', 5.0),
        'avaliacoes': 0,
        'localizacao': data.get('localizacao', '')
    }
    
    if not novo_estabelecimento['titulo'] or not novo_estabelecimento['categoria']:
        return jsonify({'sucesso': False, 'erro': 'Título e categoria são obrigatórios'}), 400
    
    estabelecimentos.append(novo_estabelecimento)
    return jsonify({'sucesso': True, 'dados': novo_estabelecimento}), 201


@app.route('/api/admin/estabelecimentos/<int:id_est>', methods=['PUT'])
def atualizar_estabelecimento(id_est):
    data = request.get_json()
    
    for est in estabelecimentos:
        if est['id'] == id_est:
            est['titulo'] = data.get('titulo', est['titulo'])
            est['categoria'] = data.get('categoria', est['categoria'])
            est['descricao'] = data.get('descricao', est['descricao'])
            est['localizacao'] = data.get('localizacao', est['localizacao'])
            return jsonify({'sucesso': True, 'dados': est})
    
    return jsonify({'sucesso': False, 'erro': 'Estabelecimento não encontrado'}), 404


@app.route('/api/admin/estabelecimentos/<int:id_est>', methods=['DELETE'])
def deletar_estabelecimento(id_est):
    global estabelecimentos
    estabelecimentos = [e for e in estabelecimentos if e['id'] != id_est]
    return jsonify({'sucesso': True, 'mensagem': 'Estabelecimento deletado'})


@app.route('/api/admin/prestadores', methods=['GET'])
def listar_prestadores_admin():
    return jsonify(prestadores)


@app.route('/api/admin/prestadores', methods=['POST'])
def criar_prestador():
    data = request.get_json()
    
    novo_id = max([p['id'] for p in prestadores]) + 1 if prestadores else 1
    
    novo_prestador = {
        'id': novo_id,
        'nome': data.get('nome', ''),
        'profissao': data.get('profissao', ''),
        'especialidades': data.get('especialidades', []),
        'avaliacao': data.get('avaliacao', 5.0),
        'avaliacoes': 0,
        'localizacao': data.get('localizacao', ''),
        'telefone': data.get('telefone', ''),
        'descricao': data.get('descricao', ''),
        'verificado': data.get('verificado', False)
    }
    
    if not novo_prestador['nome'] or not novo_prestador['profissao']:
        return jsonify({'sucesso': False, 'erro': 'Nome e profissão são obrigatórios'}), 400
    
    prestadores.append(novo_prestador)
    return jsonify({'sucesso': True, 'dados': novo_prestador}), 201


@app.route('/api/admin/prestadores/<int:id_prest>', methods=['PUT'])
def atualizar_prestador(id_prest):
    data = request.get_json()
    
    for prest in prestadores:
        if prest['id'] == id_prest:
            prest['nome'] = data.get('nome', prest['nome'])
            prest['profissao'] = data.get('profissao', prest['profissao'])
            prest['especialidades'] = data.get('especialidades', prest['especialidades'])
            prest['localizacao'] = data.get('localizacao', prest['localizacao'])
            prest['telefone'] = data.get('telefone', prest['telefone'])
            prest['descricao'] = data.get('descricao', prest['descricao'])
            prest['verificado'] = data.get('verificado', prest['verificado'])
            return jsonify({'sucesso': True, 'dados': prest})
    
    return jsonify({'sucesso': False, 'erro': 'Prestador não encontrado'}), 404


@app.route('/api/admin/prestadores/<int:id_prest>', methods=['DELETE'])
def deletar_prestador(id_prest):
    global prestadores
    prestadores = [p for p in prestadores if p['id'] != id_prest]
    return jsonify({'sucesso': True, 'mensagem': 'Prestador deletado'})


@app.route('/api/admin/mensagens', methods=['GET'])
def listar_mensagens_admin():
    try:
        mensagens = ContactMessage.query.all()
        return jsonify([msg.to_dict() for msg in mensagens])
    except Exception as e:
        app.logger.error(f'Erro ao listar mensagens: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao listar mensagens'
        }), 500


@app.route('/api/admin/mensagens/<int:id_msg>', methods=['DELETE'])
def deletar_mensagem(id_msg):
    try:
        msg = ContactMessage.query.get(id_msg)
        if msg:
            db.session.delete(msg)
            db.session.commit()
            return jsonify({
                'sucesso': True,
                'mensagem': 'Mensagem deletada'
            })
        
        return jsonify({
            'sucesso': False,
            'erro': 'Mensagem não encontrada'
        }), 404
    except Exception as e:
        app.logger.error(f'Erro ao deletar mensagem: {str(e)}')
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao deletar mensagem'
        }), 500


@app.route('/api/admin/mensagens/<int:id_msg>/responder', methods=['POST'])
def responder_mensagem_admin(id_msg):
    try:
        dados = request.get_json() or {}
        resposta_texto = (dados.get('resposta') or '').strip()
        if not resposta_texto or len(resposta_texto) < 5:
            return jsonify({'sucesso': False, 'erro': 'A resposta deve ter pelo menos 5 caracteres'}), 400
        if len(resposta_texto) > 5000:
            return jsonify({'sucesso': False, 'erro': 'A resposta não pode ter mais de 5000 caracteres'}), 400

        msg = ContactMessage.query.get(id_msg)
        if not msg:
            return jsonify({'sucesso': False, 'erro': 'Mensagem não encontrada'}), 404

        sucesso = enviar_resposta_mensagem(
            destinatario_email=msg.email,
            nome_destinatario=msg.nome,
            assunto_original=msg.assunto,
            resposta_texto=resposta_texto,
            admin_nome=(getattr(current_user, 'username', 'Administrador') if 'current_user' in globals() else 'Administrador')
        )

        if not sucesso:
            return jsonify({'sucesso': False, 'erro': 'Falha ao enviar email. Verifique configuração SMTP.'}), 500

        msg.respondida = True
        msg.resposta = resposta_texto
        msg.respondida_em = datetime.utcnow()
        try:
            from flask_login import current_user as _cu
            msg.respondido_por = getattr(_cu, 'username', None)
        except Exception:
            pass

        db.session.commit()

        return jsonify({'sucesso': True, 'mensagem': 'Resposta enviada com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Erro ao responder mensagem: {str(e)}')
        return jsonify({'sucesso': False, 'erro': 'Erro ao processar a resposta'}), 500


@app.route('/api/admin/enviar-email-teste', methods=['POST'])
def enviar_email_teste():
    try:
        dados = request.get_json() or {}
        destinatario = dados.get('to') or dados.get('email')
        assunto = dados.get('assunto') or 'Teste de email - ConectAreal'
        mensagem = dados.get('mensagem') or 'Este é um email de teste enviado pelo servidor ConectAreal.'

        if not destinatario:
            return jsonify({'sucesso': False, 'erro': 'Destinatário não informado'}), 400

        sucesso = enviar_resposta_mensagem(
            destinatario_email=destinatario,
            nome_destinatario=destinatario.split('@')[0],
            assunto_original=assunto,
            resposta_texto=mensagem,
            admin_nome=(getattr(current_user, 'username', 'Administrador') if 'current_user' in globals() else 'Administrador')
        )

        if not sucesso:
            return jsonify({'sucesso': False, 'erro': 'Falha ao enviar email de teste'}), 500

        return jsonify({'sucesso': True, 'mensagem': 'Email de teste enviado com sucesso'}), 200
    except Exception as e:
        app.logger.error(f'Erro no envio de email de teste: {str(e)}')
        return jsonify({'sucesso': False, 'erro': 'Erro interno ao enviar email de teste'}), 500


@app.route('/admin/logout')
def logout_admin():
    session.pop('usuario_admin', None)
    return redirect(url_for('login_admin'))


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'sucesso': False,
        'erro': 'Página não encontrada'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    import traceback as _tb
    db.session.rollback()
    tb = _tb.format_exc()
    app.logger.error(f'Erro interno: {str(error)}\n{tb}')
    if app.debug:
        return jsonify({
            'sucesso': False,
            'erro': str(error),
            'traceback': tb
        }), 500

    return jsonify({
        'sucesso': False,
        'erro': 'Erro interno do servidor'
    }), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    # Use PORT and HOST do ambiente quando disponível (recomendado em PaaS)
    import os as _os
    _port = int(_os.environ.get('PORT', 80))
    _host = _os.environ.get('HOST', '0.0.0.0')

    # Usa o valor de DEBUG da configuração (False em produção)
    _debug = app.config.get('DEBUG', False)

    app.run(host=_host, port=_port, debug=_debug)
