import React, { useState } from "react";
import { ShoppingCart, AlertCircle, Package } from "lucide-react";
import { useCart } from "../../contexts/CartContext";
import "./ProductCard.css";

const ProductCard = ({ product }) => {
  const { addItem, fetchCart } = useCart();
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const handleAddToCart = async () => {
    setLoading(true);
    setFeedback(null);
    try {
      const response = await addItem(product.id, 1);
      setFeedback({ type: "success", message: "Produto adicionado!" });
      setTimeout(() => setFeedback(null), 2000);
      fetchCart();
    } catch (error) {
      setFeedback({
        type: "error",
        message:
          error.response?.data?.detail || "Erro ao adicionar ao carrinho",
      });
      fetchCart();
    } finally {
      setLoading(false);
    }
  };

  const outOfStock = product.stock === 0;

  return (
    <div className="product-card">
      {outOfStock && (
        <div className="product-out-of-stock-badge">
          <AlertCircle size={12} />
          <span>Esgotado</span>
        </div>
      )}

      <div className="product-image">
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} />
        ) : (
          <Package />
        )}
      </div>

      <h3 className="product-name">{product.name}</h3>

      <div className="product-footer">
        <span className="product-price">R$ {product.price.toFixed(2)}</span>
        <span className="product-stock">{product.stock} em estoque</span>
      </div>

      {feedback && (
        <div className={`product-feedback ${feedback.type}`}>
          {feedback.message}
        </div>
      )}

      <button
        onClick={handleAddToCart}
        disabled={outOfStock || loading}
        className="btn-add-to-cart"
      >
        {loading ? (
          <div className="loading-spinner"></div>
        ) : (
          <>
            <ShoppingCart size={20} />
            <span>Adicionar ao Carrinho</span>
          </>
        )}
      </button>
    </div>
  );
};

export default ProductCard;
