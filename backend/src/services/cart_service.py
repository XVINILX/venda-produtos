# backend/src/services/cart_service.py
from typing import Dict, Optional
from src.models.coupons import Coupon
from fastapi import HTTPException, status
from src.database import SessionLocal
from src.models.cart import Cart, CartItem
from src.models.product import Product
from src.models.user import User
from decimal import Decimal
from datetime import datetime

class CartService:
    def __init__(self):
        pass
    
    def _get_or_create_active_cart(self, db, user_id: int) -> Cart:
        """Obtém ou cria um carrinho ativo para o usuário"""
        cart = db.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.status == "active"
        ).first()
        
        if not cart:
            cart = Cart(user_id=user_id, status="active")
            db.add(cart)
            db.commit()
            db.refresh(cart)
        
        return cart
    
    def _to_float(self, value):
        """Converte Decimal para float"""
        if isinstance(value, Decimal):
            return float(value)
        return float(value) if value else 0
    
    def get_cart(self, user_id: int) -> Dict:
        """Retorna o carrinho ativo do usuário"""
        db = SessionLocal()
        try:
            cart = self._get_or_create_active_cart(db, user_id)
            
            # Atualizar totais baseado nos itens atuais
            cart.update_totals()
            db.commit()
            
            items = []
            for item in cart.items:
                if item.product:
                    items.append({
                        "id": item.id,
                        "product_id": item.product_id,
                        "product_name": item.product.name,
                        "quantity": item.quantity,
                        "unit_price": self._to_float(item.product.price),
                        "subtotal": self._to_float(item.subtotal)
                    })
            
            return {
                "cart_id": cart.id,
                "status": cart.status,
                "items": items,
                "total_items": cart.total_items,
                "subtotal": self._to_float(cart.subtotal_amount),
                "discount": self._to_float(cart.discount_amount),
                "total": self._to_float(cart.final_amount),
                "coupon_code": cart.coupon_code,
                "created_at": cart.created_at.isoformat() if cart.created_at else None
            }
            
        finally:
            db.close()
    
    def add_item(self, user_id: int, product_id: int, quantity: int) -> Dict:
        """Adiciona item ao carrinho"""
        db = SessionLocal()
        try:
            # Validar produto
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produto não encontrado"
                )
            
            # Validar estoque
            if product.stock < quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estoque insuficiente. Disponível: {product.stock}"
                )
            
            # Obter carrinho ativo
            cart = self._get_or_create_active_cart(db, user_id)
            
            # Verificar se produto já está no carrinho
            existing_item = None
            for item in cart.items:
                if item.product_id == product_id:
                    existing_item = item
                    break
            
            if existing_item:
                # Atualizar quantidade
                new_quantity = existing_item.quantity + quantity
                if product.stock < new_quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Quantidade total excede estoque. Máximo: {product.stock}"
                    )
                existing_item.quantity = new_quantity
            else:
                # Criar novo item
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=product_id,
                    quantity=quantity
                )
                db.add(cart_item)
            
            # Atualizar totais do carrinho
            cart.update_totals()
            db.commit()
            
            return self.get_cart(user_id)
            
        finally:
            db.close()
    
    def update_item(self, user_id: int, item_id: int, quantity: int) -> Dict:
        """Atualiza quantidade de um item"""
        db = SessionLocal()
        try:
            # Buscar item
            item = db.query(CartItem).join(Cart).filter(
                CartItem.id == item_id,
                Cart.user_id == user_id,
                Cart.status == "active"
            ).first()
            
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item não encontrado no carrinho"
                )
            
            if quantity == 0:
                # Remover item
                db.delete(item)
            else:
                # Validar estoque
                if item.product and item.product.stock < quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Estoque insuficiente. Disponível: {item.product.stock}"
                    )
                item.quantity = quantity
            
            # Atualizar totais do carrinho
            item.cart.update_totals()
            db.commit()
            
            return self.get_cart(user_id)
            
        finally:
            db.close()
    
    def remove_item(self, user_id: int, item_id: int) -> Dict:
        """Remove item do carrinho"""
        db = SessionLocal()
        try:
            item = db.query(CartItem).join(Cart).filter(
                CartItem.id == item_id,
                Cart.user_id == user_id,
                Cart.status == "active"
            ).first()
            
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item não encontrado"
                )
            
            db.delete(item)
            
            # Atualizar totais do carrinho
            item.cart.update_totals()
            db.commit()
            
            return self.get_cart(user_id)
            
        finally:
            db.close()
    
    def apply_coupon(self, user_id: int, coupon_code: str) -> Dict:
        """Aplica um cupom ao carrinho"""
        db = SessionLocal()
        try:
            # Buscar carrinho ativo
            cart = self._get_or_create_active_cart(db, user_id)
            
            # Validar cupom
            coupon = db.query(Coupon).filter(
                Coupon.code == coupon_code.upper(),
                Coupon.active == True,
                Coupon.expires_at > datetime.now()
            ).first()
            
            if not coupon:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cupom inválido ou expirado"
                )
            
            # Calcular desconto
            cart.update_totals()  # Garantir subtotal atualizado
            
            if coupon.discount_type == 'percentage':
                discount = cart.subtotal_amount * (coupon.discount_value / Decimal('100'))
            else:  # fixed
                discount = coupon.discount_value
            
            # Aplicar desconto (não pode ser maior que subtotal)
            cart.discount_amount = min(discount, cart.subtotal_amount)
            cart.coupon_code = coupon.code
            cart.final_amount = cart.subtotal_amount - cart.discount_amount
            
            db.commit()
            
            return self.get_cart(user_id)
            
        finally:
            db.close()
    
    def remove_coupon(self, user_id: int) -> Dict:
        """Remove o cupom do carrinho"""
        db = SessionLocal()
        try:
            cart = self._get_or_create_active_cart(db, user_id)
            
            cart.coupon_code = None
            cart.discount_amount = Decimal('0')
            cart.final_amount = cart.subtotal_amount
            
            db.commit()
            
            return self.get_cart(user_id)
            
        finally:
            db.close()
    
    def checkout(self, user_id: int) -> Dict:
        """Finaliza a compra (checkout)"""
        db = SessionLocal()
        try:
            cart = db.query(Cart).filter(
                Cart.user_id == user_id,
                Cart.status == "active"
            ).first()
            
            if not cart or not cart.items:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Carrinho vazio"
                )
            
            # Validar estoque novamente
            for item in cart.items:
                if item.product and item.product.stock < item.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Estoque insuficiente para {item.product.name}"
                    )
            
            # Atualizar estoque
            for item in cart.items:
                if item.product:
                    item.product.stock -= item.quantity
            
            # Finalizar carrinho
            cart.status = "completed"
            cart.completed_at = datetime.now()
            
            db.commit()
            
            return {
                "success": True,
                "message": "Compra finalizada com sucesso!",
                "cart_id": cart.id,
                "total": self._to_float(cart.final_amount),
                "items_count": cart.total_items
            }
            
        finally:
            db.close()
    
    def get_cart_history(self, user_id: int) -> Dict:
        """Retorna histórico de carrinhos finalizados"""
        db = SessionLocal()
        try:
            carts = db.query(Cart).filter(
                Cart.user_id == user_id,
                Cart.status == "completed"
            ).order_by(Cart.completed_at.desc()).all()
            
            history = []
            for cart in carts:
                history.append({
                    "cart_id": cart.id,
                    "completed_at": cart.completed_at.isoformat() if cart.completed_at else None,
                    "total": self._to_float(cart.final_amount),
                    "items_count": cart.total_items,
                    "coupon_code": cart.coupon_code
                })
            
            return {
                "history": history,
                "total_carts": len(history)
            }
            
        finally:
            db.close()