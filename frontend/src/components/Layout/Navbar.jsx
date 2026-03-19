// frontend/src/components/Layout/Navbar.jsx
import React, { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ShoppingCart,
  Package,
  Home,
  User,
  LogOut,
  ChevronDown,
} from "lucide-react";
import { useCart } from "../../contexts/CartContext";
import { useAuth } from "../../contexts/AuthContext";
import "./Navbar.css";

const Navbar = () => {
  const { cart, clearCart } = useCart();
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);
  const totalItems = cart.items.reduce((acc, item) => acc + item.quantity, 0);

  // Fechar dropdown ao clicar fora
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = () => {
    clearCart();
    logout();
    navigate("/");
    setShowDropdown(false);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <Package />
          <span>Wise Sales</span>
        </Link>

        <div className="navbar-menu">
          <Link to="/" className="navbar-link">
            <Home size={20} />
            <span>Catálogo</span>
          </Link>

          <Link to="/cart" className="navbar-link">
            <ShoppingCart size={20} />
            <span>Carrinho</span>
            {totalItems > 0 && <span className="cart-badge">{totalItems}</span>}
          </Link>

          {isAuthenticated() ? (
            <div className="user-menu" ref={dropdownRef}>
              <button
                className="user-button"
                onClick={() => setShowDropdown(!showDropdown)}
              >
                <User size={20} />
                <span>Olá, {user?.name?.split(" ")[0]}</span>
                <ChevronDown size={16} />
              </button>

              {showDropdown && (
                <div className="user-dropdown">
                  <div className="dropdown-header">
                    <strong>{user?.name}</strong>
                    <small>{user?.email}</small>
                  </div>
                  <div className="dropdown-divider"></div>

                  {user?.is_admin && (
                    <Link to="/dashboard" className="dropdown-item">
                      <Package size={16} />
                      Dashboard
                    </Link>
                  )}
                  <div className="dropdown-divider"></div>
                  <button
                    onClick={handleLogout}
                    className="dropdown-item logout"
                  >
                    <LogOut size={16} />
                    Sair
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link to="/login" className="navbar-link login-btn">
              <User size={20} />
              <span>Entrar</span>
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
