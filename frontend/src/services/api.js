import axios from "axios";

// Configuração base da API
const API_BASE_URL = "http://localhost:8000"; // Ajuste se seu backend estiver em outra porta

export const api = axios.create({
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

// ==================== UTILITÁRIOS ====================

// Exportar instância configurada para uso direto se necessário
export default api;
