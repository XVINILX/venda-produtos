# backend/src/repositories/coupon_repository.py
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict
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