from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class CouponBase(BaseModel):
    """Schema base para cupom"""
    code: str = Field(..., min_length=3, max_length=50, description="Código único do cupom")
    discount_type: str = Field(..., description="Tipo de desconto: 'percentage' ou 'fixed'")
    discount_value: float = Field(..., gt=0, description="Valor do desconto")
    active: bool = Field(True, description="Se o cupom está ativo")
    expires_at: datetime = Field(..., description="Data de expiração")

class CouponCreate(CouponBase):
    """Schema para criação de cupom"""
    pass

class CouponUpdate(BaseModel):
    """Schema para atualização de cupom"""
    code: Optional[str] = Field(None, min_length=3, max_length=50)
    discount_type: Optional[str] = None
    discount_value: Optional[float] = Field(None, gt=0)
    active: Optional[bool] = None
    expires_at: Optional[datetime] = None

class CouponResponse(CouponBase):
    """Schema para resposta com dados do cupom"""
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CouponListResponse(BaseModel):
    """Schema para listagem de cupons"""
    items: List[CouponResponse]
    total: int
    active_count: int
    expired_count: int