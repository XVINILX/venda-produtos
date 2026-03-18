# backend/src/repositories/cart_repository.py
from decimal import Decimal

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, List
from src.config import settings

class CartRepository:
    def __init__(self):
        self.conn_string = (
            f"host={settings.db_host} port={settings.db_port} "
            f"dbname={settings.db_name} user={settings.db_user} "
            f"password={settings.db_password}"
        )
    
    def _get_connection(self):
        return psycopg2.connect(self.conn_string)
    

    def get_cart_items_admin(self) -> List[Dict]:
        """Retorna todos os itens do carrinho com detalhes dos produtos"""
        query = """
            SELECT 
                ci.id,
                ci.product_id,
                p.name as product_name,
                ci.quantity,
                p.price as unit_price,
                (ci.quantity * p.price) as subtotal
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            ORDER BY ci.created_at
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query,)
                results = cur.fetchall()
                # Converter Decimals para float
                items = []
                for row in results:
                    item = dict(row)
                    if 'unit_price' in item and isinstance(item['unit_price'], Decimal):
                        item['unit_price'] = float(item['unit_price'])
                    if 'subtotal' in item and isinstance(item['subtotal'], Decimal):
                        item['subtotal'] = float(item['subtotal'])
                    items.append(item)
                return items


    def get_cart_items(self, user_id: int) -> List[Dict]:
        """Retorna todos os itens do carrinho com detalhes dos produtos"""
        query = """
            SELECT 
                ci.id,
                ci.product_id,
                p.name as product_name,
                ci.quantity,
                p.price as unit_price,
                (ci.quantity * p.price) as subtotal
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.user_id = %s
            ORDER BY ci.created_at
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (user_id,))
                results = cur.fetchall()
                # Converter Decimals para float
                items = []
                for row in results:
                    item = dict(row)
                    if 'unit_price' in item and isinstance(item['unit_price'], Decimal):
                        item['unit_price'] = float(item['unit_price'])
                    if 'subtotal' in item and isinstance(item['subtotal'], Decimal):
                        item['subtotal'] = float(item['subtotal'])
                    items.append(item)
                return items
    
    def get_cart_item(self, item_id: int) -> Optional[Dict]:
        """Busca um item específico do carrinho"""
        query = """
            SELECT 
                ci.id,
                ci.product_id,
                p.name as product_name,
                ci.quantity,
                p.price as unit_price
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.id = %s
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (item_id,))
                row = cur.fetchone()
                return dict(row) if row else None
    
    def find_cart_item_by_product(self, product_id: int) -> Optional[Dict]:
        """Verifica se um produto já está no carrinho"""
        query = """
            SELECT id, quantity FROM cart_items WHERE product_id = %s
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (product_id,))
                row = cur.fetchone()
                return dict(row) if row else None
    
    def add_item(self, product_id: int, quantity: int, user_id: int) -> Dict:
        """Adiciona um novo item ao carrinho"""
        query = """
            INSERT INTO cart_items (product_id, quantity, user_id)
            VALUES (%s, %s, %s)
            RETURNING id
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (product_id, quantity, user_id))
                conn.commit()
                new_id = cur.fetchone()['id']
                return self.get_cart_item(new_id)
    
    def update_item_quantity(self, item_id: int, quantity: int) -> Optional[Dict]:
        """Atualiza quantidade de um item"""
        query = """
            UPDATE cart_items 
            SET quantity = %s 
            WHERE id = %s
            RETURNING id
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (quantity, item_id))
                conn.commit()
                if cur.rowcount > 0:
                    return self.get_cart_item(item_id)
                return None
    
    def remove_item(self, item_id: int) -> bool:
        """Remove um item do carrinho"""
        query = "DELETE FROM cart_items WHERE id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (item_id,))
                conn.commit()
                return cur.rowcount > 0
    
    def clear_cart(self) -> bool:
        """Remove todos os itens do carrinho"""
        query = "DELETE FROM cart_items"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                conn.commit()
                return True