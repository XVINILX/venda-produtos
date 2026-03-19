# backend/tests/test_auth.py
import pytest
from fastapi import status

def test_register_user(client):
    """Testa registro de usuário"""
    response = client.post("/auth/register", json={
        "name": "Usuário Teste",
        "email": "teste@email.com",
        "password": "senha123",
        "confirm_password": "senha123"
    })
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "teste@email.com"
    assert data["name"] == "Usuário Teste"
    assert "id" in data

def test_register_duplicate_email(client):
    """Testa registro com email duplicado"""
    # Primeiro registro
    client.post("/auth/register", json={
        "name": "Usuário 1",
        "email": "duplicado@email.com",
        "password": "senha123",
        "confirm_password": "senha123"
    })
    
    # Segundo registro com mesmo email
    response = client.post("/auth/register", json={
        "name": "Usuário 2",
        "email": "duplicado@email.com",
        "password": "senha456",
        "confirm_password": "senha456"
    })
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "já cadastrado" in response.json()["detail"].lower()

def test_login_success(client):
    """Testa login com sucesso"""
    # Registrar usuário
    client.post("/auth/register", json={
        "name": "Login Teste",
        "email": "login@email.com",
        "password": "senha123",
        "confirm_password": "senha123"
    })
    
    # Fazer login
    response = client.post("/auth/login", json={
        "email": "login@email.com",
        "password": "senha123"
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "login@email.com"

def test_login_wrong_password(client):
    """Testa login com senha errada"""
    # Registrar usuário
    client.post("/auth/register", json={
        "name": "Login Teste",
        "email": "login2@email.com",
        "password": "senha123",
        "confirm_password": "senha123"
    })
    
    # Tentar login com senha errada
    response = client.post("/auth/login", json={
        "email": "login2@email.com",
        "password": "senha_errada"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_register_password_mismatch(client):
    """Testa registro com senhas diferentes"""
    response = client.post("/auth/register", json={
        "name": "Teste",
        "email": "teste@email.com",
        "password": "senha123",
        "confirm_password": "senha_diferente"
    })
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "não conferem" in response.json()["detail"].lower()