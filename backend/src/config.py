from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "wisesales")
DB_USER = os.getenv("DB_USER", "wisesales")
DB_PASSWORD = os.getenv("DB_PASSWORD", "wisesales123")
class Settings(BaseSettings):
    # Database PostgreSQL
    db_host: str = DB_HOST
    db_port: int = DB_PORT
    db_name: str = DB_NAME
    db_user: str = DB_USER
    db_password: str = DB_PASSWORD
    
    # JWT
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7 
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    @property
    def database_url(self) -> str:
        """Retorna URL de conexão com PostgreSQL"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()