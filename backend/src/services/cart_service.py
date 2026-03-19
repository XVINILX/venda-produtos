# backend/src/services/cart_service.py
from typing import Dict, List
from fastapi import HTTPException, status
from src.repositories.cart_repository import CartRepository
from decimal import Decimal

class CartService:
    def __init__(self):
        self.cart_repo = CartRepository()
    
    def _to_float(self, value):
        """Converte Decimal para float"""
        if isinstance(value, Decimal):
            return float(value)
        return float(value) if value else 0
    
    def _get_cart_with_details(self, cart: Dict) -> Dict:
        """Obtém carrinho completo com itens e totais calculados"""
        items = self.cart_repo.get_cart_items(cart["id"])
        
        # Recalcular totais (garantir consistência)
        subtotal = cart.get("subtotal_amount", 0)
        discount = cart.get("discount_amount", 0)
        total = float(subtotal) - float(discount)

        total_quantity = 0
        for item in items:
            total_quantity += item["quantity"]

        created_at = cart.get("created_at")
        if created_at and not isinstance(created_at, str):
            created_at = created_at.isoformat() 
        
        return {
            "cart_id": cart["id"],
            "status": cart["status"],
            "items": items,
            "total_items":total_quantity,
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
            "coupon_code": cart.get("coupon_code"),
            "created_at": created_at
        }
    
    def get_cart(self, user_id: int) -> Dict:
        """Retorna o carrinho ativo do usuário"""
        # Obter ou criar carrinho
        cart = self.cart_repo.get_or_create_active_cart(user_id)
        
        # Atualizar totais
        cart = self.cart_repo.update_cart_totals(cart["id"])
        
        # Buscar itens e montar resposta
        return self._get_cart_with_details(cart)
    
    def add_item(self, user_id: int, product_id: int, quantity: int) -> Dict:
        """Adiciona item ao carrinho"""
        # Validar produto
        product = self.cart_repo.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        # Validar estoque
        if product["stock"] < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente. Disponível: {product['stock']}"
            )
        
        # Obter carrinho ativo
        cart = self.cart_repo.get_or_create_active_cart(user_id)
        
        # Verificar se produto já está no carrinho
        existing_item = self.cart_repo.get_cart_item_by_product(cart["id"], product_id)
        
        if existing_item:
            # Atualizar quantidade
            new_quantity = existing_item["quantity"] + quantity
            if product["stock"] < new_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Quantidade total excede estoque. Máximo: {product['stock']}"
                )
            self.cart_repo.update_cart_item_quantity(existing_item["id"], new_quantity)
        else:
            # Criar novo item
            self.cart_repo.add_cart_item(cart["id"], product_id, quantity)
        
        # Atualizar totais do carrinho
        self.cart_repo.update_cart_totals(cart["id"])
        
        return self.get_cart(user_id)
    
    def update_item(self, user_id: int, item_id: int, quantity: int) -> Dict:
        """Atualiza quantidade de um item"""
        # Buscar item
        item = self.cart_repo.get_cart_item(item_id, user_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item não encontrado no carrinho"
            )
        
        if quantity == 0:
            # Remover item
            self.cart_repo.remove_cart_item(item_id)
        else:
            # Validar estoque
            product = self.cart_repo.get_product_by_id(item["product_id"])
            if product["stock"] < quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estoque insuficiente. Disponível: {product['stock']}"
                )
            
            # Atualizar quantidade
            self.cart_repo.update_cart_item_quantity(item_id, quantity)
        
        # Buscar carrinho do usuário
        cart = self.cart_repo.get_active_cart_by_user(user_id)
        if cart:
            self.cart_repo.update_cart_totals(cart["id"])
        
        return self.get_cart(user_id)
    
    def remove_item(self, user_id: int, item_id: int) -> Dict:
        """Remove item do carrinho"""
        # Buscar item
        item = self.cart_repo.get_cart_item(item_id, user_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item não encontrado"
            )
        
        # Remover item
        self.cart_repo.remove_cart_item(item_id)
        
        # Atualizar totais do carrinho
        cart = self.cart_repo.get_active_cart_by_user(user_id)
        if cart:
            self.cart_repo.update_cart_totals(cart["id"])
        
        return self.get_cart(user_id)
    
    def apply_coupon(self, user_id: int, coupon_code: str) -> Dict:
        """Aplica um cupom ao carrinho"""
        # Buscar carrinho ativo
        cart = self.cart_repo.get_active_cart_by_user(user_id)
        if not cart:
            cart = self.cart_repo.get_or_create_active_cart(user_id)
        
        # Validar cupom
        coupon = self.cart_repo.get_valid_coupon(coupon_code)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cupom inválido ou expirado"
            )
        
        # Atualizar totais para ter subtotal correto
        cart = self.cart_repo.update_cart_totals(cart["id"])
        
        # Calcular desconto
        subtotal = cart["subtotal_amount"]
        if coupon["discount_type"] == 'percentage':
            discount = subtotal * (coupon["discount_value"] / 100)
        else:  # fixed
            discount = coupon["discount_value"]
        
        # Garantir que desconto não seja maior que subtotal
        discount = min(discount, subtotal)
        
        # Aplicar desconto
        self.cart_repo.update_cart_coupon(cart["id"], coupon["code"], discount)
        
        return self.get_cart(user_id)
    
    def remove_coupon(self, user_id: int) -> Dict:
        """Remove o cupom do carrinho"""
        cart = self.cart_repo.get_active_cart_by_user(user_id)
        if cart and cart.get("coupon_code"):
            self.cart_repo.update_cart_coupon(cart["id"], None, 0)
        
        return self.get_cart(user_id)
    
    def checkout(self, user_id: int) -> Dict:
        """Finaliza a compra (checkout)"""
        cart = self.cart_repo.get_active_cart_by_user(user_id)
        
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Carrinho não encontrado"
            )
        
        # Buscar itens do carrinho
        items = self.cart_repo.get_cart_items(cart["id"])
        
        if not items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Carrinho vazio"
            )
        
        # Validar estoque para cada item
        for item in items:
            product = self.cart_repo.get_product_by_id(item["product_id"])
            if product["stock"] < item["quantity"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estoque insuficiente para {item['product_name']}"
                )
        
        # Atualizar estoque
        for item in items:
            self.cart_repo.update_product_stock(item["product_id"], item["quantity"])
        
        # Finalizar carrinho
        completed = self.cart_repo.complete_cart(cart["id"])
        
        return {
            "success": True,
            "message": "Compra finalizada com sucesso!",
            "cart_id": cart["id"],
            "total": completed["final_amount"] if completed else cart["final_amount"],
            "items_count": len(items)
        }
    
    def get_cart_history(self, user_id: int) -> Dict:
        """Retorna histórico de carrinhos finalizados"""
        carts = self.cart_repo.get_user_carts_history(user_id)
        
        history = []
        for cart in carts:
            history.append({
                "cart_id": cart["id"],
                "completed_at": cart.get("completed_at"),
                "total": cart["final_amount"],
                "items_count": 0,  # Poderia buscar itens se necessário
                "coupon_code": cart.get("coupon_code")
            })
        
        return {
            "history": history,
            "total_carts": len(history)
        }
    
    def clear_cart(self, user_id: int) -> Dict:
        """Remove todos os itens do carrinho"""
        cart = self.cart_repo.get_active_cart_by_user(user_id)
        if cart:
            self.cart_repo.clear_cart_items(cart["id"])
            self.cart_repo.update_cart_totals(cart["id"])
        
        return self.get_cart(user_id)