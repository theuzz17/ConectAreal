from app import app
from models import ContactMessage

with app.app_context():
    msgs = ContactMessage.query.order_by(ContactMessage.criado_em.desc()).limit(50).all()
    if not msgs:
        print('Nenhuma mensagem encontrada')
    for m in msgs:
        print(f'ID: {m.id} | Nome: {m.nome} | Email: {m.email} | Lido: {m.lido} | Respondida: {m.respondida} | Resposta: {bool(m.resposta)} | Criado: {m.criado_em}')
