# backend/src/routes/cart_routes.py
from fastapi import APIRouter, Depends, HTTPException
from src.schemas.cart_schemas import (
    CartItemCreate,
    CartItemUpdate,
    CartResponse,
    ApplyCouponRequest, CheckoutResponse
)
from src.services.cart_service import CartService
from src.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/cart", tags=["Carrinho"])
cart_service = CartService()

@router.get("/", response_model=CartResponse)
async def get_cart(current_user: dict = Depends(get_current_active_user)):
    """Retorna o carrinho ativo do usuário"""
    return cart_service.get_cart(current_user["id"])

@router.get("/history")
async def get_cart_history(current_user: dict = Depends(get_current_active_user)):
    """Retorna histórico de compras do usuário"""
    return cart_service.get_cart_history(current_user["id"])

@router.post("/items", response_model=CartResponse)
async def add_to_cart(
    item_data: CartItemCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Adiciona item ao carrinho"""
    return cart_service.add_item(
        user_id=current_user["id"],
        product_id=item_data.product_id,
        quantity=item_data.quantity
    )

@router.patch("/items/{item_id}", response_model=CartResponse)
async def update_cart_item(
    item_id: int,
    item_data: CartItemUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Atualiza quantidade de um item"""
    return cart_service.update_item(
        user_id=current_user["id"],
        item_id=item_id,
        quantity=item_data.quantity
    )

@router.delete("/items/{item_id}", response_model=CartResponse)
async def remove_from_cart(
    item_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Remove item do carrinho"""
    return cart_service.remove_item(current_user["id"], item_id)

@router.post("/coupon", response_model=CartResponse)
async def apply_coupon(
    coupon_data: ApplyCouponRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Aplica cupom de desconto"""
    return cart_service.apply_coupon(current_user["id"], coupon_data.code)

@router.delete("/coupon", response_model=CartResponse)
async def remove_coupon(current_user: dict = Depends(get_current_active_user)):
    """Remove cupom do carrinho"""
    return cart_service.remove_coupon(current_user["id"])

@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(current_user: dict = Depends(get_current_active_user)):
    """Finaliza a compra"""
    return cart_service.checkout(current_user["id"])

@router.delete("/clear", response_model=CartResponse)
async def clear_cart(current_user: dict = Depends(get_current_active_user)):
    """Remove todos os itens do carrinho"""
    return cart_service.clear_cart(current_user["id"])