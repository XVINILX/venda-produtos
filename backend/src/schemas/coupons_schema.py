# backend/src/schemas/coupon_schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CouponResponse(BaseModel):
    """Schema para resposta de cupom"""
    id: int
    code: str
    discount_type: str  # 'percentage' ou 'fixed'
    discount_value: float
    active: bool
    expires_at: datetime