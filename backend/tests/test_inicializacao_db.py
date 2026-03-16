# backend/test_sqlite.py
import sqlite3
from src.repositories.user_repository import UserRepository
from src.repositories.product_repository import ProductRepository

def test_connection():
    """Testa conexão com SQLite"""
    try:
        conn = sqlite3.connect('wisesales.db')
        print("✅ Conexão com SQLite estabelecida")
        
        # Listar tabelas
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📊 Tabelas encontradas: {[t[0] for t in tables]}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_products():
    """Testa repositório de produtos"""
    repo = ProductRepository()
    products = repo.get_products()
    print(f"📦 Produtos encontrados: {len(products)}")
    for p in products[:3]:  # Mostra apenas os primeiros 3
        print(f"  - {p['name']}: R${p['price']} (estoque: {p['stock']})")
    return products

if __name__ == "__main__":
    print("🔍 Testando configuração SQLite...")
    test_connection()
    print("\n")
    test_products()