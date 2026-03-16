import bcrypt
import hashlib

def hash_password(password: str) -> bytes:
    sha = hashlib.sha256(password.encode()).digest()
    return bcrypt.hashpw(sha, bcrypt.gensalt())

def verify_password(password: str, hashed: bytes) -> bool:
    sha = hashlib.sha256(password.encode()).digest()
    return bcrypt.checkpw(sha, hashed)