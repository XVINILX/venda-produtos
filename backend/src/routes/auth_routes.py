from fastapi import APIRouter, status
from src.schemas.auth_schemas import (
    UserCreate, UserLogin, UserResponse, 
    TokenResponse
)
from src.services.auth_service import AuthService
from typing import List

router = APIRouter(prefix="/auth", tags=["auth"])

# Instância do serviço (em produção, use injeção de dependência)
auth_service = AuthService()

@router.post(
    "/register/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário"
)
async def register(user_data: UserCreate):
    """
    Registra um novo usuário no sistema.
    
    - **email**: Email válido e único
    - **password**: Senha (mínimo 6 caracteres)
    - **full_name**: Nome completo (opcional)
    """
    user = auth_service.register_user(
        email=user_data.email,
        password=user_data.password,
        name=user_data.name
    )
    return user

@router.post(
    "/login/",
    response_model=TokenResponse,
    summary="Login de usuário"
)
async def login(user_data: UserLogin):
    """
    Autentica um usuário e retorna token de acesso.
    
    - **email**: Email do usuário
    - **password**: Senha do usuário
    """
    result = auth_service.login_user(
        email=user_data.email,
        password=user_data.password
    )
    return result

@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="Listar todos os usuários"
)
async def list_users():
    """
    Retorna lista de todos os usuários cadastrados.
    """
    return auth_service.list_all_users()

@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Buscar usuário por ID"
)
async def get_user(user_id: int):
    """
    Retorna dados de um usuário específico.
    
    - **user_id**: ID do usuário
    """
    return auth_service.get_user_profile(user_id)

@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Atualizar usuário"
)
async def update_user(user_id: int, user_data: dict):
    """
    Atualiza dados de um usuário.
    
    - **user_id**: ID do usuário
    - **user_data**: Dados a serem atualizados
    """
    return auth_service.update_user(user_id, user_data)

@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover usuário"
)
async def delete_user(user_id: int):
    """
    Remove um usuário do sistema.
    
    - **user_id**: ID do usuário
    """
    auth_service.delete_user(user_id)
    return None