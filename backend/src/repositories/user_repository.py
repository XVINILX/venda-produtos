# backend/src/repositories/user_repository.py
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, List
from src.config import settings

class UserRepository:
    def __init__(self):
        self.conn_string = (
            f"host={settings.db_host} port={settings.db_port} "
            f"dbname={settings.db_name} user={settings.db_user} "
            f"password={settings.db_password}"
        )
    
    def _get_connection(self):
        return psycopg2.connect(self.conn_string)
    
    def create(self, email: str, password: str, name: Optional[str] = None, is_admin: bool = False) -> Dict:
        """Insere um novo usuário no banco PostgreSQL"""
        query = """
            INSERT INTO users (email, password, name, is_admin, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING id, email, name, is_admin, created_at
        """
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (email, password, name, is_admin))
                conn.commit()
                result = cur.fetchone()
                return dict(result) if result else None
    
    def get_by_email(self, email: str) -> Optional[Dict]:
        """Busca usuário por email"""
        query = """
            SELECT id, email, password, name, is_admin, created_at 
            FROM users 
            WHERE email = %s
        """
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (email,))
                row = cur.fetchone()
                return dict(row) if row else None
    
    def get_by_id(self, user_id: int) -> Optional[Dict]:
        """Busca usuário por ID"""
        query = """
            SELECT id, email, name, is_admin, created_at 
            FROM users 
            WHERE id = %s
        """
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (user_id,))
                row = cur.fetchone()
                return dict(row) if row else None
    
    def get_all(self) -> List[Dict]:
        """Lista todos os usuários"""
        query = """
            SELECT id, email, name, is_admin, created_at 
            FROM users 
            ORDER BY id
        """
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                rows = cur.fetchall()
                return [dict(row) for row in rows]
    
    def make_admin(self, user_id: int) -> bool:
        """Torna um usuário admin"""
        query = "UPDATE users SET is_admin = true WHERE id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                conn.commit()
                return cur.rowcount > 0