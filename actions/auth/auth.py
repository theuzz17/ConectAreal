from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from mail import send_confirmation_email, send_password_reset_email, send_welcome_email, send_contact_notification, send_email_async
import secrets
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()


def init_login_manager(app):
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_page'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html')


@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json() or {}
        username_or_email = (data.get('username_or_email') or '').strip()
        password = data.get('password') or ''
        remember_me = data.get('remember_me', False)
        
        if not username_or_email or not password:
            return jsonify({
                'sucesso': False,
                'erro': 'Usuário e senha são obrigatórios'
            }), 400
        
        
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'sucesso': False,
                'erro': 'Usuário ou senha inválidos'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'sucesso': False,
                'erro': 'Esta conta foi desativada'
            }), 403
        
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=remember_me)
        
        return jsonify({
            'sucesso': True,
            'mensagem': f'Bem-vindo, {user.username}!',
            'usuario': user.to_dict()
        }), 200
    
    except Exception as e:
        current_app.logger.error(f'Erro no login: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao fazer login. Tente novamente.'
        }), 500


@auth_bp.route('/register', methods=['GET'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('register.html')


@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json() or {}
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''
        password_confirm = data.get('password_confirm') or ''
        email = (data.get('email') or '').strip()
        
        
        if not username or not password or not email:
            return jsonify({
                'sucesso': False,
                'erro': 'Todos os campos são obrigatórios'
            }), 400
        
        if len(username) < 3:
            return jsonify({
                'sucesso': False,
                'erro': 'Username deve ter pelo menos 3 caracteres'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'sucesso': False,
                'erro': 'Senha deve ter pelo menos 6 caracteres'
            }), 400
        
        if password != password_confirm:
            return jsonify({
                'sucesso': False,
                'erro': 'As senhas não correspondem'
            }), 400
        
        
        if User.query.filter_by(username=username).first():
            return jsonify({
                'sucesso': False,
                'erro': 'Este username já está em uso'
            }), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({
                'sucesso': False,
                'erro': 'Este email já está registrado'
            }), 400
        
        
        confirmation_token = secrets.token_urlsafe(32)
        user = User(
            username=username,
            email=email,
            confirmation_token=confirmation_token
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        
        try:
            send_confirmation_email(email, username, confirmation_token)
        except Exception as e:
            current_app.logger.error(f'Erro ao enviar email de confirmação: {str(e)}')

        # Enviar mensagem automática de agradecimento a partir de conectareal@gmail.com
        try:
            subject_auto = 'Recebemos seu contato - ConectAreal'
            text_auto = 'A Conectareal agradece o seu contato. Em breve, retornaremos com mais informações.'
            sender_addr = current_app.config.get('MAIL_USERNAME') or current_app.config.get('MAIL_DEFAULT_SENDER') or 'conectareal@gmail.com'
            sent = send_email_async(subject_auto, email, text_auto, None, sender=sender_addr)
            if not sent:
                current_app.logger.error('Envio do email automático de agradecimento retornou False')
        except Exception as e:
            current_app.logger.error(f'Erro ao enviar email automático de agradecimento: {str(e)}')
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Cadastro realizado com sucesso! Verifique seu email para confirmar sua conta.'
        }), 201
    
    except Exception as e:
        current_app.logger.error(f'Erro no registro: {str(e)}')
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao registrar. Tente novamente.'
        }), 500


@auth_bp.route('/confirm/<token>', methods=['GET'])
def confirm_email(token):
    try:
        user = User.query.filter_by(confirmation_token=token).first()
        
        if not user:
            return render_template('confirmation_result.html', 
                                 sucesso=False,
                                 mensagem='Link de confirmação inválido ou expirado'), 400
        
        if user.email_confirmed:
            return render_template('confirmation_result.html',
                                 sucesso=True,
                                 mensagem='Este email já foi confirmado'), 200
        
        user.email_confirmed = True
        user.confirmation_token = None
        db.session.commit()
        
        
        try:
            send_welcome_email(user.email, user.username)
        except Exception as e:
            current_app.logger.error(f'Erro ao enviar email de boas-vindas: {str(e)}')
        
        return render_template('confirmation_result.html',
                             sucesso=True,
                             mensagem=f'Parabéns {user.username}! Seu email foi confirmado. Agora você pode fazer login.'), 200
    
    except Exception as e:
        current_app.logger.error(f'Erro na confirmação de email: {str(e)}')
        return render_template('confirmation_result.html',
                             sucesso=False,
                             mensagem='Erro ao confirmar email. Tente novamente.'), 500


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({
        'sucesso': True,
        'mensagem': 'Logout realizado com sucesso'
    }), 200


@auth_bp.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('forgot_password.html')


@auth_bp.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip()
        
        if not email:
            return jsonify({
                'sucesso': False,
                'erro': 'Email é obrigatório'
            }), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            reset_token = secrets.token_urlsafe(32)
            user.confirmation_token = reset_token  # Reutilizando o campo
            db.session.commit()
            
            try:
                send_password_reset_email(user.email, user.username, reset_token)
            except Exception as e:
                current_app.logger.error(f'Erro ao enviar email de reset: {str(e)}')
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Se este email estiver registrado, você receberá um link para redefinir a senha.'
        }), 200
    
    except Exception as e:
        current_app.logger.error(f'Erro ao solicitar reset de senha: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao solicitar reset de senha'
        }), 500


@auth_bp.route('/reset/<token>', methods=['GET'])
def reset_password_page(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    user = User.query.filter_by(confirmation_token=token).first()
    if not user:
        return render_template('error.html',
                             mensagem='Link de reset inválido ou expirado'), 400
    
    return render_template('reset_password.html', token=token)


@auth_bp.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    try:
        data = request.get_json() or {}
        token = (data.get('token') or '').strip()
        password = data.get('password') or ''
        password_confirm = data.get('password_confirm') or ''
        
        if not token or not password:
            return jsonify({
                'sucesso': False,
                'erro': 'Token e senha são obrigatórios'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'sucesso': False,
                'erro': 'Senha deve ter pelo menos 6 caracteres'
            }), 400
        
        if password != password_confirm:
            return jsonify({
                'sucesso': False,
                'erro': 'As senhas não correspondem'
            }), 400
        
        user = User.query.filter_by(confirmation_token=token).first()
        
        if not user:
            return jsonify({
                'sucesso': False,
                'erro': 'Link de reset inválido ou expirado'
            }), 400
        
        user.set_password(password)
        user.confirmation_token = None
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Senha redefinida com sucesso! Faça login com sua nova senha.'
        }), 200
    
    except Exception as e:
        current_app.logger.error(f'Erro ao resetar senha: {str(e)}')
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao redefinir senha'
        }), 500


@auth_bp.route('/user/profile')
@login_required
def profile_page():
    return render_template('profile.html', user=current_user)


@auth_bp.route('/api/user/profile')
@login_required
def api_get_profile():
    return jsonify(current_user.to_dict()), 200


@auth_bp.route('/api/user/update', methods=['POST'])
@login_required
def api_update_profile():
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip()
        
        if not email:
            return jsonify({
                'sucesso': False,
                'erro': 'Email é obrigatório'
            }), 400
        
        if email != current_user.email and User.query.filter_by(email=email).first():
            return jsonify({
                'sucesso': False,
                'erro': 'Este email já está em uso'
            }), 400
        
        current_user.email = email
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Perfil atualizado com sucesso',
            'usuario': current_user.to_dict()
        }), 200
    
    except Exception as e:
        current_app.logger.error(f'Erro ao atualizar perfil: {str(e)}')
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao atualizar perfil'
        }), 500


@auth_bp.route('/api/user/change-password', methods=['POST'])
@login_required
def api_change_password():
    try:
        data = request.get_json() or {}
        old_password = data.get('old_password') or ''
        new_password = data.get('new_password') or ''
        new_password_confirm = data.get('new_password_confirm') or ''
        
        if not old_password or not new_password:
            return jsonify({
                'sucesso': False,
                'erro': 'Todos os campos são obrigatórios'
            }), 400
        
        if not current_user.check_password(old_password):
            return jsonify({
                'sucesso': False,
                'erro': 'Senha atual incorreta'
            }), 401
        
        if len(new_password) < 6:
            return jsonify({
                'sucesso': False,
                'erro': 'Nova senha deve ter no mínimo 6 caracteres'
            }), 400
        
        if new_password != new_password_confirm:
            return jsonify({
                'sucesso': False,
                'erro': 'As senhas não correspondem'
            }), 400
        
        current_user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Senha alterada com sucesso'
        }), 200
    
    except Exception as e:
        current_app.logger.error(f'Erro ao alterar senha: {str(e)}')
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao alterar senha'
        }), 500


if __name__ == '__main__':
    # Bloco mínimo para executar este blueprint isoladamente (útil para deploy na Square Cloud)
    import os
    from flask import Flask
    from config import config
    try:
        from mail import mail
    except Exception:
        mail = None

    app = Flask(__name__)

    # Carrega configuração baseada na variável FLASK_ENV (default: production)
    env = os.environ.get('FLASK_ENV', 'production')
    cfg = config.get(env, config.get('production'))
    app.config.from_object(cfg)

    # Inicializa extensões que o blueprint usa
    try:
        db.init_app(app)
    except Exception:
        pass

    if mail is not None:
        try:
            mail.init_app(app)
        except Exception:
            pass

    # Inicializa login manager definido neste arquivo
    try:
        init_login_manager(app)
    except Exception:
        pass

    app.register_blueprint(auth_bp)

    # Cria tabelas caso seja necessário (somente se SQLAlchemy estiver configurado)
    try:
        with app.app_context():
            db.create_all()
    except Exception:
        pass

    # Executa na interface pública na porta 80 (requer permissão/do ambiente)
    app.run(host='0.0.0.0', port=80)
