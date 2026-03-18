import api from "./api";
/**
 * Busca dados do usuário atual
 * @returns {Promise<Object>} Dados do usuário
 */
export const getCurrentUser = async () => {
  try {
    const response = await api.get("/auth/me");
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar usuário atual:", error);
    throw error;
  }
};
