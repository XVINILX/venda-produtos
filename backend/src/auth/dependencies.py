from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.repositories.user_repository import UserRepository
from src.auth.jwt_handler import decode_token, get_user_id_from_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


user_repo = UserRepository()

async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)):
    """
    Obtém o usuário atual a partir do token.
    Retorna None se não autenticado.
    """
    if not token:
        return None
    
    # Decodificar token
    user_id = get_user_id_from_token(token)
    if not user_id:
        return None
    
    # Buscar usuário no banco
    user = user_repo.get_by_id(user_id)
    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """
    Obtém o usuário atual e verifica se está ativo.
    Levanta exceção se não autenticado.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar se usuário está ativo (se tiver o campo)
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
    
    return current_user

async def get_current_admin(current_user: dict = Depends(get_current_user)):
    """
    Verifica se o usuário atual é admin.
    Levanta exceção se não for admin.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )
    
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Privilégios de administrador necessários."
        )
    
    return current_user