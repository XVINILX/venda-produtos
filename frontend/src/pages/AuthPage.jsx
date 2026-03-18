// frontend/src/pages/AuthPage.jsx
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, AlertCircle, Mail, Lock, User } from "lucide-react";
import "./AuthPage.css";
import { registerUser, loginUser } from "../services/auth.service";
import { useAuth } from "../contexts/AuthContext";

const AuthPage = () => {
  const navigate = useNavigate();

  const { isAuthenticated, login, logout, register } = useAuth();
  const [activeTab, setActiveTab] = useState("login");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [rememberMe, setRememberMe] = useState(false);

  // Estados para os formulários
  const [loginData, setLoginData] = useState({
    email: "",
    password: "",
  });

  const [registerData, setRegisterData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  // Validação de senha em tempo real
  const getPasswordStrength = (password) => {
    if (!password) return null;

    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;

    if (strength <= 1) return { level: "weak", text: "Fraca" };
    if (strength <= 2) return { level: "medium", text: "Média" };
    return { level: "strong", text: "Forte" };
  };

  const passwordStrength = getPasswordStrength(registerData.password);

  const validateRegister = () => {
    const newErrors = {};

    if (!registerData.name.trim()) {
      newErrors.name = "Nome é obrigatório";
    } else if (registerData.name.length < 3) {
      newErrors.name = "Nome deve ter pelo menos 3 caracteres";
    }

    if (!registerData.email) {
      newErrors.email = "Email é obrigatório";
    } else if (!/\S+@\S+\.\S+/.test(registerData.email)) {
      newErrors.email = "Email inválido";
    }

    if (!registerData.password) {
      newErrors.password = "Senha é obrigatória";
    } else if (registerData.password.length < 6) {
      newErrors.password = "Senha deve ter pelo menos 6 caracteres";
    }

    if (registerData.password !== registerData.confirmPassword) {
      newErrors.confirmPassword = "As senhas não conferem";
    }

    return newErrors;
  };

  const validateLogin = () => {
    const newErrors = {};

    if (!loginData.email) {
      newErrors.email = "Email é obrigatório";
    } else if (!/\S+@\S+\.\S+/.test(loginData.email)) {
      newErrors.email = "Email inválido";
    }

    if (!loginData.password) {
      newErrors.password = "Senha é obrigatória";
    }

    return newErrors;
  };

  const handleLogin = async (e) => {
    e.preventDefault();

    const validationErrors = validateLogin();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      // Simular chamada API

      // Aqui você faria a chamada real:
      // const response = await api.post('/auth/login', loginData);
      const response = await login(loginData.email, loginData.password);
      console.log("Login:", loginData);

      // Salvar token se "lembrar-me" estiver marcado
      if (rememberMe) {
        localStorage.setItem("rememberedEmail", loginData.email);
      }

      // Redirecionar para a página inicial
      navigate("/");
    } catch (error) {
      setErrors({
        general: error.response?.data?.detail || "Erro ao fazer login",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();

    const validationErrors = validateRegister();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      // Simular chamada API

      // Aqui você faria a chamada real:
      const response = await register(registerData);

      console.log("Registro:", registerData);

      // Mostrar mensagem de sucesso e mudar para login
      alert("Conta criada com sucesso! Faça login para continuar.");
      setActiveTab("login");
    } catch (error) {
      setErrors({
        general: error.response?.data?.detail || "Erro ao criar conta",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSocialLogin = (provider) => {
    console.log(`Login com ${provider}`);
    // Implementar lógica de login social
  };

  // Carregar email salvo
  React.useEffect(() => {
    const rememberedEmail = localStorage.getItem("rememberedEmail");
    if (rememberedEmail) {
      setLoginData((prev) => ({ ...prev, email: rememberedEmail }));
      setRememberMe(true);
    }
  }, []);

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-tabs">
          <button
            className={`auth-tab ${activeTab === "login" ? "active" : ""}`}
            onClick={() => setActiveTab("login")}
          >
            Login
          </button>
          <button
            className={`auth-tab ${activeTab === "register" ? "active" : ""}`}
            onClick={() => setActiveTab("register")}
          >
            Criar Conta
          </button>
        </div>

        {activeTab === "login" ? (
          // FORMULÁRIO DE LOGIN
          <form onSubmit={handleLogin} className="auth-form">
            <div className="auth-title">
              <h2>Bem-vindo de volta!</h2>
              <p>
                Novo por aqui?{" "}
                <a onClick={() => setActiveTab("register")}>Crie uma conta</a>
              </p>
            </div>

            {errors.general && (
              <div className="error-message" style={{ marginBottom: "1rem" }}>
                <AlertCircle size={16} />
                {errors.general}
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Email</label>
              <div className="password-input-wrapper">
                <Mail
                  size={20}
                  style={{
                    position: "absolute",
                    left: "1rem",
                    top: "50%",
                    transform: "translateY(-50%)",
                    color: "#9ca3af",
                  }}
                />
                <input
                  type="email"
                  className={`form-input ${errors.email ? "error" : ""}`}
                  style={{ paddingLeft: "3rem" }}
                  placeholder="seu@email.com"
                  value={loginData.email}
                  onChange={(e) =>
                    setLoginData({ ...loginData, email: e.target.value })
                  }
                />
              </div>
              {errors.email && (
                <div className="error-message">
                  <AlertCircle size={14} />
                  {errors.email}
                </div>
              )}
            </div>

            <div className="form-group">
              <label className="form-label">Senha</label>
              <div className="password-input-wrapper">
                <Lock
                  size={20}
                  style={{
                    position: "absolute",
                    left: "1rem",
                    top: "50%",
                    transform: "translateY(-50%)",
                    color: "#9ca3af",
                    zIndex: 1,
                  }}
                />
                <input
                  type={showPassword ? "text" : "password"}
                  className={`form-input ${errors.password ? "error" : ""}`}
                  style={{ paddingLeft: "3rem", paddingRight: "3rem" }}
                  placeholder="••••••••"
                  value={loginData.password}
                  onChange={(e) =>
                    setLoginData({ ...loginData, password: e.target.value })
                  }
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {errors.password && (
                <div className="error-message">
                  <AlertCircle size={14} />
                  {errors.password}
                </div>
              )}
            </div>

            <div className="form-options">
              <label className="remember-me">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                <span>Lembrar-me</span>
              </label>
              <a href="/forgot-password" className="forgot-password">
                Esqueceu a senha?
              </a>
            </div>

            <button
              type="submit"
              className={`auth-button ${loading ? "loading" : ""}`}
              disabled={loading}
            >
              {loading ? <span className="spinner"></span> : "Entrar"}
            </button>
          </form>
        ) : (
          // FORMULÁRIO DE REGISTRO
          <form onSubmit={handleRegister} className="auth-form">
            <div className="auth-title">
              <h2>Criar nova conta</h2>
              <p>
                Já tem uma conta?{" "}
                <a onClick={() => setActiveTab("login")}>Faça login</a>
              </p>
            </div>

            {errors.general && (
              <div className="error-message" style={{ marginBottom: "1rem" }}>
                <AlertCircle size={16} />
                {errors.general}
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Nome completo</label>
              <div className="password-input-wrapper">
                <User
                  size={20}
                  style={{
                    position: "absolute",
                    left: "1rem",
                    top: "50%",
                    transform: "translateY(-50%)",
                    color: "#9ca3af",
                  }}
                />
                <input
                  type="text"
                  className={`form-input ${errors.name ? "error" : ""}`}
                  style={{ paddingLeft: "3rem" }}
                  placeholder="João Silva"
                  value={registerData.name}
                  onChange={(e) =>
                    setRegisterData({ ...registerData, name: e.target.value })
                  }
                />
              </div>
              {errors.name && (
                <div className="error-message">
                  <AlertCircle size={14} />
                  {errors.name}
                </div>
              )}
            </div>

            <div className="form-group">
              <label className="form-label">Email</label>
              <div className="password-input-wrapper">
                <Mail
                  size={20}
                  style={{
                    position: "absolute",
                    left: "1rem",
                    top: "50%",
                    transform: "translateY(-50%)",
                    color: "#9ca3af",
                  }}
                />
                <input
                  type="email"
                  className={`form-input ${errors.email ? "error" : ""}`}
                  style={{ paddingLeft: "3rem" }}
                  placeholder="seu@email.com"
                  value={registerData.email}
                  onChange={(e) =>
                    setRegisterData({ ...registerData, email: e.target.value })
                  }
                />
              </div>
              {errors.email && (
                <div className="error-message">
                  <AlertCircle size={14} />
                  {errors.email}
                </div>
              )}
            </div>

            <div className="form-group">
              <label className="form-label">Senha</label>
              <div className="password-input-wrapper">
                <Lock
                  size={20}
                  style={{
                    position: "absolute",
                    left: "1rem",
                    top: "50%",
                    transform: "translateY(-50%)",
                    color: "#9ca3af",
                  }}
                />
                <input
                  type={showPassword ? "text" : "password"}
                  className={`form-input ${errors.password ? "error" : ""}`}
                  style={{ paddingLeft: "3rem", paddingRight: "3rem" }}
                  placeholder="••••••••"
                  value={registerData.password}
                  onChange={(e) =>
                    setRegisterData({
                      ...registerData,
                      password: e.target.value,
                    })
                  }
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {passwordStrength && (
                <div className="password-strength">
                  <div className="strength-bar">
                    <div
                      className={`strength-bar-fill ${passwordStrength.level}`}
                    ></div>
                  </div>
                  <span className="strength-text">
                    Força da senha: {passwordStrength.text}
                  </span>
                </div>
              )}
              {errors.password && (
                <div className="error-message">
                  <AlertCircle size={14} />
                  {errors.password}
                </div>
              )}
            </div>

            <div className="form-group">
              <label className="form-label">Confirmar senha</label>
              <div className="password-input-wrapper">
                <Lock
                  size={20}
                  style={{
                    position: "absolute",
                    left: "1rem",
                    top: "50%",
                    transform: "translateY(-50%)",
                    color: "#9ca3af",
                  }}
                />
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  className={`form-input ${errors.confirmPassword ? "error" : ""}`}
                  style={{ paddingLeft: "3rem", paddingRight: "3rem" }}
                  placeholder="••••••••"
                  value={registerData.confirmPassword}
                  onChange={(e) =>
                    setRegisterData({
                      ...registerData,
                      confirmPassword: e.target.value,
                    })
                  }
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? (
                    <EyeOff size={20} />
                  ) : (
                    <Eye size={20} />
                  )}
                </button>
              </div>
              {errors.confirmPassword && (
                <div className="error-message">
                  <AlertCircle size={14} />
                  {errors.confirmPassword}
                </div>
              )}
            </div>

            <button
              type="submit"
              className={`auth-button ${loading ? "loading" : ""}`}
              disabled={loading}
            >
              {loading ? <span className="spinner"></span> : "Criar conta"}
            </button>

            <p className="auth-footer">
              Ao criar uma conta, você concorda com nossos{" "}
              <a href="/terms">Termos de Uso</a> e{" "}
              <a href="/privacy">Política de Privacidade</a>.
            </p>
          </form>
        )}
      </div>
    </div>
  );
};

export default AuthPage;
