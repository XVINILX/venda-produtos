from decimal import Decimal

from sqlalchemy import Column, Integer, ForeignKey, DateTime, CheckConstraint, Boolean, String, Numeric
from sqlalchemy.sql import func
from src.database import Base
from sqlalchemy.orm import relationship

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Campos do carrinho
    status = Column(String(20), default="active", nullable=False)  # active, completed, abandoned
    coupon_code = Column(String(50), nullable=True)  # Código do cupom aplicado
    discount_amount = Column(Numeric(10, 2), default=0, nullable=False)  # Valor do desconto
    final_amount = Column(Numeric(10, 2), default=0, nullable=False)  # Valor final com desconto
    subtotal_amount = Column(Numeric(10, 2), default=0, nullable=False)  # Valor sem desconto
    
    # Datas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)  # Data de finalização
    
    # Relacionamentos
    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    @property
    def total_items(self):
        """Total de itens no carrinho"""
        return sum(item.quantity for item in self.items)
    
    @property
    def calculated_subtotal(self):
        """Calcula o subtotal baseado nos itens"""
        total = Decimal('0')
        for item in self.items:
            if item.product:
                total += Decimal(str(item.quantity)) * item.product.price
        return total
    
    def update_totals(self):
        """Atualiza os valores totais do carrinho"""
        self.subtotal_amount = self.calculated_subtotal
        self.final_amount = self.subtotal_amount - self.discount_amount
        if self.final_amount < 0:
            self.final_amount = Decimal('0')

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
    )
    
    @property
    def subtotal(self):
        """Subtotal do item"""
        if self.product:
            return Decimal(str(self.quantity)) * self.product.price
        return Decimal('0')