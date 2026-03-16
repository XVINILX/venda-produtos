# backend/src/repositories/product_repository.py
import sqlite3
from typing import Optional, Dict, List
from src.config import settings

class ProductRepository:
    def __init__(self):
        self.db_path = settings.database_url.replace('sqlite:///', '')
    
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_products(self, category: Optional[str] = None) -> List[Dict]:
        if category:
            query = "SELECT * FROM products WHERE category = ? AND stock > 0"
            params = (category,)
        else:
            query = "SELECT * FROM products WHERE stock > 0"
            params = ()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        query = "SELECT * FROM products WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (product_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_stock(self, product_id: int, quantity: int) -> bool:
        query = "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (quantity, product_id, quantity))
            conn.commit()
            return cursor.rowcount > 0