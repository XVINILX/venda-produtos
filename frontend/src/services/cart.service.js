// ==================== CARRINHO ====================
import api from "./api";
/**
 * Busca o carrinho atual
 * @returns {Promise<Object>} Dados do carrinho
 */
export const getCart = async () => {
  try {
    const response = await api.get("/cart");
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar carrinho:", error);
    // Retorna um carrinho vazio em caso de erro
    return {
      items: [],
      subtotal: 0,
      discount: 0,
      total: 0,
      coupon_code: null,
    };
  }
};

/**
 * Adiciona um item ao carrinho
 * @param {number} productId - ID do produto
 * @param {number} quantity - Quantidade
 * @returns {Promise<Object>} Carrinho atualizado
 */
export const addToCart = async (productId, quantity) => {
  try {
    const response = await api.post("/cart/items", {
      product_id: productId,
      quantity: quantity,
    });
    return response.data;
  } catch (error) {
    console.error("Erro ao adicionar ao carrinho:", error);
    throw error;
  }
};

/**
 * Atualiza a quantidade de um item no carrinho
 * @param {number} itemId - ID do item no carrinho
 * @param {number} quantity - Nova quantidade
 * @returns {Promise<Object>} Carrinho atualizado
 */
export const updateCartItem = async (itemId, quantity) => {
  try {
    const response = await api.patch(`/cart/items/${itemId}`, {
      quantity: quantity,
    });
    return response.data;
  } catch (error) {
    console.error("Erro ao atualizar item:", error);
    throw error;
  }
};

/**
 * Remove um item do carrinho
 * @param {number} itemId - ID do item no carrinho
 * @returns {Promise<Object>} Carrinho atualizado
 */
export const removeFromCart = async (itemId) => {
  try {
    const response = await api.delete(`/cart/items/${itemId}`);
    return response.data;
  } catch (error) {
    console.error("Erro ao remover item:", error);
    throw error;
  }
};
