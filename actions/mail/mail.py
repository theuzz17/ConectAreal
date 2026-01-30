from flask_mail import Mail, Message
from flask import current_app, render_template
import logging

mail = Mail()
logger = logging.getLogger(__name__)


def send_email_async(subject, recipients, text_body=None, html_body=None, attachments=None, sender=None, reply_to=None):
    """Enviar email (sincronamente por enquanto)."""
    try:
        recipients_list = recipients if isinstance(recipients, list) else [recipients]
        # Se não houver html_body, renderiza um template de e-mail padrão com estilo verde
        if not html_body:
            try:
                html_body = render_template('email/simple_message.html', title=subject, message=text_body)
            except Exception:
                # fallback para um HTML simples se template não existir
                html_body = f"<html><body><p>{text_body or ''}</p></body></html>"

        msg = Message(
            subject=subject,
            recipients=recipients_list,
            body=text_body,
            html=html_body,
            sender=sender or current_app.config.get('MAIL_DEFAULT_SENDER'),
            reply_to=reply_to,
        )

        if attachments:
            for att in attachments:
                msg.attach(att['filename'], att.get('content_type', 'application/octet-stream'), att['data'])

        mail.send(msg)
        logger.info(f"Email enviado com sucesso para {recipients_list}")
        return True
    except Exception as e:
        logger.exception(f"Erro ao enviar email para {recipients}: {e}")
        return False


def send_confirmation_email(user_email, username, confirmation_token):
    subject = 'Confirmação de cadastro - ConectAreal'
    app_url = current_app.config.get('APP_URL', 'http://localhost:5000')
    html_body = f"Olá {username},\nConfirme seu email: {app_url}/confirm/{confirmation_token}"
    text_body = f"Bem-vindo {username}! Confirme em: {app_url}/confirm/{confirmation_token}"
    return send_email_async(subject, user_email, text_body, html_body)


def send_password_reset_email(user_email, username, reset_token):
    subject = 'Redefinir sua senha - ConectAreal'
    app_url = current_app.config.get('APP_URL', 'http://localhost:5000')
    html_body = f"Redefina a senha: {app_url}/reset/{reset_token}"
    text_body = f"Redefinir senha: {app_url}/reset/{reset_token}"
    return send_email_async(subject, user_email, text_body, html_body)


def send_contact_notification(contact_data):
    admin_email = current_app.config.get('ADMIN_EMAIL')
    if not admin_email:
        logger.warning('Email de admin não configurado para notificações de contato')
        return False
    subject = f"Nova mensagem de contato: {contact_data.get('assunto')}"
    text_body = f"Nova mensagem de {contact_data.get('nome')}: {contact_data.get('mensagem')}"
    return send_email_async(subject, admin_email, text_body)


def send_welcome_email(user_email, username):
    subject = 'Bem-vindo ao ConectAreal!'
    app_url = current_app.config.get('APP_URL', 'http://localhost:5000')
    text_body = f"Bem-vindo {username}! Acesse: {app_url}"
    return send_email_async(subject, user_email, text_body)


def enviar_resposta_mensagem(destinatario_email, nome_destinatario, assunto_original, resposta_texto, admin_nome):
    assunto = f"Resposta: {assunto_original}"
    html_body = resposta_texto
    text_body = f"{resposta_texto}\nEnviado por: {admin_nome}"
    sender_address = current_app.config.get('REPLY_SENDER_EMAIL', 'arealconect@gmail.com')
    return send_email_async(assunto, destinatario_email, text_body, html_body, sender=sender_address, reply_to=sender_address)
