# backend/src/models/__init__.py
from src.models.user import User
from src.models.product import Product
from src.models.coupons import Coupon
from src.models.cart import CartItem

__all__ = ["User", "Product", "Coupon", "CartItem"]