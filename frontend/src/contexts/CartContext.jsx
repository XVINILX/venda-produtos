// frontend/src/contexts/CartContext.jsx
import React, { createContext, useState, useContext, useEffect } from "react";
import * as api from "../services/api";
import { addToCart } from "../services/cart.service";

const CartContext = createContext();

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return context;
};

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState({
    items: [],
    subtotal: 0,
    discount: 0,
    total: 0,
    couponCode: null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Carregar carrinho do localStorage ao iniciar
  useEffect(() => {
    const savedCart = localStorage.getItem("cart");
    if (savedCart) {
      try {
        setCart(JSON.parse(savedCart));
      } catch (e) {
        console.error("Erro ao carregar carrinho:", e);
      }
    }
  }, []);

  // Salvar carrinho no localStorage quando mudar
  useEffect(() => {
    localStorage.setItem("cart", JSON.stringify(cart));
  }, [cart]);

  const fetchCart = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getCart();
      setCart(data);
    } catch (err) {
      setError("Erro ao carregar carrinho");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const addItem = async (productId, quantity) => {
    setLoading(true);
    setError(null);
    try {
      const updatedCart = await addToCart(productId, quantity);
      setCart(updatedCart);
    } catch (err) {
      setError("Erro ao adicionar item");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const updateItem = async (itemId, quantity) => {
    setLoading(true);
    setError(null);
    try {
      const updatedCart = await api.updateCartItem(itemId, quantity);
      setCart(updatedCart);
    } catch (err) {
      setError("Erro ao atualizar item");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const removeItem = async (itemId) => {
    setLoading(true);
    setError(null);
    try {
      const updatedCart = await api.removeFromCart(itemId);
      setCart(updatedCart);
    } catch (err) {
      setError("Erro ao remover item");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const applyCouponToCart = async (code) => {
    setLoading(true);
    setError(null);
    try {
      const updatedCart = await api.applyCoupon(code);
      setCart(updatedCart);
    } catch (err) {
      setError("Cupom inválido");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const clearCart = () => {
    setCart({
      items: [],
      subtotal: 0,
      discount: 0,
      total: 0,
      couponCode: null,
    });
  };

  const value = {
    cart,
    loading,
    error,
    fetchCart,
    addItem,
    updateItem,
    removeItem,
    applyCouponToCart,
    clearCart,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};
