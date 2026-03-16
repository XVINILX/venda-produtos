# backend/src/repositories/user_repository.py
import sqlite3
from typing import Optional, Dict, List
from datetime import datetime

class UserRepository:
    def __init__(self):
        self.db_path = "wisesales.db"
    
    def _get_connection(self):
        """Cria conexão com o banco"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create(self, email: str, password: str, name: Optional[str] = None) -> Dict:
        """Insere um novo usuário no banco"""
        query = """
            INSERT INTO users (email, password, name)
            VALUES (?, ?, ?)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                query, 
                (email, password, name)
            )
            conn.commit()
            
            # Retorna o usuário criado
            return self.get_by_id(cursor.lastrowid)
    
    def get_by_email(self, email: str) -> Optional[Dict]:
        """Busca usuário por email"""
        query = "SELECT id, email, password, name FROM users WHERE email = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_by_id(self, user_id: int) -> Optional[Dict]:
        """Busca usuário por ID"""
        query = "SELECT id, email, name FROM users WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all(self) -> List[Dict]:
        """Lista todos os usuários"""
        query = "SELECT id, email, name FROM users"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def update(self, user_id: int, data: Dict) -> Optional[Dict]:
        """Atualiza dados de um usuário"""
        fields = []
        values = []
        
        for key, value in data.items():
            if value is not None:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return self.get_by_id(user_id)
        
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
        values.append(user_id)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            
            if cursor.rowcount > 0:
                return self.get_by_id(user_id)
            return None
    
    def delete(self, user_id: int) -> bool:
        """Remove um usuário"""
        query = "DELETE FROM users WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            conn.commit()
            return cursor.rowcount > 0