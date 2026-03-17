// frontend/src/pages/CartPage.jsx
import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useCart } from "../contexts/CartContext";
import CartItem from "../components/Cart/CartItem";
import CouponInput from "../components/Cart/CouponInput";
import { ShoppingCart, ArrowLeft } from "lucide-react";
import "./CartPage.css";

const CartPage = () => {
  const { cart, loading, error, applyCouponToCart } = useCart();
  const [couponFeedback, setCouponFeedback] = useState(null);

  const handleApplyCoupon = async (code) => {
    setCouponFeedback(null);
    try {
      await applyCouponToCart(code);
      setCouponFeedback({ type: "success", message: "Cupom aplicado!" });
    } catch (err) {
      setCouponFeedback({ type: "error", message: "Cupom inválido" });
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner-large"></div>
      </div>
    );
  }

  return (
    <div className="container cart-page">
      <div className="cart-header">
        <h1 className="cart-title">Seu Carrinho</h1>
        <Link to="/" className="continue-shopping">
          <ArrowLeft size={20} />
          Continuar Comprando
        </Link>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {cart.items.length === 0 ? (
        <div className="cart-empty">
          <ShoppingCart />
          <p>Seu carrinho está vazio</p>
          <Link to="/" className="shop-btn">
            Ir às Compras
          </Link>
        </div>
      ) : (
        <div className="cart-grid">
          <div className="cart-items">
            {cart.items.map((item) => (
              <CartItem key={item.id} item={item} />
            ))}
          </div>

          <div className="cart-summary">
            <h2 className="summary-title">Resumo do Pedido</h2>

            <CouponInput
              onApply={handleApplyCoupon}
              feedback={couponFeedback}
            />

            <div className="summary-row">
              <span>Subtotal:</span>
              <span>R$ {cart.subtotal.toFixed(2)}</span>
            </div>

            {cart.discount > 0 && (
              <div className="summary-row discount-row">
                <span>Desconto:</span>
                <span>- R$ {cart.discount.toFixed(2)}</span>
              </div>
            )}

            {cart.couponCode && (
              <div className="coupon-code">Cupom: {cart.couponCode}</div>
            )}

            <div className="summary-row total">
              <span>Total:</span>
              <span>R$ {cart.total.toFixed(2)}</span>
            </div>

            <button className="checkout-btn">Finalizar Compra</button>

            <p className="free-shipping-note">
              Frete calculado no próximo passo
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default CartPage;
