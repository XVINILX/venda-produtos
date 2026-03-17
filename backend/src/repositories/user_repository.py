# backend/src/repositories/user_repository.py
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, List
from datetime import datetime
from src.config import settings

class UserRepository:
    def __init__(self):
        """Inicializa conexão com PostgreSQL"""
        self.conn_string = (
            f"host={settings.db_host} port={settings.db_port} "
            f"dbname={settings.db_name} user={settings.db_user} "
            f"password={settings.db_password}"
        )
    
    def _get_connection(self):
        """Cria conexão com PostgreSQL"""
        return psycopg2.connect(self.conn_string)
    
    def create(self, email: str, password: str, name: Optional[str] = None) -> Dict:
        """Insere um novo usuário no banco PostgreSQL"""
        query = """
            INSERT INTO users (email, password, name, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id, email, name, created_at
        """
        
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        query, 
                        (email, password, name, datetime.now())
                    )
                    conn.commit()
                    result = cur.fetchone()
                    return dict(result) if result else None
        except psycopg2.IntegrityError as e:
            if "unique constraint" in str(e).lower():
                raise ValueError(f"Email {email} já está cadastrado")
            raise e
    
    def get_by_email(self, email: str) -> Optional[Dict]:
        """Busca usuário por email"""
        query = """
            SELECT id, email, password, name, created_at 
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
            SELECT id, email, name, created_at 
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
            SELECT id, email, name, created_at 
            FROM users 
            ORDER BY id
        """
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                rows = cur.fetchall()
                return [dict(row) for row in rows]
    
    def update(self, user_id: int, data: Dict) -> Optional[Dict]:
        """Atualiza dados de um usuário"""
        fields = []
        values = []
        
        for key, value in data.items():
            if value is not None:
                fields.append(f"{key} = %s")
                values.append(value)
        
        if not fields:
            return self.get_by_id(user_id)
        
        # Adicionar updated_at
        fields.append("updated_at = %s")
        values.append(datetime.now())
        
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = %s RETURNING id, email, name"
        values.append(user_id)
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute(query, values)
                    conn.commit()
                    result = cur.fetchone()
                    return dict(result) if result else None
                except psycopg2.IntegrityError as e:
                    if "unique constraint" in str(e).lower():
                        raise ValueError("Email já está em uso")
                    raise e
    
    def delete(self, user_id: int) -> bool:
        """Remove um usuário"""
        query = "DELETE FROM users WHERE id = %s RETURNING id"
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                conn.commit()
                return cur.rowcount > 0
    
    def get_users_paginated(self, page: int = 1, per_page: int = 10) -> Dict:
        """Busca usuários com paginação"""
        offset = (page - 1) * per_page
        
        # Buscar usuários
        query = """
            SELECT id, email, name, created_at 
            FROM users 
            ORDER BY id 
            LIMIT %s OFFSET %s
        """
        
        # Contar total
        count_query = "SELECT COUNT(*) as total FROM users"
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Buscar dados
                cur.execute(query, (per_page, offset))
                items = [dict(row) for row in cur.fetchall()]
                
                # Buscar total
                cur.execute(count_query)
                total = cur.fetchone()['total']
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def search_users(self, term: str) -> List[Dict]:
        """Busca usuários por termo (email ou nome)"""
        query = """
            SELECT id, email, name, created_at 
            FROM users 
            WHERE email ILIKE %s OR name ILIKE %s
            ORDER BY id
            LIMIT 20
        """
        search_term = f"%{term}%"
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (search_term, search_term))
                rows = cur.fetchall()
                return [dict(row) for row in rows]
    
    def count_users(self) -> int:
        """Retorna total de usuários"""
        query = "SELECT COUNT(*) as total FROM users"
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                result = cur.fetchone()
                return result['total'] if result else 0
    
    def user_exists(self, email: str) -> bool:
        """Verifica se usuário existe pelo email"""
        query = "SELECT id FROM users WHERE email = %s"
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (email,))
                return cur.fetchone() is not None


# Exemplo de uso:
if __name__ == "__main__":
    # Teste rápido
    repo = UserRepository()
    
    # Criar usuário
    try:
        user = repo.create(
            email="teste@email.com",
            password="hash123",
            name="Usuário Teste"
        )
        print(f"✅ Usuário criado: {user}")
    except ValueError as e:
        print(f"❌ Erro: {e}")
    
    # Listar usuários
    users = repo.get_all()
    print(f"\n📋 Total de usuários: {len(users)}")
    for u in users:
        print(f"   - {u['email']} ({u['name']})")