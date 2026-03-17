# backend/src/schemas/product_schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ProductBase(BaseModel):
    """Schema base para produto"""
    name: str = Field(..., description="Nome do produto", min_length=3, max_length=255)
    description: Optional[str] = Field(None, description="Descrição do produto")
    price: float = Field(..., gt=0, description="Preço do produto", example=99.90)
    category: str = Field(..., description="Categoria do produto", min_length=2)
    stock: int = Field(0, ge=0, description="Quantidade em estoque")
    image_url: Optional[str] = Field(None, description="URL da imagem do produto")

class ProductCreate(ProductBase):
    """Schema para criação de produto"""
    pass

class ProductUpdate(BaseModel):
    """Schema para atualização de produto"""
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=2)
    stock: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None

class ProductResponse(ProductBase):
    """Schema para resposta com dados do produto"""
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Notebook Gamer",
                "description": "Notebook com placa RTX 3060",
                "price": 4999.99,
                "category": "eletrônicos",
                "stock": 10,
                "image_url": "https://example.com/image.jpg",
                "created_at": "2024-01-01T12:00:00"
            }
        }

class ProductListResponse(BaseModel):
    """Schema para listagem de produtos"""
    items: List[ProductResponse]
    total: int
    page: int = 1
    per_page: int = 10
    pages: int = 1
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "name": "Notebook Gamer",
                        "price": 4999.99,
                        "category": "eletrônicos",
                        "stock": 10
                    }
                ],
                "total": 1,
                "page": 1,
                "per_page": 10,
                "pages": 1
            }
        }

class ProductCategoryResponse(BaseModel):
    """Schema para categorias"""
    categories: List[str]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "categories": ["eletrônicos", "roupas", "calçados"],
                "total": 3
            }
        }

class ProductStockResponse(BaseModel):
    """Schema para verificação de estoque"""
    product_id: int
    product_name: str
    current_stock: int
    requested_quantity: int
    available: bool
    message: str