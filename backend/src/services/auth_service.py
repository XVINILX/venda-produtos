# backend/src/services/auth_service.py
from passlib.context import CryptContext
from typing import List, Optional, Dict
from src.auth.password import hash_password, verify_password
from src.repositories.user_repository import UserRepository
from fastapi import HTTPException, status

# Configuração do hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
    
    
    def register_user(self, email: str, password: str, name: Optional[str] = None) -> Dict:
        """
        Regras de negócio para registro de usuário
        """
        # Validar email
        if not email or '@' not in email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email inválido"
            )
        
        # Validar senha
        if len(password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha deve ter no mínimo 6 caracteres"
            )
        
        # Verificar se usuário já existe
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email já cadastrado"
            )
        
        # Criar usuário
        password = hash_password(password)
        user = self.user_repo.create(email, password, name)
        
        # Remover dados sensíveis antes de retornar
        return user
    
    def login_user(self, email: str, password: str) -> Dict:
        """
        Regras de negócio para login
        """
        # Buscar usuário
        user = self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        # Verificar senha
        if not verify_password(password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        # Gerar token (simplificado para exemplo)
        token = f"token_ficticio_{user['id']}"
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"]
            }
        }
    
    def get_user_profile(self, user_id: int) -> Dict:
        """
        Busca perfil do usuário
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        return user
    
    def list_all_users(self) -> List[Dict]:
        """
        Lista todos os usuários (apenas para admin)
        """
        return self.user_repo.get_all()
    
    def update_user(self, user_id: int, data: Dict) -> Dict:
        """
        Atualiza dados do usuário
        """
        # Validar dados antes de atualizar
        if "email" in data:
            # Verificar se email já existe
            existing = self.user_repo.get_by_email(data["email"])
            if existing and existing["id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email já está em uso"
                )
        
        if "password" in data:
            data["password"] = self._hash_password(data.pop("password"))
        
        user = self.user_repo.update(user_id, data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """
        Remove um usuário
        """
        if not self.user_repo.delete(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        return True