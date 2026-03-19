import pytest
from fastapi import status
import uuid

def test_register_user(client):
    """Testa registro de usuário com email único"""
    # Gera um email único usando UUID
    unique_id = uuid.uuid4().hex[:8]
    email = f"teste_{unique_id}@email.com"
    
    response = client.post("/auth/register", json={
        "name": "Usuário Teste",
        "email": email,
        "password": "senha123",
        "confirm_password": "senha123"  # 👈 NÃO ESQUEÇA!
    })
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == email
    assert data["name"] == "Usuário Teste"
    assert "id" in data

def test_register_duplicate_email(client):
    """Testa registro com email duplicado"""
    # Primeiro registro
    client.post("/auth/register", json={
        "name": "Usuário 1",
        "email": "duplicado@email.com",
        "password": "senha123",
    })
    
    # Segundo registro com mesmo email
    response = client.post("/auth/register", json={
        "name": "Usuário 2",
        "email": "duplicado@email.com",
        "password": "senha456",
    })
    
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "já cadastrado" in response.json()["detail"].lower()

def test_login_success(client):
    """Testa login com sucesso"""
    # Registrar usuário
    client.post("/auth/register", json={
        "name": "Login Teste",
        "email": "login@email.com",
        "password": "senha123",
    })
    
    # Fazer login
    response = client.post("/auth/login", json={
        "email": "login@email.com",
        "password": "senha123"
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    token = data["access_token"]
    client.headers.update({
        "Authorization": f"Bearer {token}"
    })
    
    # Agora o client tem o token automaticamente em todas as requisições
    user_data = client.get("/users/me").json()
    print(user_data)
    
    assert user_data["email"] == "login@email.com"

    
    assert user_data["email"] == "login@email.com"

# def test_login_wrong_password(client):
#     """Testa login com senha errada"""
#     # Registrar usuário
#     client.post("/auth/register", json={
#         "name": "Login Teste",
#         "email": "login2@email.com",
#         "password": "senha123",
#     })
    
#     # Tentar login com senha errada
#     response = client.post("/auth/login", json={
#         "email": "login2@email.com",
#         "password": "senha_errada"
#     })
    
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED

