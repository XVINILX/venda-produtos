import pytest
from fastapi import status

def test_apply_percentage_coupon_success(auth_client, test_coupon_percentage):
    """
    Cenário: Aplicar cupom percentual com sucesso
    - Cupom válido e ativo
    - Carrinho com itens
    - Deve aplicar desconto percentual corretamente
    """
    # Arrange: Carrinho já tem itens (preparado pela fixture)
    subtotal_original = auth_client.get("/cart/").json()["subtotal"]
    
    # Act: Aplicar cupom
    response = auth_client.post(
        "/cart/coupon",
        json={"code": test_coupon_percentage["code"]}
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verificar desconto (10% do subtotal)
    desconto_esperado = subtotal_original * 0.10
    assert data["discount"] == pytest.approx(desconto_esperado)
    assert data["total"] == pytest.approx(subtotal_original - desconto_esperado)
    assert data["coupon_code"] == test_coupon_percentage["code"]
    
    # Verificar se o cupom está registrado no carrinho
    cart_response = auth_client.get("/cart/")
    assert cart_response.json()["coupon_code"] == test_coupon_percentage["code"]

def test_apply_fixed_coupon_success(auth_client, test_coupon_fixed, cart_with_items):
    """
    Cenário: Aplicar cupom de valor fixo com sucesso
    - Cupom válido e ativo
    - Carrinho com itens
    - Deve aplicar desconto fixo corretamente
    """
    # Arrange
    subtotal_original = auth_client.get("/cart/").json()["subtotal"]
    valor_fixo = 15.00  # Do cupom VALE15
    
    # Act
    response = auth_client.post(
        "/cart/coupon",
        json={"code": test_coupon_fixed["code"]}
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["discount"] == valor_fixo
    assert data["total"] == subtotal_original - valor_fixo
    assert data["coupon_code"] == test_coupon_fixed["code"]

def test_apply_coupon_to_empty_cart(auth_client, test_coupon_percentage):
    """
    Cenário: Aplicar cupom em carrinho vazio
    - Carrinho sem itens
    - Cupom válido
    - Deve aplicar normalmente (desconto 0)
    """
    # Act
    response = auth_client.post(
        "/cart/coupon",
        json={"code": test_coupon_percentage["code"]}
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["items"] == []
    assert data["subtotal"] == 0
    assert data["discount"] == 0
    assert data["total"] == 0
    assert data["coupon_code"] == test_coupon_percentage["code"]

def test_apply_invalid_coupon(auth_client):
    """
    Cenário: Aplicar cupom inexistente
    - Código de cupom que não existe no banco
    - Deve retornar erro 400
    """
    # Act
    response = auth_client.post(
        "/cart/coupon",
        json={"code": "CUPOM_INEXISTENTE"}
    )
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "inválido" in data["detail"].lower() or "expirado" in data["detail"].lower()


def test_apply_inactive_coupon(auth_client, test_coupon_inactive):
    """
    Cenário: Aplicar cupom inativo
    - Cupom com active = false
    - Deve retornar erro 400
    """
    # Act
    response = auth_client.post(
        "/cart/coupon",
        json={"code": test_coupon_inactive["code"]}
    )
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "inválido" in data["detail"].lower()

def test_apply_coupon_twice(auth_client, test_coupon_percentage):
    """
    Cenário: Aplicar cupom duas vezes
    - Primeira aplicação deve funcionar
    - Segunda aplicação deve substituir o primeiro cupom
    """
    # Act 1: Aplicar primeiro cupom
    response1 = auth_client.post(
        "/cart/coupon",
        json={"code": test_coupon_percentage["code"]}
    )
    assert response1.status_code == status.HTTP_200_OK
    data1 = response1.json()
    
    # Act 2: Aplicar segundo cupom (pode ser o mesmo ou outro)
    response2 = auth_client.post(
        "/cart/coupon",
        json={"code": test_coupon_percentage["code"]}
    )
    
    # Assert
    assert response2.status_code == status.HTTP_200_OK
    data2 = response2.json()
    
    # Deve ter o mesmo desconto (aplicado novamente)
    assert data2["coupon_code"] == test_coupon_percentage["code"]
    assert data2["discount"] == data1["discount"]


def test_apply_coupon_with_zero_subtotal(auth_client, test_coupon_percentage):
    """
    Cenário: Aplicar cupom com subtotal zero
    - Carrinho vazio
    - Desconto deve ser zero
    """
    # Act
    response = auth_client.post(
        "/cart/coupon",
        json={"code": test_coupon_percentage["code"]}
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["discount"] == 0
    assert data["total"] == 0
    assert data["coupon_code"] == test_coupon_percentage["code"]

def test_remove_coupon_after_applying(auth_client, test_coupon_percentage):
    """
    Cenário: Remover cupom após aplicar
    - Aplicar cupom
    - Remover cupom
    - Carrinho deve voltar ao estado original
    """
    # Arrange: Aplicar cupom
    apply_response = auth_client.post(
        "/cart/coupon",
        json={"code": test_coupon_percentage["code"]}
    )
    assert apply_response.status_code == status.HTTP_200_OK
    cart_com_cupom = apply_response.json()
    
    # Act: Remover cupom
    remove_response = auth_client.delete("/cart/coupon")
    
    # Assert
    assert remove_response.status_code == status.HTTP_200_OK
    cart_sem_cupom = remove_response.json()
    
    assert cart_sem_cupom["coupon_code"] is None
    assert cart_sem_cupom["discount"] == 0
    assert cart_sem_cupom["total"] == cart_com_cupom["subtotal"]

def test_apply_coupon_unauthenticated(client, test_coupon_percentage):
    """
    Cenário: Aplicar cupom sem estar autenticado
    - Usuário não logado
    - Deve retornar erro 401
    """
    # Act
    client.headers.clear()
    response = client.post(
        "/cart/coupon",
        json={"code": test_coupon_percentage["code"]}
    )
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_apply_coupon_with_invalid_code_format(auth_client):
    """
    Cenário: Aplicar cupom com formato inválido
    - Código vazio, muito longo, etc.
    """
    # Teste com código vazio
    response1 = auth_client.post(
        "/cart/coupon",
        json={"code": ""}
    )
    assert response1.status_code == status.HTTP_400_BAD_REQUEST
    
    # Teste com código muito longo (assumindo limite de 50 caracteres)
    response2 = auth_client.post(
        "/cart/coupon",
        json={"code": "A" * 100}
    )
    assert response2.status_code == status.HTTP_400_BAD_REQUEST

