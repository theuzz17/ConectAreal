from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nome_completo = db.Column(db.String(255), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    endereco = db.Column(db.String(255), nullable=True)
    bairro = db.Column(db.String(100), nullable=True)
    foto_url = db.Column(db.String(500), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    email_confirmed = db.Column(db.Boolean, default=False)
    confirmation_token = db.Column(db.String(255), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nome_completo': self.nome_completo,
            'telefone': self.telefone,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'bio': self.bio,
            'endereco': self.endereco,
            'bairro': self.bairro,
            'foto_url': self.foto_url,
            'is_admin': self.is_admin,
            'email_confirmed': self.email_confirmed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    assunto = db.Column(db.String(255), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    lido = db.Column(db.Boolean, default=False)
    respondida = db.Column(db.Boolean, default=False)
    resposta = db.Column(db.Text, nullable=True)
    respondida_em = db.Column(db.DateTime, nullable=True)
    respondido_por = db.Column(db.String(255), nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContactMessage {self.assunto}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'assunto': self.assunto,
            'mensagem': self.mensagem,
            'lido': self.lido,
            'respondida': self.respondida,
            'resposta': self.resposta,
            'respondida_em': self.respondida_em.isoformat() if self.respondida_em else None,
            'respondido_por': self.respondido_por,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }


class Newsletter(db.Model):
    __tablename__ = 'newsletter'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    confirmado = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Newsletter {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'confirmado': self.confirmado,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }


class Estabelecimento(db.Model):
    __tablename__ = 'estabelecimentos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    nome = db.Column(db.String(255), nullable=False, index=True)
    categoria = db.Column(db.String(100), nullable=False, index=True)
    descricao = db.Column(db.Text, nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    endereco = db.Column(db.String(255), nullable=True)
    localizacao = db.Column(db.String(255), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    horario_funcionamento = db.Column(db.String(500), nullable=True)
    imagem_url = db.Column(db.String(500), nullable=True)
    verificado = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    usuario = db.relationship('User', backref=db.backref('estabelecimentos', lazy=True))
    
    def __repr__(self):
        return f'<Estabelecimento {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'nome': self.nome,
            'categoria': self.categoria,
            'descricao': self.descricao,
            'telefone': self.telefone,
            'email': self.email,
            'endereco': self.endereco,
            'localizacao': self.localizacao,
            'website': self.website,
            'horario_funcionamento': self.horario_funcionamento,
            'imagem_url': self.imagem_url,
            'verificado': self.verificado,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }


class Avaliacao(db.Model):
    __tablename__ = 'avaliacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    estabelecimento_id = db.Column(db.Integer, db.ForeignKey('estabelecimentos.id'), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    nota = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    estabelecimento = db.relationship('Estabelecimento', backref=db.backref('avaliacoes', lazy=True, cascade='all, delete-orphan'))
    usuario = db.relationship('User', backref=db.backref('avaliacoes', lazy=True))
    
    def __repr__(self):
        return f'<Avaliacao {self.estabelecimento_id} - {self.nota}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'estabelecimento_id': self.estabelecimento_id,
            'usuario_id': self.usuario_id,
            'nota': self.nota,
            'comentario': self.comentario,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }
