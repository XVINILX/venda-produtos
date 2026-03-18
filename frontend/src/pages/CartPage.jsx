// frontend/src/pages/CartPage.jsx
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useCart } from "../contexts/CartContext";
import CartItem from "../components/Cart/CartItem";
import CouponInput from "../components/Cart/CouponInput";
import { ShoppingCart, ArrowLeft, CheckCircle, XCircle } from "lucide-react";
import "./CartPage.css";

const CartPage = () => {
  const navigate = useNavigate();
  const { cart, loading, error, applyCouponToCart, makeCheckout } = useCart();
  const [couponFeedback, setCouponFeedback] = useState(null);
  const [showCheckoutModal, setShowCheckoutModal] = useState(false);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [checkoutResult, setCheckoutResult] = useState(null);

  const handleApplyCoupon = async (code) => {
    setCouponFeedback(null);
    try {
      await applyCouponToCart(code);
      setCouponFeedback({ type: "success", message: "Cupom aplicado!" });
    } catch (err) {
      setCouponFeedback({ type: "error", message: "Cupom inválido" });
    }
  };

  const handleCheckout = () => {
    setShowCheckoutModal(true);
  };

  const confirmCheckout = async () => {
    setCheckoutLoading(true);
    try {
      const result = await makeCheckout();
      setCheckoutResult({
        success: true,
        message: "Compra finalizada com sucesso!",
        cart_id: result.cart_id,
        total: result.total,
      });

      // Fechar modal após 3 segundos e redirecionar
      setTimeout(() => {
        setShowCheckoutModal(false);
        setCheckoutResult(null);
        navigate("/"); // ou para uma página de pedido confirmado
      }, 3000);
    } catch (error) {
      console.error("Erro no checkout:", error);
      setCheckoutResult({
        success: false,
        message: error.response?.data?.detail || "Erro ao finalizar compra",
      });
    } finally {
      setCheckoutLoading(false);
    }
  };

  const cancelCheckout = () => {
    setShowCheckoutModal(false);
    setCheckoutResult(null);
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
              <span className="total-value">R$ {cart.total.toFixed(2)}</span>
            </div>

            <button
              className="checkout-btn"
              onClick={handleCheckout}
              disabled={cart.items.length === 0}
            >
              Finalizar Compra
            </button>
          </div>
        </div>
      )}

      {/* Modal de Confirmação de Checkout */}
      {showCheckoutModal && (
        <div className="modal-overlay">
          <div className="modal-content checkout-modal">
            {!checkoutResult ? (
              // Modal de confirmação
              <>
                <h3>Confirmar Compra</h3>

                <div className="checkout-summary">
                  <div className="summary-item">
                    <span>Total de itens:</span>
                    <strong>{cart.items.length}</strong>
                  </div>
                  <div className="summary-item">
                    <span>Subtotal:</span>
                    <strong>R$ {cart.subtotal.toFixed(2)}</strong>
                  </div>
                  {cart.discount > 0 && (
                    <div className="summary-item discount">
                      <span>Desconto:</span>
                      <strong>- R$ {cart.discount.toFixed(2)}</strong>
                    </div>
                  )}
                  <div className="summary-item total">
                    <span>Total a pagar:</span>
                    <strong>R$ {cart.total.toFixed(2)}</strong>
                  </div>
                </div>

                <p className="checkout-warning">
                  Ao confirmar, você concorda com os termos de compra.
                </p>

                <div className="modal-actions">
                  <button
                    className="cancel-btn"
                    onClick={cancelCheckout}
                    disabled={checkoutLoading}
                  >
                    Cancelar
                  </button>
                  <button
                    className="confirm-btn"
                    onClick={confirmCheckout}
                    disabled={checkoutLoading}
                  >
                    {checkoutLoading ? (
                      <>
                        <div className="loading-spinner-small"></div>
                        Processando...
                      </>
                    ) : (
                      "Confirmar Compra"
                    )}
                  </button>
                </div>
              </>
            ) : (
              // Modal de resultado
              <div
                className={`checkout-result ${checkoutResult.success ? "success" : "error"}`}
              >
                {checkoutResult.success ? (
                  <>
                    <CheckCircle size={48} />
                    <h4>Compra realizada com sucesso!</h4>
                    <p>{checkoutResult.message}</p>
                    {checkoutResult.cart_id && (
                      <p className="order-id">
                        Pedido #{checkoutResult.cart_id}
                      </p>
                    )}
                  </>
                ) : (
                  <>
                    <XCircle size={48} />
                    <h4>Erro ao finalizar compra</h4>
                    <p>{checkoutResult.message}</p>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CartPage;
