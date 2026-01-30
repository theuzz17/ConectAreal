import unittest
import json
from app import app, db
from models import User, Estabelecimento, Avaliacao
from datetime import datetime


class TestEstabelecimentos(unittest.TestCase):

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
                email_confirmed=True
            )
            self.usuario.set_password('senha123')
            
            self.admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True,
                is_active=True,
                email_confirmed=True
            )
            self.admin.set_password('senha123')
            
            db.session.add(self.usuario)
            db.session.add(self.admin)
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

    def test_listar_estabelecimentos_vazio(self):
        response = self.client.get('/estabelecimentos/api/listar')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['sucesso'])
        self.assertEqual(len(data['estabelecimentos']), 0)

    def test_criar_estabelecimento_nao_autenticado(self):
        response = self.client.post('/estabelecimentos/api/criar',
            json={
                'nome': 'Teste',
                'categoria': 'comercios',
                'descricao': 'Descrição teste de estabelecimento'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_criar_estabelecimento_sucesso(self):
        self.login('testuser', 'senha123')
        
        response = self.client.post('/estabelecimentos/api/criar',
            json={
                'nome': 'Padaria Teste',
                'categoria': 'comercios',
                'descricao': 'Padaria com pães frescos e bolos caseiros',
                'telefone': '(11) 98765-4321',
                'email': 'padaria@example.com',
                'endereco': 'Rua Principal, 123',
                'localizacao': 'Centro'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertTrue(data['sucesso'])
        self.assertEqual(data['estabelecimento']['nome'], 'Padaria Teste')

    def test_criar_estabelecimento_campos_obrigatorios(self):
        self.login('testuser', 'senha123')
        
        response = self.client.post('/estabelecimentos/api/criar',
            json={
                'nome': 'Teste',
                'categoria': 'comercios'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['sucesso'])

    def test_criar_estabelecimento_nome_invalido(self):
        self.login('testuser', 'senha123')
        
        response = self.client.post('/estabelecimentos/api/criar',
            json={
                'nome': 'AB',
                'categoria': 'comercios',
                'descricao': 'Descrição com muitos caracteres para passar'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_criar_estabelecimento_categoria_invalida(self):
        self.login('testuser', 'senha123')
        
        response = self.client.post('/estabelecimentos/api/criar',
            json={
                'nome': 'Teste Estabelecimento',
                'categoria': 'categoriaInvalida',
                'descricao': 'Descrição com muitos caracteres para passar'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_editar_estabelecimento_nao_proprietario(self):
        with app.app_context():
            estab = Estabelecimento(
                usuario_id=self.admin.id,
                nome='Teste',
                categoria='comercios',
                descricao='Descrição de teste'
            )
            db.session.add(estab)
            db.session.commit()
            estab_id = estab.id
        
        self.login('testuser', 'senha123')
        
        response = self.client.put(f'/estabelecimentos/api/editar/{estab_id}',
            json={'nome': 'Novo Nome'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

    def test_editar_estabelecimento_proprietario(self):
        with app.app_context():
            estab = Estabelecimento(
                usuario_id=self.usuario.id,
                nome='Teste Original',
                categoria='comercios',
                descricao='Descrição de teste'
            )
            db.session.add(estab)
            db.session.commit()
            estab_id = estab.id
        
        self.login('testuser', 'senha123')
        
        response = self.client.put(f'/estabelecimentos/api/editar/{estab_id}',
            json={'nome': 'Novo Nome'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['sucesso'])
        self.assertEqual(data['estabelecimento']['nome'], 'Novo Nome')

    def test_deletar_estabelecimento_nao_proprietario(self):
        with app.app_context():
            estab = Estabelecimento(
                usuario_id=self.admin.id,
                nome='Teste',
                categoria='comercios',
                descricao='Descrição de teste'
            )
            db.session.add(estab)
            db.session.commit()
            estab_id = estab.id
        
        self.login('testuser', 'senha123')
        
        response = self.client.delete(f'/estabelecimentos/api/deletar/{estab_id}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

    def test_deletar_estabelecimento_proprietario(self):
        with app.app_context():
            estab = Estabelecimento(
                usuario_id=self.usuario.id,
                nome='Teste',
                categoria='comercios',
                descricao='Descrição de teste'
            )
            db.session.add(estab)
            db.session.commit()
            estab_id = estab.id
        
        self.login('testuser', 'senha123')
        
        response = self.client.delete(f'/estabelecimentos/api/deletar/{estab_id}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_avaliar_estabelecimento_nao_autenticado(self):
        with app.app_context():
            estab = Estabelecimento(
                usuario_id=self.usuario.id,
                nome='Teste',
                categoria='comercios',
                descricao='Descrição de teste'
            )
            db.session.add(estab)
            db.session.commit()
            estab_id = estab.id
        
        response = self.client.post(f'/estabelecimentos/api/avaliar/{estab_id}',
            json={'nota': 5, 'comentario': 'Muito bom!'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_avaliar_estabelecimento_nota_invalida(self):
        with app.app_context():
            estab = Estabelecimento(
                usuario_id=self.usuario.id,
                nome='Teste',
                categoria='comercios',
                descricao='Descrição de teste'
            )
            db.session.add(estab)
            db.session.commit()
            estab_id = estab.id
        
        self.login('testuser', 'senha123')
        
        response = self.client.post(f'/estabelecimentos/api/avaliar/{estab_id}',
            json={'nota': 10, 'comentario': 'Muito bom!'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_avaliar_estabelecimento_sucesso(self):
        with app.app_context():
            estab = Estabelecimento(
                usuario_id=self.usuario.id,
                nome='Teste',
                categoria='comercios',
                descricao='Descrição de teste'
            )
            db.session.add(estab)
            db.session.commit()
            estab_id = estab.id
        
        self.login('testuser', 'senha123')
        
        response = self.client.post(f'/estabelecimentos/api/avaliar/{estab_id}',
            json={'nota': 5, 'comentario': 'Muito bom!'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['sucesso'])
        self.assertEqual(data['nota_media'], 5.0)

    def test_listar_meus_estabelecimentos(self):
        with app.app_context():
            for i in range(3):
                estab = Estabelecimento(
                    usuario_id=self.usuario.id,
                    nome=f'Teste {i}',
                    categoria='comercios',
                    descricao='Descrição de teste'
                )
                db.session.add(estab)
            db.session.commit()
        
        self.login('testuser', 'senha123')
        
        response = self.client.get('/estabelecimentos/api/meus')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['sucesso'])
        self.assertEqual(len(data['estabelecimentos']), 3)


if __name__ == '__main__':
    unittest.main()
