// ==================== CUPONS ====================
import api from "./api";
/**
 * Aplica um cupom de desconto ao carrinho
 * @param {string} code - Código do cupom
 * @returns {Promise<Object>} Carrinho com desconto aplicado
 */
export const applyCoupon = async (code) => {
  try {
    const response = await api.post("/cart/coupon", {
      code: code,
    });
    return response.data;
  } catch (error) {
    console.error("Erro ao aplicar cupom:", error);
    throw error;
  }
};

/**
 * Remove o cupom do carrinho
 * @returns {Promise<Object>} Carrinho sem cupom
 */
export const removeCoupon = async () => {
  try {
    const response = await api.delete("/cart/coupon");
    return response.data;
  } catch (error) {
    console.error("Erro ao remover cupom:", error);
    throw error;
  }
};
