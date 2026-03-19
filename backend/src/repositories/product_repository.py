from decimal import Decimal
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, List, Any
from src.schemas.product_schemas import ProductCreate
from src.config import settings
from datetime import datetime

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
    
    # ==================== MÉTODOS DE LEITURA ====================
    
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
            SELECT id, name,  price, category, stock, image_url, created_at
            FROM products 
            WHERE id = %s
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (product_id,))
                row = cur.fetchone()
                return self._convert_decimals(dict(row)) if row else None
    
    def get_product_by_name(self, name: str) -> Optional[Dict]:
        """Busca produto por nome (exato)"""
        query = """
            SELECT id, name, price, category, stock, image_url
            FROM products 
            WHERE name = %s
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (name,))
                row = cur.fetchone()
                return self._convert_decimals(dict(row)) if row else None
    
    def get_all_products_admin(self) -> List[Dict]:
        """Busca TODOS os produtos (incluindo sem estoque) - apenas para admin"""
        query = """
            SELECT id, name,  price, category, stock, image_url, created_at
            FROM products 
            ORDER BY id
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                results = cur.fetchall()
                return [self._convert_decimals(dict(row)) for row in results]
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        """Busca produtos por categoria específica"""
        query = """
            SELECT id, name, price, category, stock, image_url
            FROM products 
            WHERE category = %s
            ORDER BY id
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (category,))
                results = cur.fetchall()
                return [self._convert_decimals(dict(row)) for row in results]
    
    def get_categories(self) -> List[str]:
        """Retorna todas as categorias únicas"""
        query = """
            SELECT DISTINCT category 
            FROM products 
            ORDER BY category
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                results = cur.fetchall()
                return [row[0] for row in results]
    
    def get_low_stock_products(self, threshold: int = 5) -> List[Dict]:
        """Retorna produtos com estoque baixo"""
        query = """
            SELECT id, name, price, category, stock, image_url
            FROM products 
            WHERE stock <= %s AND stock > 0
            ORDER BY stock
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (threshold,))
                results = cur.fetchall()
                return [self._convert_decimals(dict(row)) for row in results]
    
    def get_out_of_stock_products(self) -> List[Dict]:
        """Retorna produtos esgotados"""
        query = """
            SELECT id, name, price, category, stock, image_url
            FROM products 
            WHERE stock = 0
            ORDER BY id
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                results = cur.fetchall()
                return [self._convert_decimals(dict(row)) for row in results]
    
    def search_products(self, search_term: str) -> List[Dict]:
        """Busca produtos por termo no nome ou descrição"""
        query = """
            SELECT id, name,  price, category, stock, image_url
            FROM products 
            WHERE name ILIKE %s
            ORDER BY name
            LIMIT 20
        """
        search_pattern = f"%{search_term}%"
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (search_pattern, search_pattern))
                results = cur.fetchall()
                return [self._convert_decimals(dict(row)) for row in results]
    
    def count_products(self) -> int:
        """Retorna o total de produtos"""
        query = "SELECT COUNT(*) as total FROM products"
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                result = cur.fetchone()
                return result['total'] if result else 0
    
    # ==================== MÉTODOS DE ESCRITA ====================
    
    def create_product(self, product_data: ProductCreate) -> Dict:
        """
        Cria um novo produto
        """
        query = """
            INSERT INTO products (
                name, price, category, stock, image_url, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, name, price, category, stock, image_url, created_at
        """
        
        image_url = product_data.image_url
        if image_url == '':
            image_url = None
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (
                    product_data.name,
                    product_data.price,
                    product_data.category,
                    product_data.stock,
                    image_url,
                    datetime.now()
                ))
                conn.commit()
                result = cur.fetchone()
                return self._convert_decimals(dict(result))
    
    def update_product(self, product_id: int, update_data: Dict) -> Optional[Dict]:
        """
        Atualiza um produto existente
        update_data: dicionário com apenas os campos a serem atualizados
        """
        # Construir query dinamicamente baseada nos campos fornecidos
        fields = []
        values = []
        
        for key, value in update_data.items():
            if value is not None:
                fields.append(f"{key} = %s")
                values.append(value)
        
        if not fields:
            # Nada para atualizar
            return self.get_product_by_id(product_id)
        
        query = f"""
            UPDATE products 
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING id, name,  price, category, stock, image_url, created_at
        """
        values.append(product_id)
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, values)
                conn.commit()
                result = cur.fetchone()
                return self._convert_decimals(dict(result)) if result else None
    
    def delete_product(self, product_id: int) -> bool:
        """Remove um produto pelo ID"""
        query = "DELETE FROM products WHERE id = %s RETURNING id"
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (product_id,))
                conn.commit()
                return cur.rowcount > 0
    
    def update_stock(self, product_id: int, quantity: int) -> bool:
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
    
    def set_stock(self, product_id: int, new_stock: int) -> Optional[Dict]:
        """Define o estoque para um valor específico"""
        if new_stock < 0:
            raise ValueError("Estoque não pode ser negativo")
        
        query = """
            UPDATE products 
            SET stock = %s 
            WHERE id = %s
            RETURNING id, name, stock
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (new_stock, product_id))
                conn.commit()
                result = cur.fetchone()
                return dict(result) if result else None
    
    # ==================== MÉTODOS DE VERIFICAÇÃO ====================
    
    def product_exists(self, product_id: int) -> bool:
        """Verifica se um produto existe pelo ID"""
        query = "SELECT id FROM products WHERE id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (product_id,))
                return cur.fetchone() is not None
    
    def check_stock_availability(self, product_id: int, requested_quantity: int) -> bool:
        """Verifica se há estoque suficiente"""
        query = "SELECT stock FROM products WHERE id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (product_id,))
                result = cur.fetchone()
                if result:
                    return result[0] >= requested_quantity
                return False