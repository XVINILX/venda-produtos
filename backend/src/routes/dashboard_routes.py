from fastapi import APIRouter, Depends, Query, Path
from typing import List, Optional
from src.services.admin_service import AdminService
from src.auth.dependencies import get_current_admin
from src.schemas.dashboard_schemas import (
    DashboardStats, AdminProductResponse, AdminUserResponse,
    DailySales, CategorySales
)

router = APIRouter(prefix="/admin", tags=["Admin"])
admin_service = AdminService()

@router.get(
    "/dashboard",
    response_model=DashboardStats,
    summary="Estatísticas do Dashboard"
)
async def get_dashboard_stats(admin: dict = Depends(get_current_admin)):
    """Retorna estatísticas gerais para o dashboard administrativo"""
    return admin_service.get_dashboard_stats()

@router.get(
    "/products",
    response_model=List[AdminProductResponse],
    summary="Listar produtos com dados de venda"
)
async def get_products_with_sales(admin: dict = Depends(get_current_admin)):
    """Retorna todos os produtos com informações de vendas"""
    return admin_service.get_products_with_sales()

@router.get(
    "/products/low-stock",
    response_model=List[AdminProductResponse],
    summary="Produtos com estoque baixo"
)
async def get_low_stock_products(
    threshold: int = Query(5, ge=1),
    admin: dict = Depends(get_current_admin)
):
    """Retorna produtos com estoque baixo (<= threshold)"""
    return admin_service.get_low_stock_products(threshold)

@router.get(
    "/products/top-selling",
    response_model=List[AdminProductResponse],
    summary="Produtos mais vendidos"
)
async def get_top_selling_products(
    limit: int = Query(5, ge=1, le=20),
    admin: dict = Depends(get_current_admin)
):
    """Retorna os produtos mais vendidos"""
    return admin_service.get_top_selling_products(limit)

@router.get(
    "/sales/daily",
    response_model=List[DailySales],
    summary="Vendas diárias"
)
async def get_daily_sales(
    days: int = Query(7, ge=1, le=30),
    admin: dict = Depends(get_current_admin)
):
    """Retorna vendas dos últimos X dias"""
    return admin_service.get_daily_sales(days)

@router.get(
    "/sales/by-category",
    response_model=List[CategorySales],
    summary="Vendas por categoria"
)
async def get_sales_by_category(admin: dict = Depends(get_current_admin)):
    """Retorna vendas agrupadas por categoria"""
    return admin_service.get_sales_by_category()

@router.get(
    "/users",
    response_model=List[AdminUserResponse],
    summary="Listar todos os usuários"
)
async def get_all_users(admin: dict = Depends(get_current_admin)):
    """Retorna todos os usuários cadastrados"""
    return admin_service.get_all_users()

@router.patch(
    "/products/{product_id}/stock",
    response_model=AdminProductResponse,
    summary="Atualizar estoque"
)
async def update_product_stock(
    product_id: int = Path(..., gt=0),
    new_stock: int = Query(..., ge=0),
    admin: dict = Depends(get_current_admin)
):
    """Atualiza o estoque de um produto"""
    return admin_service.update_product_stock(product_id, new_stock)