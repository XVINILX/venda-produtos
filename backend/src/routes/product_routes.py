# backend/src/routes/product_routes.py
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from src.services.product_service import ProductService
from src.schemas.product_schemas import ProductResponse

router = APIRouter(prefix="/products", tags=["Produtos"])
product_service = ProductService()

@router.get("/", response_model=List[ProductResponse])
async def list_products(
    category: Optional[str] = Query(None, description="Filtrar por categoria")
):
    """Lista todos os produtos disponíveis"""
    return product_service.get_products(category)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """Busca um produto específico"""
    product = product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product