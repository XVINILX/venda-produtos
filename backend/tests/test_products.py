# backend/tests/test_products.py
import pytest
from fastapi import status

def test_list_products(client):
    """Testa listagem de produtos"""
    response = client.get("/products/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

def test_get_product_by_id(client):
    """Testa busca de produto por ID"""
    # Primeiro pegar lista para ter um ID válido
    products = client.get("/products/").json()
    if products:
        product_id = products[0]["id"]
        response = client.get(f"/products/{product_id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == product_id

def test_get_product_not_found(client):
    """Testa produto não encontrado"""
    response = client.get("/products/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_filter_by_category(client):
    """Testa filtro por categoria"""
    # Pegar categorias disponíveis
    categories = client.get("/products/categories/").json()
    
    if categories["categories"]:
        category = categories["categories"][0]
        response = client.get(f"/products/?category={category}")
        
        assert response.status_code == status.HTTP_200_OK
        products = response.json()
        if products:
            assert products[0]["category"] == category