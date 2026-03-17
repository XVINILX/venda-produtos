# backend/src/services/cart_service.py
from typing import Dict, List, Optional
from fastapi import HTTPException, status
from src.repositories.cart_repository import CartRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.coupon_repository import CouponRepository
from datetime import datetime

class CartService:
    def __init__(self):
        self.cart_repo = CartRepository()
        self.product_repo = ProductRepository()
        self.coupon_repo = CouponRepository()
        self._current_coupon = None  # Simula cupom aplicado na sessão
    
    def _calculate_totals(self, items: List[Dict]) -> Dict:
        """Calcula subtotal e aplica desconto se houver cupom"""
        subtotal = sum(item['subtotal'] for item in items)
        
        discount = 0
        if self._current_coupon:
            if self._current_coupon['discount_type'] == 'percentage':
                discount = subtotal * (self._current_coupon['discount_value'] / 100)
            else:  # fixed
                discount = self._current_coupon['discount_value']
            
            # Desconto não pode ser maior que o subtotal
            discount = min(discount, subtotal)
        
        total = subtotal - discount
        
        return {
            'items': items,
            'subtotal': round(subtotal, 2),
            'discount': round(discount, 2),
            'total': round(total, 2),
            'coupon_code': self._current_coupon['code'] if self._current_coupon else None,
            'coupon_discount': round(discount, 2) if discount > 0 else None
        }
    
    def get_cart(self) -> Dict:
        """Retorna o carrinho atual"""
        items = self.cart_repo.get_cart_items()
        return self._calculate_totals(items)
    
    def add_item(self, product_id: int, quantity: int) -> Dict:
        """Adiciona item ao carrinho"""
        # Validar produto
        product = self.product_repo.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        # Validar estoque
        if product['stock'] < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente. Disponível: {product['stock']}"
            )
        
        # Verificar se produto já está no carrinho
        existing = self.cart_repo.find_cart_item_by_product(product_id)
        
        if existing:
            # Atualizar quantidade existente
            new_quantity = existing['quantity'] + quantity
            
            # Validar estoque para a nova quantidade
            if product['stock'] < new_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Quantidade total excede estoque. Máximo: {product['stock']}"
                )
            
            self.cart_repo.update_item_quantity(existing['id'], new_quantity)
        else:
            # Adicionar novo item
            self.cart_repo.add_item(product_id, quantity)
        
        # Atualizar estoque (opcional - se quiser reservar)
        # self.product_repo.update_stock(product_id, quantity)
        
        return self.get_cart()
    
    def update_item(self, item_id: int, quantity: int) -> Dict:
        """Atualiza quantidade de um item"""
        # Buscar item atual
        item = self.cart_repo.get_cart_item(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item não encontrado no carrinho"
            )
        
        if quantity == 0:
            # Remover item
            self.cart_repo.remove_item(item_id)
        else:
            # Validar estoque
            product = self.product_repo.get_product_by_id(item['product_id'])
            if product['stock'] < quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estoque insuficiente. Disponível: {product['stock']}"
                )
            
            # Atualizar quantidade
            self.cart_repo.update_item_quantity(item_id, quantity)
        
        return self.get_cart()
    
    def remove_item(self, item_id: int) -> Dict:
        """Remove item do carrinho"""
        if not self.cart_repo.remove_item(item_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item não encontrado no carrinho"
            )
        
        return self.get_cart()
    
    def apply_coupon(self, code: str) -> Dict:
        """Aplica cupom de desconto"""
        # Validar cupom
        coupon = self.coupon_repo.validate_coupon(code)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cupom inválido ou expirado"
            )
        
        self._current_coupon = coupon
        return self.get_cart()
    
    def remove_coupon(self) -> Dict:
        """Remove cupom aplicado"""
        self._current_coupon = None
        return self.get_cart()
    
    def clear_cart(self) -> Dict:
        """Limpa todo o carrinho"""
        self.cart_repo.clear_cart()
        self._current_coupon = None
        return self.get_cart()