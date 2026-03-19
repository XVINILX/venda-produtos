import pytest
from fastapi import status

def test_add_to_cart_with_fixture(auth_client, auth_client_with_products):
    """Testa adicionar item ao carrinho usando fixtures"""
    print(f"Headers: {auth_client.headers}")
    
    # Verificar se o token está presente
    assert 'authorization' in auth_client.headers, "Token não encontrado nos headers"
    print(f"Token: {auth_client.headers['authorization']}")
    
    product = auth_client_with_products["Notebook Teste"]
    print(f"Produto ID: {product['id']}")
    
    response = auth_client.post(
        "/cart/items",
        json={"product_id": product["id"], "quantity": 2}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Resposta: {response.text}")
    
    assert response.status_code == status.HTTP_200_OK

def test_add_out_of_stock_product(auth_client_with_products, auth_client):
    """Testa adicionar produto sem estoque"""
    product = auth_client_with_products["Produto Esgotado"]
    
    response = auth_client.post(
        "/cart/items",
        json={"product_id": product["id"], "quantity": 1}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Estoque insuficiente" in response.json()["detail"]

def test_add_multiple_items(auth_client_with_products, auth_client):
    """Testa adicionar múltiplos itens ao carrinho"""
    notebook = auth_client_with_products["Notebook Teste"]
    mouse = auth_client_with_products["Mouse Teste"]
    
    # Adicionar notebook
    response1 = auth_client.post(
        "/cart/items",
        json={"product_id": notebook["id"], "quantity": 1}
    )
    assert response1.status_code == 200
    
    # Adicionar mouse
    response2 = auth_client.post(
        "/cart/items",
        json={"product_id": mouse["id"], "quantity": 3}
    )
    assert response2.status_code == 200
    
    # Verificar carrinho
    cart_response = auth_client.get("/cart/")
    assert cart_response.status_code == 200
    cart_data = cart_response.json()
    assert len(cart_data["items"]) == 2
    assert cart_data["total_items"] == 4  # 1 + 3

def test_update_cart_item(auth_client_with_products, auth_client):
    """Testa atualizar quantidade de um item"""
    product = auth_client_with_products["Mouse Teste"]
    
    # Adicionar item
    add_response = auth_client.post(
        "/cart/items",
        json={"product_id": product["id"], "quantity": 2}
    )
    item_id = add_response.json()["items"][0]["id"]
    
    # Atualizar quantidade
    update_response = auth_client.patch(
        f"/cart/items/{item_id}",
        json={"quantity": 5}
    )
    
    assert update_response.status_code == 200
    updated_item = update_response.json()["items"][0]
    assert updated_item["quantity"] == 5

def test_remove_cart_item(auth_client_with_products, auth_client):
    """Testa remover item do carrinho"""
    product = auth_client_with_products["Mouse Teste"]
    
    # Adicionar item
    add_response = auth_client.post(
        "/cart/items",
        json={"product_id": product["id"], "quantity": 2}
    )
    item_id = add_response.json()["items"][0]["id"]
    
    # Remover item
    remove_response = auth_client.delete(
        f"/cart/items/{item_id}"
    )
    
    assert remove_response.status_code == 200
    assert len(remove_response.json()["items"]) == 0