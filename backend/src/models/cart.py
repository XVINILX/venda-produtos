from sqlalchemy import Column, Integer, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.sql import func
from src.database import Base

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
    )