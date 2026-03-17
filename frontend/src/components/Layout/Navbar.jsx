// frontend/src/components/Layout/Navbar.jsx
import React from "react";
import { Link, useLocation } from "react-router-dom";
import { ShoppingCart, Package, Home } from "lucide-react";
import { useCart } from "../../contexts/CartContext";
import "./Navbar.css";

const Navbar = () => {
  const location = useLocation();
  const { cart } = useCart();

  const totalItems = cart.items.reduce((acc, item) => acc + item.quantity, 0);

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <Package />
          <span>Wise Sales</span>
        </Link>

        <div className="navbar-menu">
          <Link
            to="/"
            className={`navbar-link ${location.pathname === "/" ? "active" : ""}`}
          >
            <Home />
            <span>Catálogo</span>
          </Link>

          <Link
            to="/cart"
            className={`navbar-link ${location.pathname === "/cart" ? "active" : ""}`}
          >
            <ShoppingCart />
            <span>Carrinho</span>
            {totalItems > 0 && <span className="cart-badge">{totalItems}</span>}
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
