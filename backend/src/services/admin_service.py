# backend/src/services/admin_service.py
from typing import Dict, List
from fastapi import HTTPException, status
from src.repositories.product_repository import ProductRepository
from src.repositories.user_repository import UserRepository
from src.repositories.cart_repository import CartRepository
from src.repositories.coupon_repository import CouponRepository
from datetime import datetime, timedelta

class AdminService:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.user_repo = UserRepository()
        self.cart_repo = CartRepository()
        self.coupon_repo = CouponRepository()
    
    def get_dashboard_stats(self) -> Dict:
        """Retorna estatísticas gerais do dashboard"""
        
        # Produtos
        products = self.product_repo.get_products()
        total_products = len(products)
        products_low_stock = len([p for p in products if 0 < p['stock'] <= 5])
        products_out_of_stock = len([p for p in products if p['stock'] == 0])
        
        # Categorias únicas
        categories = len(set(p['category'] for p in products))
        
        # Usuários
        users = self.user_repo.get_all()
        total_users = len(users)
        
        # Itens do carrinho (simulando vendas)
        cart_items = self.cart_repo.get_cart_items_admin()
        
        # Calcular receita total (considerando todos os itens como vendidos)
        total_revenue = sum(item['subtotal'] for item in cart_items)
        total_orders = len(set(item['id'] for item in cart_items))  # Simplificado
        
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        return {
            "total_products": total_products,
            "total_categories": categories,
            "total_users": total_users,
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "products_low_stock": products_low_stock,
            "products_out_of_stock": products_out_of_stock,
            "average_order_value": round(avg_order_value, 2)
        }
    
    def get_products_with_sales(self) -> List[Dict]:
        """Retorna produtos com dados de venda"""
        products = self.product_repo.get_products()
        cart_items = self.cart_repo.get_cart_items_admin()
            
        result = []
        for product in products:
            # Calcular vendas deste produto
            sold = sum(item['quantity'] for item in cart_items if item['product_id'] == product['id'])
            revenue = sum(item['subtotal'] for item in cart_items if item['product_id'] == product['id'])
            
            result.append({
                **product,
                "total_sold": sold,
                "revenue": round(revenue, 2)
            })
        
        return sorted(result, key=lambda x: x['revenue'], reverse=True)
    
    def get_sales_by_category(self) -> List[Dict]:
        """Retorna vendas agrupadas por categoria"""
        products = self.product_repo.get_products()
        cart_items = self.cart_repo.get_cart_items_admin()
        
        # Agrupar por categoria
        categories = {}
        for product in products:
            cat = product['category']
            if cat not in categories:
                categories[cat] = {
                    "category": cat,
                    "products_count": 0,
                    "total_stock": 0,
                    "total_sold": 0,
                    "revenue": 0
                }
            
            categories[cat]["products_count"] += 1
            categories[cat]["total_stock"] += product['stock']
            
            # Calcular vendas
            sold = sum(item['quantity'] for item in cart_items if item['product_id'] == product['id'])
            revenue = sum(item['subtotal'] for item in cart_items if item['product_id'] == product['id'])
            
            categories[cat]["total_sold"] += sold
            categories[cat]["revenue"] += revenue
        
        return list(categories.values())
    
    def get_daily_sales(self, days: int = 7) -> List[Dict]:
        """Retorna vendas diárias dos últimos X dias"""
        cart_items = self.cart_repo.get_cart_items_admin()
        
        # Agrupar por dia (simplificado - assumindo que todos os itens foram criados hoje)
        today = datetime.now().date()
        daily = []
        
        for i in range(days):
            date = today - timedelta(days=i)
            # Simular dados para demonstração
            # Em produção, você agruparia por data real
            daily.append({
                "date": date.strftime("%Y-%m-%d"),
                "orders": len(cart_items) // days + (i % 3),
                "revenue": round(sum(item['subtotal'] for item in cart_items) / days * (1 + i * 0.1), 2)
            })
        
        return sorted(daily, key=lambda x: x['date'])
    
    def get_all_users(self) -> List[Dict]:
        """Retorna todos os usuários (apenas admin)"""
        return self.user_repo.get_all()
    
    def get_low_stock_products(self, threshold: int = 5) -> List[Dict]:
        """Retorna produtos com estoque baixo"""
        products = self.product_repo.get_products()
        low_stock = [p for p in products if 0 < p['stock'] <= threshold]
        return sorted(low_stock, key=lambda x: x['stock'])
    
    def update_product_stock(self, product_id: int, new_stock: int) -> Dict:
        """Atualiza estoque de um produto"""
        if new_stock < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estoque não pode ser negativo"
            )
        
        # Buscar produto
        product = self.product_repo.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        # Atualizar (você precisará implementar este método no repositório)
        product = self.product_repo.set_stock(product_id, new_stock)
        product = self.product_repo.get_product_by_id(product_id)
        
        return {**product}
    
    def get_top_selling_products(self, limit: int = 5) -> List[Dict]:
        """Retorna os produtos mais vendidos"""
        products_with_sales = self.get_products_with_sales()
        return sorted(products_with_sales, key=lambda x: x['total_sold'], reverse=True)[:limit]