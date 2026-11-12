import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from './AuthContext';

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { user, token } = useAuth();
  const [cart, setCart] = useState({ items: [], total_amount: 0, total_items: 0 });
  const [loading, setLoading] = useState(false);

  const fetchCart = async () => {
    if (!token || user?.role !== 'CUSTOMER') {
      setCart({ items: [], total_amount: 0, total_items: 0 });
      return;
    }
    try {
      setLoading(true);
      const res = await api.get('/cart');
      if (res.data.success) {
        setCart(res.data.cart);
      }
    } catch (err) {
      console.error('Failed to load cart', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, [token, user]);

  const addToCart = async (productId, quantity = 1) => {
    if (!token) {
      throw new Error('Please log in to add products to your cart');
    }
    const res = await api.post('/cart/add', { product_id: productId, quantity });
    if (res.data.success) {
      setCart(res.data.cart);
      return res.data;
    }
  };

  const updateQuantity = async (productId, quantity) => {
    const res = await api.put('/cart/update', { product_id: productId, quantity });
    if (res.data.success) {
      setCart(res.data.cart);
      return res.data;
    }
  };

  const removeFromCart = async (productId) => {
    const res = await api.delete(`/cart/remove/${productId}`);
    if (res.data.success) {
      setCart(res.data.cart);
      return res.data;
    }
  };

  const clearCart = async () => {
    const res = await api.delete('/cart/clear');
    if (res.data.success) {
      setCart({ items: [], total_amount: 0, total_items: 0 });
      return res.data;
    }
  };

  const value = {
    cart,
    cartCount: cart.total_items || 0,
    cartTotal: cart.total_amount || 0,
    loading,
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart,
    refreshCart: fetchCart
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  return useContext(CartContext);
}
