# backend/src/routes/coupon_routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from src.services.coupon_service import CouponService
from src.schemas.coupon_schemas import (
    CouponCreate, CouponUpdate, CouponResponse, CouponListResponse
)
from src.auth.dependencies import get_current_admin, get_current_user

router = APIRouter(prefix="/coupons", tags=["Cupons"])
coupon_service = CouponService()

# ==================== ENDPOINTS PÚBLICOS ====================

@router.get("/validate/{code}")
async def validate_coupon(
    code: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Valida se um cupom é válido (público, mas requer login)
    Útil para o frontend verificar cupons antes de aplicar
    """
    coupon = coupon_service.validate_coupon(code)
    return {
        "valid": True,
        "code": coupon["code"],
        "discount_type": coupon["discount_type"],
        "discount_value": coupon["discount_value"]
    }

# ==================== ENDPOINTS DE ADMIN ====================

@router.post(
    "/",
    response_model=CouponResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo cupom (admin)"
)
async def create_coupon(
    coupon_data: CouponCreate,
    admin: dict = Depends(get_current_admin)
):
    """
    Cria um novo cupom de desconto.
    
    **Requer privilégios de administrador.**
    
    - **code**: Código único do cupom (ex: PROMO10)
    - **discount_type**: 'percentage' ou 'fixed'
    - **discount_value**: Valor do desconto
    - **active**: Se está ativo (padrão: true)
    - **expires_at**: Data de expiração
    """
    return coupon_service.create_coupon(coupon_data)

@router.get(
    "/",
    response_model=List[CouponResponse],
    summary="Listar todos os cupons (admin)"
)
async def list_coupons(
    admin: dict = Depends(get_current_admin)
):
    """Lista todos os cupons cadastrados"""
    return coupon_service.get_all_coupons()

@router.get(
    "/stats",
    summary="Estatísticas de cupons (admin)"
)
async def get_coupon_stats(
    admin: dict = Depends(get_current_admin)
):
    """Retorna estatísticas sobre os cupons"""
    return coupon_service.get_coupon_stats()

@router.get(
    "/active",
    response_model=List[CouponResponse],
    summary="Listar cupons ativos (admin)"
)
async def list_active_coupons(
    admin: dict = Depends(get_current_admin)
):
    """Lista apenas cupons ativos e não expirados"""
    return coupon_service.get_active_coupons()

@router.get(
    "/expired",
    response_model=List[CouponResponse],
    summary="Listar cupons expirados (admin)"
)
async def list_expired_coupons(
    admin: dict = Depends(get_current_admin)
):
    """Lista cupons expirados"""
    return coupon_service.get_expired_coupons()

@router.get(
    "/{coupon_id}",
    response_model=CouponResponse,
    summary="Buscar cupom por ID (admin)"
)
async def get_coupon(
    coupon_id: int,
    admin: dict = Depends(get_current_admin)
):
    """Busca um cupom específico pelo ID"""
    return coupon_service.get_coupon(coupon_id)

@router.get(
    "/code/{code}",
    response_model=CouponResponse,
    summary="Buscar cupom por código (admin)"
)
async def get_coupon_by_code(
    code: str,
    admin: dict = Depends(get_current_admin)
):
    """Busca um cupom específico pelo código"""
    return coupon_service.get_coupon_by_code(code)

@router.patch(
    "/{coupon_id}",
    response_model=CouponResponse,
    summary="Atualizar cupom (admin)"
)
async def update_coupon(
    coupon_id: int,
    update_data: CouponUpdate,
    admin: dict = Depends(get_current_admin)
):
    """Atualiza um cupom existente"""
    return coupon_service.update_coupon(coupon_id, update_data)

@router.put(
    "/{coupon_id}/activate",
    response_model=CouponResponse,
    summary="Ativar cupom (admin)"
)
async def activate_coupon(
    coupon_id: int,
    admin: dict = Depends(get_current_admin)
):
    """Ativa um cupom"""
    return coupon_service.activate_coupon(coupon_id)

@router.put(
    "/{coupon_id}/deactivate",
    response_model=CouponResponse,
    summary="Desativar cupom (admin)"
)
async def deactivate_coupon(
    coupon_id: int,
    admin: dict = Depends(get_current_admin)
):
    """Desativa um cupom"""
    return coupon_service.deactivate_coupon(coupon_id)

@router.delete(
    "/{coupon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover cupom (admin)"
)
async def delete_coupon(
    coupon_id: int,
    admin: dict = Depends(get_current_admin)
):
    """Remove um cupom do sistema"""
    coupon_service.delete_coupon(coupon_id)
    return None

# ==================== ENDPOINTS EM MASSA ====================

@router.post(
    "/bulk",
    response_model=List[CouponResponse],
    summary="Criar múltiplos cupons (admin)"
)
async def create_coupons_bulk(
    coupons: List[CouponCreate],
    admin: dict = Depends(get_current_admin)
):
    """Cria múltiplos cupons de uma vez"""
    created = []
    errors = []
    
    for coupon_data in coupons:
        try:
            created.append(coupon_service.create_coupon(coupon_data))
        except HTTPException as e:
            errors.append({
                "code": coupon_data.code,
                "error": e.detail
            })
    
    return {
        "created": created,
        "errors": errors,
        "total_created": len(created),
        "total_errors": len(errors)
    }