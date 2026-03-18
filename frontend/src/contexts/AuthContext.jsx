// frontend/src/contexts/AuthContext.jsx
import React, { createContext, useState, useContext, useEffect } from "react";
import { loginUser, registerUser } from "../services/auth.service";
import api from "../services/api";
import { getCurrentUser } from "../services/user.service";
// Criar o contexto
const AuthContext = createContext();

// Hook personalizado para usar o contexto
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider");
  }
  return context;
};

// Provider do contexto
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Verificar se usuário está logado ao carregar a página
  useEffect(() => {
    const loadStoredAuth = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const refreshToken = localStorage.getItem("refresh_token");
        const storedUser = localStorage.getItem("user");

        if (token && storedUser) {
          // Configurar token no axios
          api.defaults.headers.common["Authorization"] = `Bearer ${token}`;

          // Verificar se token ainda é válido
          try {
            const response = await api.get("/auth/verify");
            if (response.data.authenticated) {
              setUser(JSON.parse(storedUser));
            } else {
              // Token inválido, tentar refresh
              console.log("refresh token");
            }
          } catch (error) {
            // Token expirado, tentar refresh
            console.log("refresh token");
          }
        }
      } catch (error) {
        console.error("Erro ao carregar autenticação:", error);
        logout();
      } finally {
        setLoading(false);
      }
    };

    loadStoredAuth();
  }, []);

  // Função para fazer login
  const login = async (email, password) => {
    setLoading(true);
    setError(null);

    try {
      const response = await loginUser(email, password);

      const { access_token, refresh_token } = response;

      // Salvar tokens e dados do usuário
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("refresh_token", refresh_token);

      // Configurar token no axios para próximas requisições
      api.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;

      const userData = await getCurrentUser();
      console.log(userData);
      localStorage.setItem("user", JSON.stringify(userData));
      setUser(userData);
      return { success: true };
    } catch (error) {
      console.error(error);
      const message = error.response?.data?.detail || "Erro ao fazer login";
      setError(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  // Função para registrar usuário
  const register = async (userData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await registerUser(userData);

      const { access_token, refresh_token, user: newUser } = response.data;

      // Salvar tokens e dados do usuário
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("refresh_token", refresh_token);
      localStorage.setItem("user", JSON.stringify(newUser));

      // Configurar token no axios
      api.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;

      setUser(newUser);
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || "Erro ao registrar";
      setError(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  // Função para fazer logout
  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    delete api.defaults.headers.common["Authorization"];
    setUser(null);
  };

  // Função para verificar se usuário está autenticado
  const isAuthenticated = () => {
    return !!user && !!localStorage.getItem("access_token");
  };

  // Função para obter token
  const getToken = () => {
    return localStorage.getItem("access_token");
  };

  // Valor do contexto
  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated,
    getToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
