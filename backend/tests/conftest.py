import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database import Base, get_db
from src.config import settings
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configuração do banco de testes
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

@pytest.fixture(scope="session")
def db_engine():
    """Cria engine do banco de testes"""
    create_test_database()
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator:
    """Cria sessão do banco para cada teste"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

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