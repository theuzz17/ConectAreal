import unittest
import json
from datetime import datetime
from app import app, db
from models import User, ContactMessage, Newsletter, Estabelecimento, Avaliacao

class TestAdminPainel(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.app = app
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            self.admin_user = User(
                username='admin',
                email='admin@test.com',
                is_admin=True,
                is_active=True,
                email_confirmed=True
            )
            self.admin_user.set_password('senha123')
            
            self.regular_user = User(
                username='usuario',
                email='usuario@test.com',
                is_admin=False,
                is_active=True,
                email_confirmed=True
            )
            self.regular_user.set_password('senha123')
            
            db.session.add(self.admin_user)
            db.session.add(self.regular_user)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login_admin(self):
        self.client.post('/auth/login', data={
            'username': 'admin',
            'password': 'senha123'
        }, follow_redirects=True)

    def login_usuario(self):
        self.client.post('/auth/login', data={
            'username': 'usuario',
            'password': 'senha123'
        }, follow_redirects=True)

    def test_acesso_painel_nao_autenticado(self):
        response = self.client.get('/admin/', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_acesso_painel_usuario_normal(self):
        self.login_usuario()
        response = self.client.get('/admin/', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_acesso_painel_admin(self):
        self.login_admin()
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Painel Administrativo', response.data)

    def test_obter_dashboard(self):
        self.login_admin()
        response = self.client.get('/admin/api/dashboard')
        self.assertEqual(response.status_code, 200)
        
        dados = json.loads(response.data)
        self.assertIn('usuarios', dados)
        self.assertIn('estabelecimentos', dados)
        self.assertIn('avaliacoes', dados)
        self.assertIn('mensagens', dados)

    def test_listar_usuarios(self):
        self.login_admin()
        response = self.client.get('/admin/api/usuarios')
        self.assertEqual(response.status_code, 200)
        
        dados = json.loads(response.data)
        self.assertEqual(len(dados['usuarios']), 2)

    def test_listar_usuarios_filtro_admins(self):
        self.login_admin()
        response = self.client.get('/admin/api/usuarios?filtro=admins')
        self.assertEqual(response.status_code, 200)
        
        dados = json.loads(response.data)
        self.assertEqual(len(dados['usuarios']), 1)
        self.assertEqual(dados['usuarios'][0]['username'], 'admin')

    def test_listar_usuarios_buscar(self):
        self.login_admin()
        response = self.client.get('/admin/api/usuarios?buscar=usuario')
        self.assertEqual(response.status_code, 200)
        
        dados = json.loads(response.data)
        self.assertEqual(len(dados['usuarios']), 1)
        self.assertEqual(dados['usuarios'][0]['username'], 'usuario')

    def test_toggle_admin_usuario(self):
        self.login_admin()
        
        with app.app_context():
            usuario = User.query.filter_by(username='usuario').first()
            self.assertFalse(usuario.is_admin)
        
        response = self.client.post(f'/admin/api/usuarios/{self.regular_user.id}/toggle-admin')
        self.assertEqual(response.status_code, 200)
        
        dados = json.loads(response.data)
        self.assertTrue(dados['is_admin'])

    def test_toggle_admin_propria_conta(self):
        self.login_admin()
        response = self.client.post(f'/admin/api/usuarios/{self.admin_user.id}/toggle-admin')
        self.assertEqual(response.status_code, 400)

    def test_toggle_ativo_usuario(self):
        self.login_admin()
        response = self.client.post(f'/admin/api/usuarios/{self.regular_user.id}/toggle-ativo')
        self.assertEqual(response.status_code, 200)
        
        dados = json.loads(response.data)
        self.assertFalse(dados['is_active'])

    def test_deletar_usuario(self):
        self.login_admin()
        response = self.client.delete(f'/admin/api/usuarios/{self.regular_user.id}')
        self.assertEqual(response.status_code, 200)
        
        with app.app_context():
            usuario = User.query.filter_by(username='usuario').first()
            self.assertIsNone(usuario)

    def test_deletar_propria_conta(self):
        self.login_admin()
        response = self.client.delete(f'/admin/api/usuarios/{self.admin_user.id}')
        self.assertEqual(response.status_code, 400)

    def test_listar_estabelecimentos(self):
        self.login_admin()
        
        with app.app_context():
            estab = Estabelecimento(
                usuario_id=self.regular_user.id,
                nome='Padaria XYZ',
                categoria='comercios',
                descricao='Padaria artesanal'
            )
            db.session.add(estab)
            db.session.commit()
        
        response = self.client.get('/admin/api/estabelecimentos')
        self.assertEqual(response.status_code, 200)
        
        dados = json.loads(response.data)
        self.assertEqual(len(dados['estabelecimentos']), 1)

    def test_toggle_verificado_estabelecimento(self):
        self.login_admin()
        
        with app.app_context():
            estab = Estabelecimento(
                usuario_id=self.regular_user.id,
                nome='Padaria XYZ',
                categoria='comercios',
                descricao='Padaria artesanal',
                verificado=False
            )
            db.session.add(estab)
            db.session.commit()
            estab_id = estab.id
        
        response = self.client.post(f'/admin/api/estabelecimentos/{estab_id}/toggle-verificado')
        self.assertEqual(response.status_code, 200)
        
        dados = json.loads(response.data)
        self.assertTrue(dados['verificado'])

    def test_toggle_ativo_estabelecimento(self):
        self.login_admin()
        
        with app.app_context():
            estab = Estabelecimento(
                usuario_id=self.regular_user.id,
                nome='Padaria XYZ',
                categoria='comercios',
                descricao='Padaria artesanal',
                ativo=True
            )
            db.session.add(estab)
            db.session.commit()
            estab_id = estab.id
        
        response = self.client.post(f'/admin/api/estabelecimentos/{estab_id}/toggle-ativo')
        self.assertEqual(response.status_code, 200)
        
        dados = json.loads(response.data)
        self.assertFalse(dados['ativo'])

    def test_deletar_estabelecimento(self):
        self.login_admin()
        
        with app.app_context():
            estab = Estabelecimento(
                usuario_id=self.regular_user.id,
                nome='Padaria XYZ',
                categoria='comercios',
                descricao='Padaria artesanal'
            )
            db.session.add(estab)
            db.session.commit()
            estab_id = estab.id
        
        response = self.client.delete(f'/admin/api/estabelecimentos/{estab_id}/deletar')
        self.assertEqual(response.status_code, 200)
        
        with app.app_context():
            estab = Estabelecimento.query.get(estab_id)
            self.assertIsNone(estab)

    def test_listar_mensagens(self):
        self.login_admin()
        
        with app.app_context():
            msg = ContactMessage(
                nome='João',
                email='joao@test.com',
                assunto='Dúvida',
                mensagem='Qual é o horário?',
                lido=False
            )
            db.session.add(msg)
            db.session.commit()
        
        response = self.client.get('/admin/api/mensagens')
        self.assertEqual(response.status_code, 200)
        
        dados = json.loads(response.data)
        self.assertEqual(len(dados['mensagens']), 1)

    def test_marcar_mensagem_lida(self):
        self.login_admin()
        
        with app.app_context():
            msg = ContactMessage(
                nome='João',
                email='joao@test.com',
                assunto='Dúvida',
                mensagem='Qual é o horário?',
                lido=False
            )
            db.session.add(msg)
            db.session.commit()
            msg_id = msg.id
        
        response = self.client.post(f'/admin/api/mensagens/{msg_id}/marcar-lida')
        self.assertEqual(response.status_code, 200)
        
        with app.app_context():
            msg = ContactMessage.query.get(msg_id)
            self.assertTrue(msg.lido)

    def test_deletar_mensagem(self):
        self.login_admin()
        
        with app.app_context():
            msg = ContactMessage(
                nome='João',
                email='joao@test.com',
                assunto='Dúvida',
                mensagem='Qual é o horário?'
            )
            db.session.add(msg)
            db.session.commit()
            msg_id = msg.id
        
        response = self.client.delete(f'/admin/api/mensagens/{msg_id}/deletar')
        self.assertEqual(response.status_code, 200)
        
        with app.app_context():
            msg = ContactMessage.query.get(msg_id)
            self.assertIsNone(msg)

    def test_marcar_todas_lidas(self):
        self.login_admin()
        
        with app.app_context():
            msg1 = ContactMessage(
                nome='João',
                email='joao@test.com',
                assunto='Dúvida 1',
                mensagem='Qual é o horário?',
                lido=False
            )
            msg2 = ContactMessage(
                nome='Maria',
                email='maria@test.com',
                assunto='Dúvida 2',
                mensagem='Como funciona?',
                lido=False
            )
            db.session.add(msg1)
            db.session.add(msg2)
            db.session.commit()
        
        response = self.client.post('/admin/api/mensagens/marcar-todas-lidas')
        self.assertEqual(response.status_code, 200)
        
        with app.app_context():
            nao_lidas = ContactMessage.query.filter_by(lido=False).count()
            self.assertEqual(nao_lidas, 0)

    def test_listar_avaliacoes(self):
        self.login_admin()
        
        with app.app_context():
            estab = Estabelecimento(
                usuario_id=self.regular_user.id,
                nome='Padaria XYZ',
                categoria='comercios',
                descricao='Padaria artesanal'
            )
            db.session.add(estab)
            db.session.commit()
            
            aval = Avaliacao(
                estabelecimento_id=estab.id,
                usuario_id=self.regular_user.id,
                nota=5,
                comentario='Excelente'
            )
            db.session.add(aval)
            db.session.commit()
        
        response = self.client.get('/admin/api/avaliacoes')
        self.assertEqual(response.status_code, 200)
        
        dados = json.loads(response.data)
        self.assertEqual(len(dados['avaliacoes']), 1)

    def test_deletar_avaliacao(self):
        self.login_admin()
        
        with app.app_context():
            estab = Estabelecimento(
                usuario_id=self.regular_user.id,
                nome='Padaria XYZ',
                categoria='comercios',
                descricao='Padaria artesanal'
            )
            db.session.add(estab)
            db.session.commit()
            
            aval = Avaliacao(
                estabelecimento_id=estab.id,
                usuario_id=self.regular_user.id,
                nota=5,
                comentario='Excelente'
            )
            db.session.add(aval)
            db.session.commit()
            aval_id = aval.id
        
        response = self.client.delete(f'/admin/api/avaliacoes/{aval_id}/deletar')
        self.assertEqual(response.status_code, 200)
        
        with app.app_context():
            aval = Avaliacao.query.get(aval_id)
            self.assertIsNone(aval)

    def test_listar_newsletter(self):
        self.login_admin()
        
        with app.app_context():
            news = Newsletter(
                email='teste@test.com',
                confirmado=True
            )
            db.session.add(news)
            db.session.commit()
        
        response = self.client.get('/admin/api/newsletter')
        self.assertEqual(response.status_code, 200)
        
        dados = json.loads(response.data)
        self.assertEqual(len(dados['newsletter']), 1)

    def test_deletar_newsletter(self):
        self.login_admin()
        
        with app.app_context():
            news = Newsletter(
                email='teste@test.com',
                confirmado=True
            )
            db.session.add(news)
            db.session.commit()
            news_id = news.id
        
        response = self.client.delete(f'/admin/api/newsletter/{news_id}/deletar')
        self.assertEqual(response.status_code, 200)
        
        with app.app_context():
            news = Newsletter.query.get(news_id)
            self.assertIsNone(news)

    def test_filtro_mensagens_nao_lidas(self):
        self.login_admin()
        
        with app.app_context():
            msg1 = ContactMessage(
                nome='João',
                email='joao@test.com',
                assunto='Dúvida',
                mensagem='Qual é o horário?',
                lido=False
            )
            msg2 = ContactMessage(
                nome='Maria',
                email='maria@test.com',
                assunto='Info',
                mensagem='Como funciona?',
                lido=True
            )
            db.session.add(msg1)
            db.session.add(msg2)
            db.session.commit()
        
        response = self.client.get('/admin/api/mensagens?filtro=nao_lidas')
        self.assertEqual(response.status_code, 200)
        
        dados = json.loads(response.data)
        self.assertEqual(len(dados['mensagens']), 1)

    def test_relatorio_usuarios(self):
        self.login_admin()
        response = self.client.get('/admin/api/relatorios/usuarios')
        self.assertEqual(response.status_code, 200)
        
        dados = json.loads(response.data)
        self.assertIn('usuarios_por_dia', dados)

    def test_relatorio_estabelecimentos(self):
        self.login_admin()
        response = self.client.get('/admin/api/relatorios/estabelecimentos')
        self.assertEqual(response.status_code, 200)
        
        dados = json.loads(response.data)
        self.assertIn('estabelecimentos_por_dia', dados)

if __name__ == '__main__':
    unittest.main()
