import uuid
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.services.auth_service import AuthService
from src.main import app
from src.database import Base, get_db
from src.config import settings
from src.auth.password import hash_password
from src.models.user import User
from src.models.product import Product
from fastapi import status
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# ==================== CONFIGURAÇÃO DO BANCO DE TESTES ====================
TEST_DB_NAME = "test_wisesales"
TEST_DB_USER = settings.db_user
TEST_DB_PASSWORD = settings.db_password
TEST_DB_HOST = settings.db_host
TEST_DB_PORT = settings.db_port

def create_test_database():
    """Cria banco de dados de teste"""
    conn = psycopg2.connect(
        host=TEST_DB_HOST,
        port=TEST_DB_PORT,
        user=TEST_DB_USER,
        password=TEST_DB_PASSWORD,
        database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Dropar banco se existir e criar novo
    cur.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    cur.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    cur.close()
    conn.close()

# URL do banco de testes
TEST_DATABASE_URL = f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

# Engine para testes
test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# ==================== FIXTURES DE BANCO ====================

@pytest.fixture(scope="session")
def db_engine():
    """Cria engine do banco de testes (uma vez por sessão)"""
    create_test_database()
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator:
    """Cria sessão do banco para cada teste com transação isolada"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

# ==================== FIXTURES DE CLIENTE ====================

@pytest.fixture(scope="function")
def client(db_session):
    """Cria cliente de teste com banco isolado"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

# ==================== FIXTURES DE USUÁRIOS ====================

@pytest.fixture(scope="function")
def test_user(client):
    """Cria um usuário comum para testes diretamente no banco"""
    from src.models.user import User


    unique_id = uuid.uuid4().hex[:8]
    email = f"user_test{unique_id}@test.com"
    

    # Registrar usuário
    client.post("/auth/register", json={
        "name": "Login Teste",
        "email": email,
        "password": "senha123",
    })

    return {
        "email": email,

    }


@pytest.fixture(scope="function")
def user_token(client, test_user):
    """Token para usuário comum via API"""
    response = client.post("/auth/login", json={
        "email": test_user['email'],
        "password": "senha123"
    })
    assert response.status_code == status.HTTP_200_OK
    return response.json()["access_token"]

# backend/tests/conftest.py

@pytest.fixture(scope="function")
def test_admin_via_service(db_session):
    """Cria um admin usando o AuthService (mais confiável)"""
    from src.services.auth_service import AuthService
    from src.models.user import User
    import uuid
    
    auth_service = AuthService()
    
    # Gerar email único
    unique_id = uuid.uuid4().hex[:8]
    email = f"admin_{unique_id}@test.com"
    password = "admin123"
    name = "Admin Teste"
    
    
    # Registrar usuário
    user_data = auth_service.register_user(
        email=email,
        password=password,
        name=name,
        is_admin=True
    )
    
    # Tornar admin diretamente no banco
    user = db_session.query(User).filter(User.id == user_data["id"]).first()
    
    
    # Retornar dados completos
    return {
        "id": user.id,
        "email": email,
        "password": password,
        "name": name,
        "is_admin": True
    }

@pytest.fixture(scope="function")
def admin_token(client, test_admin_via_service):
    """Token para admin via API"""
    
    response = client.post("/auth/login", json={
        "email": test_admin_via_service["email"],
        "password": test_admin_via_service["password"]
    })
    

    
    assert response.status_code == status.HTTP_200_OK
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def auth_client(client, user_token):
    """Cliente autenticado como usuário comum"""
    client.headers.update({"Authorization": f"Bearer {user_token}"})
    return client

@pytest.fixture(scope="function")
def admin_client(client, admin_token):
    """Cliente autenticado como admin"""
    client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return client

# ==================== FIXTURES DE PRODUTOS ====================

@pytest.fixture(scope="function")
def test_product(db_session):
    """Cria um produto de teste diretamente no banco"""
    from src.models.product import Product
    
    product = Product(
        name="Produto Teste",
        description="Descrição do produto teste",
        price=99.90,
        category="teste",
        stock=10,
        image_url="https://exemplo.com/produto.jpg"
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    return product


@pytest.fixture(scope="function")
def auth_client_with_multiple_products(auth_client, test_products_via_api):
    """Cliente autenticado com múltiplos produtos disponíveis"""
    auth_client.test_products = {p["name"]: p for p in test_products_via_api}
    return auth_client

# ==================== FIXTURES PARA CARRINHO ====================

@pytest.fixture(scope="function")
def cart_with_items(auth_client_with_products, auth_client):
    """Cria um carrinho com itens para testes"""
    product = auth_client_with_products
    
    response = auth_client.post(
        "/cart/items",
        json={"product_id": product.id, "quantity": 2}
    )
    assert response.status_code == status.HTTP_200_OK
    
    return auth_client_with_products



@pytest.fixture
def auth_client_with_products(test_products_via_api):
    """Cliente autenticado com produtos disponíveis via dicionário"""
    # Converter lista de produtos para dicionário nome -> produto
    products_dict = {p["name"]: p for p in test_products_via_api}
    return products_dict


@pytest.fixture(scope="function")
def test_products_via_api(admin_client):
    """Cria produtos de teste via API e retorna lista"""
    products_data = [
        {
            "name": "Notebook Teste",
            "description": "Notebook para testes",
            "price": 4999.99,
            "category": "eletrônicos",
            "stock": 10,
            "image_url": "https://exemplo.com/notebook.jpg"
        },
        {
            "name": "Mouse Teste",
            "description": "Mouse para testes",
            "price": 89.90,
            "category": "eletrônicos",
            "stock": 50,
            "image_url": "https://exemplo.com/mouse.jpg"
        },
        {
            "name": "Produto Esgotado",
            "description": "Produto sem estoque",
            "price": 199.90,
            "category": "teste",
            "stock": 0,
            "image_url": "https://exemplo.com/produto.jpg"
        },
    ]
    
    created_products = []
    for product_data in products_data:
        response = admin_client.post("/products/", json=product_data)
        # Pode ser 201 (criado) ou 409 (já existe)
        if response.status_code == status.HTTP_201_CREATED:
            created_products.append(response.json())
        elif response.status_code == status.HTTP_409_CONFLICT:
            # Se já existe, buscar o produto
            products = admin_client.get("/products/").json()
            for p in products:
                if p["name"] == product_data["name"]:
                    created_products.append(p)
                    break
    
    return created_products