# backend/src/repositories/coupon_repository.py
from decimal import Decimal

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional, Dict
from src.config import settings
from datetime import datetime

class CouponRepository:
    def __init__(self):
        self.conn_string = (
            f"host={settings.db_host} port={settings.db_port} "
            f"dbname={settings.db_name} user={settings.db_user} "
            f"password={settings.db_password}"
        )
    
    def _get_connection(self):
        return psycopg2.connect(self.conn_string)
    
    def get_coupon_by_code(self, code: str) -> Optional[Dict]:
        """Busca cupom pelo código"""
        query = """
            SELECT id, code, discount_type, discount_value, active, expires_at
            FROM coupons
            WHERE code = %s
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (code.upper(),))
                row = cur.fetchone()
                return dict(row) if row else None
    
    def validate_coupon(self, code: str) -> Optional[Dict]:
        """Valida se cupom existe, está ativo e não expirou"""
        query = """
            SELECT id, code, discount_type, discount_value, active, expires_at
            FROM coupons
            WHERE code = %s 
                AND active = true 
                AND expires_at > %s
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (code.upper(), datetime.now()))
                row = cur.fetchone()
                return dict(row) if row else None
            
    def _convert_decimals(self, item):
        """Converte campos Decimal para float"""
        if item and 'discount_value' in item and isinstance(item['discount_value'], Decimal):
            item['discount_value'] = float(item['discount_value'])
        return item
    
    # ==================== CREATE ====================
    
    def create_coupon(self, coupon_data: Dict) -> Dict:
        """Cria um novo cupom"""
        query = """
            INSERT INTO coupons (
                code, discount_type, discount_value, active, expires_at, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, code, discount_type, discount_value, active, expires_at, created_at
        """
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (
                    coupon_data['code'].upper(),
                    coupon_data['discount_type'],
                    coupon_data['discount_value'],
                    coupon_data.get('active', True),
                    coupon_data['expires_at'],
                    datetime.now()
                ))
                conn.commit()
                result = cur.fetchone()
                return self._convert_decimals(dict(result))
    
    # ==================== READ ====================
    
    def get_coupon_by_id(self, coupon_id: int) -> Optional[Dict]:
        """Busca cupom por ID"""
        query = """
            SELECT id, code, discount_type, discount_value, active, expires_at, created_at
            FROM coupons 
            WHERE id = %s
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (coupon_id,))
                row = cur.fetchone()
                return self._convert_decimals(dict(row)) if row else None
    
    def get_coupon_by_code(self, code: str) -> Optional[Dict]:
        """Busca cupom por código"""
        query = """
            SELECT id, code, discount_type, discount_value, active, expires_at, created_at
            FROM coupons 
            WHERE code = %s
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (code.upper(),))
                row = cur.fetchone()
                return self._convert_decimals(dict(row)) if row else None
    
    def get_all_coupons(self) -> List[Dict]:
        """Lista todos os cupons"""
        query = """
            SELECT id, code, discount_type, discount_value, active, expires_at, created_at
            FROM coupons 
            ORDER BY created_at DESC
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                results = cur.fetchall()
                return [self._convert_decimals(dict(row)) for row in results]
    
    def get_active_coupons(self) -> List[Dict]:
        """Lista apenas cupons ativos e não expirados"""
        query = """
            SELECT id, code, discount_type, discount_value, active, expires_at, created_at
            FROM coupons 
            WHERE active = true AND expires_at > %s
            ORDER BY expires_at
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (datetime.now(),))
                results = cur.fetchall()
                return [self._convert_decimals(dict(row)) for row in results]
    
    def get_expired_coupons(self) -> List[Dict]:
        """Lista cupons expirados"""
        query = """
            SELECT id, code, discount_type, discount_value, active, expires_at, created_at
            FROM coupons 
            WHERE expires_at <= %s
            ORDER BY expires_at DESC
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (datetime.now(),))
                results = cur.fetchall()
                return [self._convert_decimals(dict(row)) for row in results]
    
    def get_valid_coupon(self, code: str) -> Optional[Dict]:
        """Busca cupom válido (ativo e não expirado) - usado pelo carrinho"""
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
    
    # ==================== UPDATE ====================
    
    def update_coupon(self, coupon_id: int, update_data: Dict) -> Optional[Dict]:
        """Atualiza um cupom existente"""
        fields = []
        values = []
        
        for key, value in update_data.items():
            if value is not None:
                if key == 'code':
                    value = value.upper()
                fields.append(f"{key} = %s")
                values.append(value)
        
        if not fields:
            return self.get_coupon_by_id(coupon_id)
        
        query = f"""
            UPDATE coupons 
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING id, code, discount_type, discount_value, active, expires_at, created_at
        """
        values.append(coupon_id)
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, values)
                conn.commit()
                result = cur.fetchone()
                return self._convert_decimals(dict(result)) if result else None
    
    def activate_coupon(self, coupon_id: int) -> Optional[Dict]:
        """Ativa um cupom"""
        return self.update_coupon(coupon_id, {"active": True})
    
    def deactivate_coupon(self, coupon_id: int) -> Optional[Dict]:
        """Desativa um cupom"""
        return self.update_coupon(coupon_id, {"active": False})
    
    # ==================== DELETE ====================
    
    def delete_coupon(self, coupon_id: int) -> bool:
        """Remove um cupom"""
        query = "DELETE FROM coupons WHERE id = %s RETURNING id"
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (coupon_id,))
                conn.commit()
                return cur.rowcount > 0
    
    # ==================== UTILS ====================
    
    def coupon_exists(self, code: str) -> bool:
        """Verifica se já existe cupom com este código"""
        query = "SELECT id FROM coupons WHERE code = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (code.upper(),))
                return cur.fetchone() is not None
    
    def get_coupon_stats(self) -> Dict:
        """Retorna estatísticas dos cupons"""
        query = """
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN active = true AND expires_at > %s THEN 1 END) as active,
                COUNT(CASE WHEN active = false THEN 1 END) as inactive,
                COUNT(CASE WHEN expires_at <= %s THEN 1 END) as expired
            FROM coupons
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (datetime.now(), datetime.now()))
                return dict(cur.fetchone())