# backend/src/auth/jwt.py
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, Dict
from src.config import settings

# Alias para facilitar
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT de acesso.
    
    Args:
        data: Dados a serem codificados no token (ex: {"sub": user_id, "email": email})
        expires_delta: Tempo de expiração personalizado
    
    Returns:
        Token JWT como string
    """
    to_encode = data.copy()
    
    # Definir tempo de expiração
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Adicionar claims padrão
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),  # Issued at
        "type": "access"  # Tipo do token
    })
    
    # Criar token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: int) -> str:
    """
    Cria um token de refresh (mais longo)
    """
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[Dict]:
    """
    Decodifica e valida um token JWT.
    
    Returns:
        Dados do token se válido, None se inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"Erro ao decodificar token: {e}")
        return None

def verify_token(token: str, token_type: str = "access") -> Optional[Dict]:
    """
    Verifica se o token é válido e do tipo correto.
    """
    payload = decode_token(token)
    if not payload:
        return None
    
    # Verificar tipo
    if payload.get("type") != token_type:
        return None
    
    return payload

def get_user_id_from_token(token: str) -> Optional[int]:
    """
    Extrai o ID do usuário do token.
    """
    payload = decode_token(token)
    if payload and "sub" in payload:
        try:
            return int(payload["sub"])
        except:
            return None
    return None

# Opcional: Gerar token para reset de senha
def create_password_reset_token(email: str) -> str:
    """
    Token de curta duração para reset de senha
    """
    expire = datetime.utcnow() + timedelta(minutes=15)  # 15 minutos
    
    to_encode = {
        "sub": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "password_reset"
    }
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)