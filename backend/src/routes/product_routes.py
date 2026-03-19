from src.auth.dependencies import get_current_admin
from fastapi import APIRouter, Query, HTTPException, status, Depends
from typing import Optional, List
from src.services.product_service import ProductService
from src.schemas.product_schemas import CategoriesResponse, ProductCreate, ProductResponse, ProductUpdate

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

@router.get("/categories/", response_model=CategoriesResponse)
async def get_categories():
    """Busca lista de categorias específico"""
    product = product_service.get_categories()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product


@router.post(
    "/", 
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo produto (admin)"
)
async def create_product(
    product_data: ProductCreate,
    admin: dict = Depends(get_current_admin)  # Apenas admin pode criar
):
    """
    Cria um novo produto.
    
    **Requer privilégios de administrador.**
    
    - **name**: Nome do produto (obrigatório)
    - **price**: Preço (obrigatório, > 0)
    - **category**: Categoria (obrigatório)
    - **stock**: Estoque inicial (obrigatório, >= 0)
    - **image_url**: URL da imagem (opcional)
    """
    return product_service.create_product(product_data)

@router.patch(
    "/{product_id}", 
    response_model=ProductResponse,
    summary="Atualizar produto (admin)"
)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    admin: dict = Depends(get_current_admin)  # Apenas admin pode atualizar
):
    """
    Atualiza um produto existente.
    
    **Requer privilégios de administrador.**
    
    Todos os campos são opcionais. Apenas os campos enviados serão atualizados.
    """
    return product_service.update_product(product_id, product_data)

@router.put(
    "/{product_id}", 
    response_model=ProductResponse,
    summary="Substituir produto completamente (admin)"
)
async def replace_product(
    product_id: int,
    product_data: ProductCreate,
    admin: dict = Depends(get_current_admin)
):
    """
    Substitui completamente um produto existente.
    
    **Requer privilégios de administrador.**
    
    Diferente do PATCH, este endpoint requer todos os campos.
    """
    return product_service.replace_product(product_id, product_data)

@router.delete(
    "/{product_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover produto (admin)"
)
async def delete_product(
    product_id: int,
    admin: dict = Depends(get_current_admin)  # Apenas admin pode deletar
):
    """
    Remove um produto do catálogo.
    
    **Requer privilégios de administrador.**
    """
    product_service.delete_product(product_id)
    return None