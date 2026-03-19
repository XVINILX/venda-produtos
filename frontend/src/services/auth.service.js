import api from "./api";
import { getCurrentUser } from "./user.service";
/**
 * Verifica se o token atual é válido
 * @returns {Promise<boolean>} True se token válido
 */
export const checkAuth = async () => {
  const token = localStorage.getItem("auth_token");
  if (!token) return false;

  try {
    await getCurrentUser();
    return true;
  } catch (error) {
    localStorage.removeItem("auth_token");
    return false;
  }
};

/**
 * Faz logout do usuário
 */
export const logoutUser = () => {
  localStorage.removeItem("auth_token");
};

// ==================== AUTENTICAÇÃO ====================

/**
 * Registra um novo usuário
 * @param {Object} userData - Dados do usuário
 * @param {string} userData.email - Email
 * @param {string} userData.password - Senha
 * @param {string} userData.name - Nome (opcional)
 * @returns {Promise<Object>} Usuário criado
 */
export const registerUser = async (userData) => {
  try {
    const response = await api.post("/auth/register/", userData);
    return response.data;
  } catch (error) {
    console.error("Erro ao registrar usuário:", error);
    throw error;
  }
};

/**
 * Faz login do usuário
 * @param {string} email - Email
 * @param {string} password - Senha
 * @returns {Promise<Object>} Token e dados do usuário
 */
export const loginUser = async (email, password) => {
  try {
    // Tentar formato JSON primeiro
    const response = await api.post("/auth/login/", {
      email: email,
      password: password,
    });

    // Salvar token
    if (response.data.access_token) {
      localStorage.setItem("auth_token", response.data.access_token);
    }

    return response.data;
  } catch (error) {
    // Se falhar, tentar formato form-data (OAuth2)

    console.error("Erro no login:", error);
    throw error;
  }
};
