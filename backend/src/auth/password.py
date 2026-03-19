import bcrypt
import hashlib

def hash_password(password: str) -> str:
    """Hash com SHA256 + bcrypt - suporta senhas de qualquer tamanho"""
    # Reduz qualquer senha para 64 bytes fixos
    sha = hashlib.sha256(password.encode()).digest()
    # Aplica bcrypt no hash SHA256
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(sha, salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verifica senha com SHA256 + bcrypt"""
    sha = hashlib.sha256(password.encode()).digest()
    try:
        return bcrypt.checkpw(sha, hashed.encode('utf-8'))
    except:
        return False
