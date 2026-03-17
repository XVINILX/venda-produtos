# backend/src/routes/cart_routes.py
from fastapi import APIRouter, HTTPException, status, Path, Body
from src.schemas.cart_schemas import (
    CartItemCreate, CartItemUpdate, CouponApply, CartResponse
)
from src.services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["Carrinho"])
cart_service = CartService()

@router.get(
    "/",
    response_model=CartResponse,
    summary="Visualizar carrinho",
    description="Retorna todos os itens do carrinho com totais calculados"
)
async def get_cart():
    """
    Retorna o carrinho atual com:
    * Lista de itens (nome, quantidade, preço unitário, subtotal)
    * Subtotal
    * Desconto (se houver cupom)
    * Total final
    """
    return cart_service.get_cart()

@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar item ao carrinho",
    description="Adiciona um produto ao carrinho. Se já existir, soma a quantidade."
)
async def add_item(item_data: CartItemCreate):
    """
    Adiciona um item ao carrinho.
    
    **Regras:**
    * Produto deve existir
    * Quantidade deve respeitar estoque
    * Se produto já estiver no carrinho, quantidades são somadas
    
    **Exemplo de body:**
    ```json
    {
        "product_id": 1,
        "quantity": 2
    }
    """
    return cart_service.add_item(
    product_id=item_data.product_id,
    quantity=item_data.quantity
    )

@router.patch(
"/items/{item_id}",
response_model=CartResponse,
summary="Atualizar quantidade",
description="Atualiza a quantidade de um item no carrinho"
)
async def update_item(
    item_id: int = Path(..., description="ID do item no carrinho"),
    item_data: CartItemUpdate = Body(...)
    ):
    """
        Atualiza a quantidade de um item.

        Se quantity = 0, remove o item

        Quantidade deve respeitar estoque disponível
        {
            "quantity": 3
        }
    """
    return cart_service.update_item(
        item_id=item_id,
        quantity=item_data.quantity
    )

@router.delete(
"/items/{item_id}",
response_model=CartResponse,
summary="Remover item",
description="Remove um item do carrinho"
)
async def remove_item(
    item_id: int = Path(..., description="ID do item no carrinho")
    ):
    """Remove um item específico do carrinho."""
    return cart_service.remove_item(item_id)

@router.post(
"/coupon",
response_model=CartResponse,
summary="Aplicar cupom",
description="Aplica um cupom de desconto ao carrinho"
)
async def apply_coupon(coupon_data: CouponApply):
    """
    Aplica um cupom de desconto.

    Regras:

    Cupom deve existir

    Cupom deve estar ativo

    Cupom não pode estar expirado

    Tipos de desconto:

    percentage: percentual do valor total

    fixed: valor fixo em reais

    Exemplo:

    json
    {
        "code": "DESCONTO10"
    }
    """
    return cart_service.apply_coupon(coupon_data.code)

@router.delete(
"/coupon",
response_model=CartResponse,
summary="Remover cupom",
description="Remove o cupom de desconto aplicado"
)
async def remove_coupon():
    """Remove o cupom atualmente aplicado ao carrinho."""
    return cart_service.remove_coupon()

@router.delete(
"/",
response_model=CartResponse,
summary="Limpar carrinho",
description="Remove todos os itens do carrinho"
)
async def clear_cart():
    """Remove todos os itens e cupons do carrinho."""
    return cart_service.clear_cart()






