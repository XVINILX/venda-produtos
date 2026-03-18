# backend/src/repositories/product_repository.py
from decimal import Decimal

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, List
from src.config import settings

class ProductRepository:
    def __init__(self):
        self.conn_string = (
            f"host={settings.db_host} port={settings.db_port} "
            f"dbname={settings.db_name} user={settings.db_user} "
            f"password={settings.db_password}"
        )

    def _convert_decimals(self, item):
        """Converte campos Decimal para float"""
        if item and 'price' in item and isinstance(item['price'], Decimal):
            item['price'] = float(item['price'])
        return item
    
    def _get_connection(self):
        """Cria conexão com PostgreSQL"""
        return psycopg2.connect(self.conn_string)
    
    def get_products(self, category: Optional[str] = None) -> List[Dict]:
        """Busca produtos com filtro opcional por categoria"""
        if category:
            query = """
                SELECT id, name, price, category, stock, image_url
                FROM products 
                WHERE category = %s AND stock > 0
                ORDER BY id
            """
            params = (category,)
        else:
            query = """
                SELECT id, name, price, category, stock, image_url
                FROM products 
                WHERE stock > 0
                ORDER BY id
            """
            params = ()
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                results = cur.fetchall()
                return [self._convert_decimals(dict(row)) for row in results]
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Busca produto por ID"""
        query = """
            SELECT id, name, price, category, stock, image_url
            FROM products 
            WHERE id = %s
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (product_id,))
                row = cur.fetchone()
                return self._convert_decimals(dict(row)) if row else None
    
    def update_stock(self, product_id: int, quantity: int) -> bool:
        """Atualiza estoque do produto"""
        query = """
            UPDATE products 
            SET stock = stock - %s 
            WHERE id = %s AND stock >= %s
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (quantity, product_id, quantity))
                conn.commit()
                return cur.rowcount > 0