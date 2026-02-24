#!/usr/bin/env python
import os
import sys
from app import app, db
from models import User

def init_db():
    with app.app_context():
        db.create_all()
        print("✓ Banco de dados criado com sucesso!")


def create_admin():
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()

        if admin:
            print("⚠ Usuário admin já existe!")
            return

        admin = User(
            username='admin',
            email='admin@conectareal.com',
            is_admin=True,
            email_confirmed=True
        )
        admin.set_password('123456')

        db.session.add(admin)
        db.session.commit()

        print("✓ Usuário admin criado com sucesso!")
        print(f"  Usuário: admin")
        print(f"  Senha: 123456")
        print(f"  Email: admin@conectareal.com")
        print("\n⚠ IMPORTANTE: Altere a senha padrão em produção!")


if __name__ == '__main__':
    print("Inicializando ConectAreal...")
    init_db()
    create_admin()
    print("\n✓ Inicialização completa!")
