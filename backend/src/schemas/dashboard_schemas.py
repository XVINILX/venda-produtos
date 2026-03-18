from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

class ProductSummary(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    category: str
    total_sold: Optional[int] = 0
    revenue: Optional[float] = 0

class DashboardStats(BaseModel):
    total_products: int
    total_categories: int
    total_users: int
    total_orders: int
    total_revenue: float
    products_low_stock: int
    products_out_of_stock: int
    average_order_value: float

class DailySales(BaseModel):
    date: str
    orders: int
    revenue: float

class CategorySales(BaseModel):
    category: str
    products_count: int
    total_stock: int
    total_sold: int
    revenue: float

class AdminUserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_admin: bool
    created_at: datetime

class AdminProductResponse(BaseModel):
    id: int
    name: str
    category: str
    price: float
    stock: int
    total_sold: Optional[int] = 0
    revenue: Optional[float] = 0