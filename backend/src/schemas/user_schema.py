# backend/src/schemas/auth_schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    """Schema para criação de usuário"""
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., min_length=6, description="Senha do usuário")
    full_name: Optional[str] = Field(None, description="Nome completo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "joao@email.com",
                "password": "senha123",
                "full_name": "João da Silva"
            }
        }

class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "joao@email.com",
                "password": "senha123"
            }
        }

class UserResponse(BaseModel):
    """Schema para resposta de usuário"""
    id: int = Field(..., description="ID do usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    name: Optional[str] = Field(None, description="Nome completo")
    is_active: bool = Field(True, description="Status da conta")
    is_admin: bool = Field(True, description="Administrador ou não")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "joao@email.com",
                "name": "João da Silva",
                "is_active": True,
                'is_admin': False
            }
        }



class TokenResponse(BaseModel):
    """Schema para resposta de token"""
    access_token: str = Field(..., description="Token JWT")
    token_type: str = Field("bearer", description="Tipo do token")
    user: Optional[UserResponse] = Field(None, description="Dados do usuário")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "joao@email.com",
                    "full_name": "João da Silva"
                }
            }
        }