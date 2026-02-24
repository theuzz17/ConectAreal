import unittest
import json
from app import app, db
from models import User, Estabelecimento
from datetime import datetime, date


class TestPerfil(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.app = app
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            self.usuario = User(
                username='testuser',
                email='test@example.com',
                is_active=True,
                email_confirmed=True,
                nome_completo='Usuário Teste'
            )
            self.usuario.set_password('senha123')
            
            db.session.add(self.usuario)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, username, password):
        return self.client.post('/api/login', 
            json={'username_or_email': username, 'password': password},
            content_type='application/json'
        )

    def test_acessar_perfil_nao_autenticado(self):
        response = self.client.get('/perfil/')
        self.assertEqual(response.status_code, 302)

    def test_acessar_perfil_autenticado(self):
        self.login('testuser', 'senha123')
        response = self.client.get('/perfil/')
        self.assertEqual(response.status_code, 200)

    def test_obter_perfil_api(self):
        self.login('testuser', 'senha123')
        response = self.client.get('/perfil/api')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['sucesso'])
        self.assertEqual(data['usuario']['username'], 'testuser')

    def test_atualizar_perfil_dados_basicos(self):
        self.login('testuser', 'senha123')
        
        response = self.client.put('/perfil/api/atualizar',
            json={
                'nome_completo': 'Novo Nome',
                'telefone': '(11) 98765-4321',
                'bairro': 'Centro'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['sucesso'])
        self.assertEqual(data['usuario']['nome_completo'], 'Novo Nome')

    def test_atualizar_perfil_nome_longo(self):
        self.login('testuser', 'senha123')
        
        nome_longo = 'a' * 300
        response = self.client.put('/perfil/api/atualizar',
            json={'nome_completo': nome_longo},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_atualizar_perfil_telefone_invalido(self):
        self.login('testuser', 'senha123')
        
        response = self.client.put('/perfil/api/atualizar',
            json={'telefone': 'telefone invalido'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_atualizar_perfil_bio(self):
        self.login('testuser', 'senha123')
        
        response = self.client.put('/perfil/api/atualizar',
            json={'bio': 'Esta é uma bio de teste'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_atualizar_perfil_data_nascimento(self):
        self.login('testuser', 'senha123')
        
        response = self.client.put('/perfil/api/atualizar',
            json={'data_nascimento': '1990-01-15'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_atualizar_perfil_data_invalida(self):
        self.login('testuser', 'senha123')
        
        response = self.client.put('/perfil/api/atualizar',
            json={'data_nascimento': 'data invalida'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_alterar_email_sucesso(self):
        self.login('testuser', 'senha123')
        
        response = self.client.put('/perfil/api/alterar-email',
            json={
                'novo_email': 'novoemail@example.com',
                'senha': 'senha123'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['sucesso'])

    def test_alterar_email_senha_incorreta(self):
        self.login('testuser', 'senha123')
        
        response = self.client.put('/perfil/api/alterar-email',
            json={
                'novo_email': 'novoemail@example.com',
                'senha': 'senha_errada'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_alterar_email_email_invalido(self):
        self.login('testuser', 'senha123')
        
        response = self.client.put('/perfil/api/alterar-email',
            json={
                'novo_email': 'email_invalido',
                'senha': 'senha123'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_alterar_email_duplicado(self):
        with app.app_context():
            outro_usuario = User(
                username='outro',
                email='outro@example.com',
                is_active=True
            )
            outro_usuario.set_password('senha123')
            db.session.add(outro_usuario)
            db.session.commit()
        
        self.login('testuser', 'senha123')
        
        response = self.client.put('/perfil/api/alterar-email',
            json={
                'novo_email': 'outro@example.com',
                'senha': 'senha123'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_alterar_senha_sucesso(self):
        self.login('testuser', 'senha123')
        
        response = self.client.put('/perfil/api/alterar-senha',
            json={
                'senha_atual': 'senha123',
                'nova_senha': 'nova_senha123',
                'confirmar_senha': 'nova_senha123'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_alterar_senha_atual_incorreta(self):
        self.login('testuser', 'senha123')
        
        response = self.client.put('/perfil/api/alterar-senha',
            json={
                'senha_atual': 'senha_errada',
                'nova_senha': 'nova_senha123',
                'confirmar_senha': 'nova_senha123'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_alterar_senha_nao_coincidem(self):
        self.login('testuser', 'senha123')
        
        response = self.client.put('/perfil/api/alterar-senha',
            json={
                'senha_atual': 'senha123',
                'nova_senha': 'nova_senha123',
                'confirmar_senha': 'outra_senha'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_alterar_senha_muito_curta(self):
        self.login('testuser', 'senha123')
        
        response = self.client.put('/perfil/api/alterar-senha',
            json={
                'senha_atual': 'senha123',
                'nova_senha': '123',
                'confirmar_senha': '123'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_alterar_senha_igual_anterior(self):
        self.login('testuser', 'senha123')
        
        response = self.client.put('/perfil/api/alterar-senha',
            json={
                'senha_atual': 'senha123',
                'nova_senha': 'senha123',
                'confirmar_senha': 'senha123'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_excluir_conta_senha_incorreta(self):
        self.login('testuser', 'senha123')
        
        response = self.client.delete('/perfil/api/excluir-conta',
            json={'senha': 'senha_errada'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_excluir_conta_sucesso(self):
        self.login('testuser', 'senha123')
        
        response = self.client.delete('/perfil/api/excluir-conta',
            json={'senha': 'senha123'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        with app.app_context():
            usuario = User.query.filter_by(username='testuser').first()
            self.assertIsNone(usuario)

    def test_historico_login(self):
        self.login('testuser', 'senha123')
        
        response = self.client.get('/perfil/api/historico-login')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['sucesso'])

    def test_atividades(self):
        self.login('testuser', 'senha123')
        
        response = self.client.get('/perfil/api/atividades')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['sucesso'])
        self.assertIn('atividades', data)


if __name__ == '__main__':
    unittest.main()
