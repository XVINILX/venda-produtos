// frontend/src/components/Cart/CouponInput.jsx
import React, { useState } from "react";
import "./CouponInput.css";

const CouponInput = ({ onApply, feedback }) => {
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!code.trim()) return;

    setLoading(true);
    try {
      await onApply(code.trim());
      setCode("");
    } catch (error) {
      console.error("Erro ao aplicar cupom:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="coupon-container">
      <form onSubmit={handleSubmit}>
        <label className="coupon-label" htmlFor="coupon">
          Cupom de desconto
        </label>
        <div className="coupon-input-group">
          <input
            type="text"
            id="coupon"
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            placeholder="Digite seu cupom"
            className="coupon-input"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!code.trim() || loading}
            className="coupon-btn"
          >
            {loading ? "Aplicando..." : "Aplicar"}
          </button>
        </div>
      </form>

      {feedback && (
        <div className={`coupon-feedback ${feedback.type}`}>
          {feedback.message}
        </div>
      )}
    </div>
  );
};

export default CouponInput;
