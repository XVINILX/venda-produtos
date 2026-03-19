// frontend/src/components/Cart/CartItem.jsx
import React, { useState } from "react";
import { Trash2, Plus, Minus } from "lucide-react";
import { useCart } from "../../contexts/CartContext";
import "./CartItem.css";

const CartItem = ({ item }) => {
  const { updateItem, removeItem } = useCart();
  const [loading, setLoading] = useState(false);

  const handleUpdateQuantity = async (newQuantity) => {
    if (newQuantity < 1) {
      await handleRemove();
      return;
    }

    setLoading(true);
    try {
      await updateItem(item.id, newQuantity);
    } catch (error) {
      console.error("Erro ao atualizar:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async () => {
    setLoading(true);
    try {
      await removeItem(item.id);
    } catch (error) {
      console.error("Erro ao remover:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="cart-item">
      <div className="cart-item-info">
        <h4 className="cart-item-name">{item.product_name}</h4>
        <span className="cart-item-price">R$ {item.unit_price.toFixed(2)}</span>
      </div>

      <div className="cart-item-actions">
        <div className="quantity-control">
          <button
            onClick={() => handleUpdateQuantity(item.quantity - 1)}
            disabled={loading || item.quantity <= 1}
            className="quantity-btn"
          >
            <Minus size={16} />
          </button>
          <span className="quantity-value">{item.quantity}</span>
          <button
            onClick={() => handleUpdateQuantity(item.quantity + 1)}
            disabled={loading}
            className="quantity-btn"
          >
            <Plus size={16} />
          </button>
        </div>

        <span className="item-subtotal">R$ {item.subtotal.toFixed(2)}</span>

        <button
          onClick={handleRemove}
          disabled={loading}
          className="remove-btn"
        >
          <Trash2 size={18} />
        </button>
      </div>
    </div>
  );
};

export default CartItem;
