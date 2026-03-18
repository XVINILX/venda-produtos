from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_active_user
from src.schemas.user_schema import UserResponse

router = APIRouter(prefix="/users")

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_active_user)):
    """
    Retorna dados do usuário atual.
    Requer token válido.
    """
    return current_user