import axios from "axios";

// Configuração base da API
const API_BASE_URL = "http://localhost:8000"; // Ajuste se seu backend estiver em outra porta

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10 segundos de timeout
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor para adicionar token de autenticação (quando implementado)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Interceptor para tratar erros globalmente
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === "ECONNABORTED") {
      console.error("Timeout da requisição");
      throw new Error("O servidor demorou muito para responder");
    }

    if (!error.response) {
      console.error("Erro de rede - servidor offline?");
      throw new Error("Não foi possível conectar ao servidor");
    }

    // Tratar erros comuns
    switch (error.response.status) {
      case 401:
        console.error("Não autorizado");
        // Redirecionar para login se necessário
        break;
      case 404:
        console.error("Recurso não encontrado");
        break;
      case 500:
        console.error("Erro interno do servidor");
        break;
      default:
        console.error(`Erro ${error.response.status}:`, error.response.data);
    }

    return Promise.reject(error);
  },
);

// ==================== PRODUTOS ====================

/**
 * Busca todos os produtos
 * @param {string} category - Categoria para filtrar (opcional)
 * @returns {Promise<Array>} Lista de produtos
 */
export const getProducts = async (category = null) => {
  try {
    const url = category
      ? `/products?category=${encodeURIComponent(category)}`
      : "/products";
    const response = await api.get(url);

    // A API pode retornar diferentes formatos
    if (response.data.items) {
      return response.data; // Formato { items: [], total: X }
    }
    return { items: response.data, total: response.data.length }; // Formato array simples
  } catch (error) {
    console.error("Erro ao buscar produtos:", error);
    throw error;
  }
};

/**
 * Busca um produto específico por ID
 * @param {number} id - ID do produto
 * @returns {Promise<Object>} Dados do produto
 */
export const getProductById = async (id) => {
  try {
    const response = await api.get(`/products/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Erro ao buscar produto ${id}:`, error);
    throw error;
  }
};

// ==================== CARRINHO ====================

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

// ==================== CUPONS ====================

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
    const response = await api.post("/auth/register", userData);
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
    const response = await api.post("/auth/login/json", {
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
    if (error.response?.status === 404) {
      try {
        const formData = new FormData();
        formData.append("username", email);
        formData.append("password", password);

        const response = await api.post("/auth/login", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        if (response.data.access_token) {
          localStorage.setItem("auth_token", response.data.access_token);
        }

        return response.data;
      } catch (secondError) {
        console.error("Erro no login:", secondError);
        throw secondError;
      }
    }

    console.error("Erro no login:", error);
    throw error;
  }
};

/**
 * Faz logout do usuário
 */
export const logoutUser = () => {
  localStorage.removeItem("auth_token");
};

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

// ==================== CATEGORIAS ====================

/**
 * Busca todas as categorias disponíveis
 * @returns {Promise<Array>} Lista de categorias
 */
export const getCategories = async () => {
  try {
    // Primeiro tenta endpoint específico de categorias
    const response = await api.get("/products/categories");
    return response.data.categories || [];
  } catch (error) {
    // Se não existir, extrai dos produtos
    try {
      const products = await getProducts();
      const categories = [...new Set(products.items.map((p) => p.category))];
      return categories;
    } catch (secondError) {
      console.error("Erro ao buscar categorias:", secondError);
      return [];
    }
  }
};

// ==================== UTILITÁRIOS ====================

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

// Exportar instância configurada para uso direto se necessário
export default api;
