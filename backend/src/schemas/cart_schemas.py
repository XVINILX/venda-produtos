# backend/src/schemas/cart_schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class CartItemCreate(BaseModel):
    """Schema para adicionar item ao carrinho"""
    product_id: int = Field(..., gt=0, description="ID do produto")
    quantity: int = Field(..., gt=0, description="Quantidade")

class CartItemUpdate(BaseModel):
    """Schema para atualizar item do carrinho"""
    quantity: int = Field(..., ge=0, description="Quantidade (0 remove o item)")

class CartItemResponse(BaseModel):
    """Schema para resposta de item do carrinho"""
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float

class CouponApply(BaseModel):
    """Schema para aplicar cupom"""
    code: str = Field(..., min_length=3, description="Código do cupom")

class CartResponse(BaseModel):
    """Schema para resposta completa do carrinho"""
    items: List[CartItemResponse]
    subtotal: float
    discount: float = 0
    total: float
    coupon_code: Optional[str] = None
    coupon_discount: Optional[float] = None