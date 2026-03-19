# backend/src/repositories/cart_repository.py
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, List
from src.config import settings
from decimal import Decimal
from datetime import datetime

class CartRepository:
    def __init__(self):
        self.conn_string = (
            f"host={settings.db_host} port={settings.db_port} "
            f"dbname={settings.db_name} user={settings.db_user} "
            f"password={settings.db_password}"
        )
    
    def _get_connection(self):
        """Cria conexão com PostgreSQL"""
        return psycopg2.connect(self.conn_string)
    
    def _convert_decimals(self, item):
        """Converte campos Decimal para float"""
        if item and 'price' in item and isinstance(item['price'], Decimal):
            item['price'] = float(item['price'])
        if item and 'subtotal' in item and isinstance(item['subtotal'], Decimal):
            item['subtotal'] = float(item['subtotal'])
        if item and 'discount_amount' in item and isinstance(item['discount_amount'], Decimal):
            item['discount_amount'] = float(item['discount_amount'])
        if item and 'final_amount' in item and isinstance(item['final_amount'], Decimal):
            item['final_amount'] = float(item['final_amount'])
        return item
    
    # ==================== CART METHODS ====================
    
    def get_or_create_active_cart(self, user_id: int) -> Dict:
        """Obtém ou cria um carrinho ativo para o usuário"""
        # Tentar buscar carrinho ativo existente
        query = """
            SELECT id, user_id, status, coupon_code, discount_amount, 
                   subtotal_amount, final_amount, created_at
            FROM carts 
            WHERE user_id = %s AND status = 'active'
        """
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (user_id,))
                cart = cur.fetchone()
                
                if cart:
                    return self._convert_decimals(dict(cart))
                
                # Se não existe, criar novo
                insert_query = """
                    INSERT INTO carts (user_id, status, created_at, discount_amount, final_amount, subtotal_amount)
                    VALUES (%s, 'active', %s, %s, %s, %s)
                    RETURNING id, user_id, status, coupon_code, discount_amount, 
                              subtotal_amount, final_amount, created_at
                """
                cur.execute(insert_query, (user_id, datetime.now(), 0, 0, 0))
                conn.commit()
                new_cart = cur.fetchone()
                return self._convert_decimals(dict(new_cart))
    
    def get_cart_by_id(self, cart_id: int) -> Optional[Dict]:
        """Busca carrinho por ID"""
        query = """
            SELECT id, user_id, status, coupon_code, discount_amount, 
                   subtotal_amount, final_amount, created_at, completed_at
            FROM carts 
            WHERE id = %s
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (cart_id,))
                cart = cur.fetchone()
                return self._convert_decimals(dict(cart)) if cart else None
    
    def get_active_cart_by_user(self, user_id: int) -> Optional[Dict]:
        """Busca carrinho ativo do usuário"""
        query = """
            SELECT id, user_id, status, coupon_code, discount_amount, 
                   subtotal_amount, final_amount, created_at
            FROM carts 
            WHERE user_id = %s AND status = 'active'
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (user_id,))
                cart = cur.fetchone()
                return self._convert_decimals(dict(cart)) if cart else None
    
    def update_cart_totals(self, cart_id: int) -> Dict:
        """Atualiza os totais do carrinho baseado nos itens"""
        # Calcular subtotal dos itens
        query = """
            UPDATE carts 
            SET subtotal_amount = (
                SELECT COALESCE(SUM(ci.quantity * p.price), 0)
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.id
                WHERE ci.cart_id = %s
            ),
            final_amount = (
                SELECT COALESCE(SUM(ci.quantity * p.price), 0)
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.id
                WHERE ci.cart_id = %s
            ) - COALESCE(discount_amount, 0)
            WHERE id = %s
            RETURNING id, user_id, status, coupon_code, discount_amount, 
                      subtotal_amount, final_amount, created_at
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (cart_id, cart_id, cart_id))
                conn.commit()
                cart = cur.fetchone()
                return self._convert_decimals(dict(cart))
    
    def update_cart_coupon(self, cart_id: int, coupon_code: Optional[str], discount: float) -> Dict:
        """Atualiza cupom e desconto do carrinho"""
        query = """
            UPDATE carts 
            SET coupon_code = %s,
                discount_amount = %s,
                final_amount = subtotal_amount - %s
            WHERE id = %s
            RETURNING id, user_id, status, coupon_code, discount_amount, 
                      subtotal_amount, final_amount, created_at
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (coupon_code, discount, discount, cart_id))
                conn.commit()
                cart = cur.fetchone()
                return self._convert_decimals(dict(cart))
    
    def complete_cart(self, cart_id: int) -> Dict:
        """Marca carrinho como finalizado"""
        query = """
            UPDATE carts 
            SET status = 'completed',
                completed_at = %s
            WHERE id = %s
            RETURNING id, user_id, status, final_amount, completed_at
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (datetime.now(), cart_id))
                conn.commit()
                cart = cur.fetchone()
                return dict(cart) if cart else None
    
    def get_user_carts_history(self, user_id: int) -> List[Dict]:
        """Retorna histórico de carrinhos finalizados do usuário"""
        query = """
            SELECT id, user_id, status, coupon_code, final_amount, 
                   created_at, completed_at
            FROM carts 
            WHERE user_id = %s AND status = 'completed'
            ORDER BY completed_at DESC
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (user_id,))
                carts = cur.fetchall()
                return [self._convert_decimals(dict(cart)) for cart in carts]
    
    # ==================== CART ITEMS METHODS ====================
    
    def get_cart_items(self, cart_id: int) -> List[Dict]:
        """Retorna todos os itens de um carrinho com detalhes dos produtos"""
        query = """
            SELECT 
                ci.id,
                ci.cart_id,
                ci.product_id,
                ci.quantity,
                ci.created_at,
                p.name as product_name,
                p.price as unit_price,
                (ci.quantity * p.price) as subtotal
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.cart_id = %s
            ORDER BY ci.created_at
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (cart_id,))
                items = cur.fetchall()
                return [self._convert_decimals(dict(item)) for item in items]
            
    def get_cart_items_admin(self) -> List[Dict]:
        """Retorna todos os itens de um carrinho com detalhes dos produtos"""
        query = """
            SELECT 
                ci.id,
                ci.cart_id,
                ci.product_id,
                ci.quantity,
                ci.created_at,
                p.name as product_name,
                p.price as unit_price,
                (ci.quantity * p.price) as subtotal
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            ORDER BY ci.created_at
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                items = cur.fetchall()
                return [self._convert_decimals(dict(item)) for item in items]
    
    def get_cart_item(self, item_id: int, user_id: int) -> Optional[Dict]:
        """Busca um item do carrinho verificando se pertence ao usuário"""
        query = """
            SELECT 
                ci.id,
                ci.cart_id,
                ci.product_id,
                ci.quantity,
                ci.created_at,
                p.name as product_name,
                p.price as unit_price,
                p.stock as product_stock
            FROM cart_items ci
            JOIN carts c ON ci.cart_id = c.id
            JOIN products p ON ci.product_id = p.id
            WHERE ci.id = %s AND c.user_id = %s AND c.status = 'active'
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (item_id, user_id))
                item = cur.fetchone()
                return self._convert_decimals(dict(item)) if item else None
    
    def get_cart_item_by_product(self, cart_id: int, product_id: int) -> Optional[Dict]:
        """Busca item do carrinho por produto"""
        query = """
            SELECT id, cart_id, product_id, quantity, created_at
            FROM cart_items 
            WHERE cart_id = %s AND product_id = %s
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (cart_id, product_id))
                item = cur.fetchone()
                return dict(item) if item else None
    
    def add_cart_item(self, cart_id: int, product_id: int, quantity: int) -> Dict:
        """Adiciona um novo item ao carrinho"""
        query = """
            INSERT INTO cart_items (cart_id, product_id, quantity, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id, cart_id, product_id, quantity, created_at
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (cart_id, product_id, quantity, datetime.now()))
                conn.commit()
                item = cur.fetchone()
                return dict(item)
    
    def update_cart_item_quantity(self, item_id: int, quantity: int) -> Dict:
        """Atualiza quantidade de um item"""
        query = """
            UPDATE cart_items 
            SET quantity = %s
            WHERE id = %s
            RETURNING id, cart_id, product_id, quantity, created_at
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (quantity, item_id))
                conn.commit()
                item = cur.fetchone()
                return dict(item) if item else None
    
    def remove_cart_item(self, item_id: int) -> bool:
        """Remove um item do carrinho"""
        query = "DELETE FROM cart_items WHERE id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (item_id,))
                conn.commit()
                return cur.rowcount > 0
    
    def clear_cart_items(self, cart_id: int) -> bool:
        """Remove todos os itens de um carrinho"""
        query = "DELETE FROM cart_items WHERE cart_id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (cart_id,))
                conn.commit()
                return True
    
    # ==================== PRODUCT METHODS ====================
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Busca produto por ID"""
        query = """
            SELECT id, name, price, stock, category, image_url
            FROM products 
            WHERE id = %s
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (product_id,))
                product = cur.fetchone()
                return self._convert_decimals(dict(product)) if product else None
    
    def update_product_stock(self, product_id: int, quantity: int) -> bool:
        """Atualiza estoque do produto (subtrai quantidade)"""
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
    
    # ==================== COUPON METHODS ====================
    
    def get_valid_coupon(self, code: str) -> Optional[Dict]:
        """Busca cupom válido (ativo e não expirado)"""
        query = """
            SELECT id, code, discount_type, discount_value, active, expires_at
            FROM coupons
            WHERE code = %s AND active = true AND expires_at > %s
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (code.upper(), datetime.now()))
                coupon = cur.fetchone()
                return self._convert_decimals(dict(coupon)) if coupon else None