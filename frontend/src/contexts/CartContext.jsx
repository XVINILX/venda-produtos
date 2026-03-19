// frontend/src/contexts/CartContext.jsx
import React, { createContext, useState, useContext, useEffect } from "react";
import {
  getCart,
  updateCartItem,
  addToCart,
  removeFromCart,
  checkout,
} from "../services/cart.service";

import { applyCoupon } from "../services/coupon.service";

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
    fetchCart();
  }, []);

  // Salvar carrinho no localStorage quando mudar
  useEffect(() => {
    localStorage.setItem("cart", JSON.stringify(cart));
  }, [cart]);

  const makeCheckout = async () => {
    setLoading(true);
    setError(null);
    try {
      // Chamar API de checkout
      const response = await checkout();

      // Limpar carrinho local após checkout bem-sucedido
      clearCart();

      // Limpar localStorage
      localStorage.removeItem("cart");

      return response;
    } catch (err) {
      setError("Erro ao finalizar compra");
      console.error(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const fetchCart = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getCart();
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
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateItem = async (itemId, quantity) => {
    setLoading(true);
    setError(null);
    try {
      const updatedCart = await updateCartItem(itemId, quantity);
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
      const updatedCart = await removeFromCart(itemId);
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
      const updatedCart = await applyCoupon(code);
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
    makeCheckout,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};
