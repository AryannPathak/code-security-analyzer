import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Customer Pages
import CustomerHome from './pages/Customer/CustomerHome';
import ProductCatalog from './pages/Customer/ProductCatalog';
import CartPage from './pages/Customer/CartPage';
import CheckoutPage from './pages/Customer/CheckoutPage';
import MyOrders from './pages/Customer/MyOrders';

// Store / POS Page
import PosTerminal from './pages/Store/PosTerminal';

// Auth Pages
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';

// Admin Pages
import AdminDashboard from './pages/Admin/AdminDashboard';
import ProductManagement from './pages/Admin/ProductManagement';
import InventoryManagement from './pages/Admin/InventoryManagement';
import TransactionManagement from './pages/Admin/TransactionManagement';
import AimlInsights from './pages/Admin/AimlInsights';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <CartProvider>
          <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
            <Navbar />
            <main className="flex-1">
              <Routes>
                {/* Customer Storefront & Catalog */}
                <Route path="/" element={<CustomerHome />} />
                <Route path="/products" element={<ProductCatalog />} />
                <Route path="/cart" element={<CartPage />} />
                <Route path="/checkout" element={<CheckoutPage />} />
                <Route path="/orders" element={<MyOrders />} />

                {/* DMart Physical Retail POS Terminal */}
                <Route path="/pos" element={<PosTerminal />} />

                {/* Authentication */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                {/* Centralized Admin & AIML Management */}
                <Route path="/admin" element={<AdminDashboard />} />
                <Route path="/admin/products" element={<ProductManagement />} />
                <Route path="/admin/inventory" element={<InventoryManagement />} />
                <Route path="/admin/transactions" element={<TransactionManagement />} />
                <Route path="/admin/aiml" element={<AimlInsights />} />
                <Route path="/admin/ai" element={<AimlInsights />} />

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </CartProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
