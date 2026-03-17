# backend/src/services/product_service.py
from typing import Optional, List, Dict
from fastapi import HTTPException, status
from src.repositories.product_repository import ProductRepository
from src.schemas.product_schemas import ProductCreate, ProductUpdate

class ProductService:
    def __init__(self):
        self.product_repo = ProductRepository()
    
    def get_products(self, category: Optional[str] = None) -> List[Dict]:
        """
        Retorna lista de produtos, opcionalmente filtrados por categoria
        """
        products = self.product_repo.get_products(category)
        
        # Pode adicionar lógica de negócio aqui
        # Ex: marcar produtos com baixo estoque
        for product in products:
            if product['stock'] <= 5:
                product['low_stock'] = True
                product['stock_status'] = 'baixo'
            elif product['stock'] == 0:
                product['stock_status'] = 'esgotado'
            else:
                product['stock_status'] = 'disponível'
        
        return products
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """
        Busca um produto específico por ID
        """
        product = self.product_repo.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto com ID {product_id} não encontrado"
            )
        
        # Adicionar informações adicionais
        product['low_stock'] = product['stock'] <= 5
        product['in_stock'] = product['stock'] > 0
        
        return product
    
    def create_product(self, product_data: ProductCreate) -> Dict:
        """
        Cria um novo produto (futura funcionalidade de admin)
        """
        # Validar dados de negócio
        if product_data.price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Preço deve ser maior que zero"
            )
        
        if product_data.stock < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estoque não pode ser negativo"
            )
        
        # Aqui você implementaria a criação no banco
        # Por enquanto, retornamos um mock
        return {
            "id": 999,
            **product_data.dict(),
            "created_at": "2024-01-01T12:00:00"
        }
    
    def update_product(self, product_id: int, product_data: ProductUpdate) -> Dict:
        """
        Atualiza um produto existente
        """
        # Verificar se produto existe
        existing = self.get_product_by_id(product_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        # Validar atualizações
        update_data = product_data.dict(exclude_unset=True)
        
        if 'price' in update_data and update_data['price'] <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Preço deve ser maior que zero"
            )
        
        if 'stock' in update_data and update_data['stock'] < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estoque não pode ser negativo"
            )
        
        # Aqui você implementaria a atualização no banco
        updated = {**existing, **update_data}
        return updated
    
    def delete_product(self, product_id: int) -> bool:
        """
        Remove um produto (apenas admin)
        """
        # Verificar se produto existe
        existing = self.get_product_by_id(product_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        # Aqui você implementaria a remoção no banco
        return True
    
    def check_stock(self, product_id: int, requested_quantity: int) -> Dict:
        """
        Verifica disponibilidade de estoque
        """
        product = self.get_product_by_id(product_id)
        
        available = product['stock'] >= requested_quantity
        
        return {
            "product_id": product_id,
            "product_name": product['name'],
            "current_stock": product['stock'],
            "requested_quantity": requested_quantity,
            "available": available,
            "message": "Estoque disponível" if available else f"Estoque insuficiente. Disponível: {product['stock']}"
        }
    
    def get_categories(self) -> List[str]:
        """
        Retorna todas as categorias disponíveis
        """
        products = self.product_repo.get_products()
        categories = sorted(list(set(p['category'] for p in products)))
        return categories
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        """
        Retorna produtos de uma categoria específica
        """
        return self.product_repo.get_products(category)
    
    def search_products(self, term: str) -> List[Dict]:
        """
        Busca produtos por termo (nome ou descrição)
        """
        products = self.product_repo.get_products()
        
        # Filtrar produtos que contêm o termo no nome ou descrição
        term_lower = term.lower()
        results = [
            p for p in products
            if term_lower in p['name'].lower() 
            or (p.get('description') and term_lower in p['description'].lower())
        ]
        
        return results
    
    def get_low_stock_products(self, threshold: int = 5) -> List[Dict]:
        """
        Retorna produtos com estoque baixo (<= threshold)
        """
        products = self.product_repo.get_products()
        low_stock = [p for p in products if p['stock'] <= threshold]
        
        return low_stock
    
    def get_out_of_stock_products(self) -> List[Dict]:
        """
        Retorna produtos esgotados
        """
        products = self.product_repo.get_products()
        out_of_stock = [p for p in products if p['stock'] == 0]
        
        return out_of_stock
    
    def get_products_paginated(self, page: int = 1, per_page: int = 10, category: Optional[str] = None) -> Dict:
        """
        Retorna produtos com paginação
        """
        products = self.product_repo.get_products(category)
        
        # Calcular paginação
        start = (page - 1) * per_page
        end = start + per_page
        
        paginated = products[start:end]
        total = len(products)
        pages = (total + per_page - 1) // per_page
        
        return {
            "items": paginated,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages
        }
    
    def format_product_response(self, product: Dict) -> Dict:
        """
        Formata a resposta do produto com informações adicionais
        """
        return {
            "id": product['id'],
            "name": product['name'],
            "description": product.get('description'),
            "price": float(product['price']),
            "category": product['category'],
            "stock": product['stock'],
            "image_url": product.get('image_url'),
            "in_stock": product['stock'] > 0,
            "low_stock": product['stock'] <= 5,
            "stock_status": self._get_stock_status(product['stock'])
        }
    
    def _get_stock_status(self, stock: int) -> str:
        """Retorna status do estoque"""
        if stock == 0:
            return "esgotado"
        elif stock <= 5:
            return "baixo"
        else:
            return "disponível"
    
    def bulk_check_stock(self, items: List[Dict]) -> List[Dict]:
        """
        Verifica estoque para múltiplos itens
        """
        results = []
        for item in items:
            check = self.check_stock(item['product_id'], item['quantity'])
            results.append(check)
        
        return results