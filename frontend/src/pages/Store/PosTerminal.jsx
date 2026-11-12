import React, { useState, useEffect, useRef } from 'react';
import { 
  Barcode, 
  Search, 
  Plus, 
  Minus, 
  Trash2, 
  CreditCard, 
  Smartphone, 
  Banknote, 
  Printer, 
  CheckCircle2, 
  User, 
  Store,
  RefreshCw,
  X
} from 'lucide-react';
import api from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import ReceiptModal from '../../components/ReceiptModal';

export default function PosTerminal() {
  const { user } = useAuth();
  const [barcodeInput, setBarcodeInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [cartItems, setCartItems] = useState([]);
  const [customerPhone, setCustomerPhone] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [couponCode, setCouponCode] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('CASH');
  const [isCheckingOut, setIsCheckingOut] = useState(false);
  const [receiptData, setReceiptData] = useState(null);
  const [isReceiptOpen, setIsReceiptOpen] = useState(false);
  const [selectedStoreId, setSelectedStoreId] = useState(2); // Default to DMart Andheri Store (id=2)
  const [stores, setStores] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');

  const barcodeRef = useRef(null);

  useEffect(() => {
    // Focus barcode input on load
    barcodeRef.current?.focus();
    api.get('/stores')
      .then((res) => {
        if (res.data.success) setStores(res.data.stores);
      })
      .catch((err) => console.error(err));
  }, []);

  // Live product search
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(() => {
      api.get(`/products?search=${encodeURIComponent(searchQuery)}&per_page=6`)
        .then((res) => {
          if (res.data.success) setSearchResults(res.data.products);
        })
        .catch((err) => console.error(err));
    }, 250);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Fast Barcode Gun submission handler
  const handleBarcodeSubmit = async (e) => {
    e.preventDefault();
    const code = barcodeInput.trim();
    if (!code) return;

    setErrorMessage('');
    try {
      const res = await api.get(`/products/barcode/${encodeURIComponent(code)}`);
      if (res.data.success) {
        addItemToCart(res.data.product);
        setBarcodeInput('');
      }
    } catch (err) {
      setErrorMessage(err.response?.data?.error || `Product with barcode/SKU "${code}" not found.`);
    }
  };

  const addItemToCart = (product) => {
    setCartItems((prev) => {
      const existing = prev.find((item) => item.product_id === product.id);
      if (existing) {
        return prev.map((item) =>
          item.product_id === product.id
            ? { ...item, quantity: item.quantity + 1, subtotal: (item.quantity + 1) * item.price }
            : item
        );
      }
      return [
        ...prev,
        {
          product_id: product.id,
          name: product.name,
          sku: product.sku,
          barcode: product.barcode,
          price: Number(product.price),
          quantity: 1,
          subtotal: Number(product.price)
        }
      ];
    });
    setSearchQuery('');
    setSearchResults([]);
    barcodeRef.current?.focus();
  };

  const updateQuantity = (productId, newQty) => {
    if (newQty <= 0) {
      removeItem(productId);
      return;
    }
    setCartItems((prev) =>
      prev.map((item) =>
        item.product_id === productId
          ? { ...item, quantity: newQty, subtotal: Number((newQty * item.price).toFixed(2)) }
          : item
      )
    );
  };

  const removeItem = (productId) => {
    setCartItems((prev) => prev.filter((item) => item.product_id !== productId));
  };

  const clearCart = () => {
    setCartItems([]);
    setCustomerPhone('');
    setCustomerName('');
    setCouponCode('');
    setErrorMessage('');
    barcodeRef.current?.focus();
  };

  // Financial calculations
  const subtotal = cartItems.reduce((acc, item) => acc + item.subtotal, 0.0);
  const taxAmount = Number((subtotal * 0.05).toFixed(2));
  const finalTotal = Number((subtotal + taxAmount).toFixed(2));

  // High-Speed POS Checkout
  const handlePosCheckout = async (selectedPayment) => {
    if (cartItems.length === 0) {
      alert('Billing cart is empty. Scan or search products first.');
      return;
    }

    setIsCheckingOut(true);
    setErrorMessage('');
    try {
      const payload = {
        store_id: selectedStoreId,
        payment_method: selectedPayment,
        items: cartItems.map((item) => ({ product_id: item.product_id, quantity: item.quantity })),
        customer_phone: customerPhone || undefined,
        customer_name: customerName || undefined,
        coupon_code: couponCode || undefined
      };

      const res = await api.post('/pos/checkout', payload);
      if (res.data.success) {
        const receipt = res.data.data.receipt;
        receipt.items = cartItems;
        setReceiptData(receipt);
        setIsReceiptOpen(true);
        clearCart();
      }
    } catch (err) {
      setErrorMessage(err.response?.data?.error || 'POS checkout failed.');
    } finally {
      setIsCheckingOut(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Top POS Terminal Status Bar */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">
            <Store className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white flex items-center gap-2">
              DMart POS Terminal #04
              <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-mono border border-emerald-500/20">
                ACTIVE SHIFT
              </span>
            </h1>
            <p className="text-xs text-slate-400">
              Cashier: <span className="text-slate-200 font-semibold">{user?.username || 'Staff'}</span> &bull; Shift: Morning
            </p>
          </div>
        </div>

        {/* Store Selector */}
        <div className="flex items-center space-x-3 text-xs">
          <span className="text-slate-400 font-medium">Retail Store:</span>
          <select
            value={selectedStoreId}
            onChange={(e) => setSelectedStoreId(Number(e.target.value))}
            className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-white font-medium focus:border-emerald-500"
          >
            {stores.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.store_code})
              </option>
            ))}
          </select>
        </div>
      </div>

      {errorMessage && (
        <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-800/60 text-rose-400 text-xs flex items-center justify-between">
          <span>{errorMessage}</span>
          <button onClick={() => setErrorMessage('')}><X className="w-4 h-4" /></button>
        </div>
      )}

      {/* Main POS Split Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Product Search & Barcode Gun Scanner (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          {/* Barcode Gun Input Box */}
          <form onSubmit={handleBarcodeSubmit} className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
            <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Barcode className="w-4 h-4 text-emerald-400" />
              <span>Barcode Gun Scan / SKU Code Entry</span>
            </label>
            <div className="flex space-x-2">
              <input
                ref={barcodeRef}
                type="text"
                value={barcodeInput}
                onChange={(e) => setBarcodeInput(e.target.value)}
                placeholder="Scan barcode gun or enter SKU (e.g. 890100000001 or GRO-10000)"
                className="flex-1 px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 focus:border-emerald-500 text-sm text-white font-mono placeholder-slate-500 transition"
              />
              <button
                type="submit"
                className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md transition"
              >
                Scan Item
              </button>
            </div>
          </form>

          {/* Keyword Product Search */}
          <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-2 relative">
            <label className="block text-xs font-semibold text-slate-400">Search Product by Name or Category</label>
            <div className="relative">
              <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Type product name (e.g. Basmati Rice, Tata Salt, Earbuds)..."
                className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-950 border border-slate-800 focus:border-blue-500 text-xs text-white placeholder-slate-500 transition"
              />
            </div>

            {/* Live Search Results Popup */}
            {searchResults.length > 0 && (
              <div className="absolute left-4 right-4 top-full mt-1 bg-slate-950 border border-slate-700 rounded-xl shadow-2xl z-30 divide-y divide-slate-800 overflow-hidden max-h-64 overflow-y-auto">
                {searchResults.map((p) => (
                  <div
                    key={p.id}
                    onClick={() => addItemToCart(p)}
                    className="p-3 hover:bg-slate-800/80 cursor-pointer flex items-center justify-between text-xs transition"
                  >
                    <div>
                      <span className="font-semibold text-white block">{p.name}</span>
                      <span className="text-[10px] text-slate-400 font-mono">{p.sku} &bull; Barcode: {p.barcode}</span>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-emerald-400 block font-mono">₹{p.price}</span>
                      <span className="text-[10px] text-blue-400 font-semibold">+ Add to Bill</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Customer Attachment (Loyalty) */}
          <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            <h3 className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
              <User className="w-4 h-4 text-blue-400" />
              <span>Customer Loyalty Information (Optional)</span>
            </h3>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <input
                type="text"
                value={customerPhone}
                onChange={(e) => setCustomerPhone(e.target.value)}
                placeholder="Customer Phone (+91 ...)"
                className="px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 font-mono"
              />
              <input
                type="text"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                placeholder="Customer Name"
                className="px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500"
              />
            </div>
          </div>
        </div>

        {/* Right Column: Active Billing Cart & Settlement Panel (5 cols) */}
        <div className="lg:col-span-5 p-6 rounded-3xl bg-slate-900 border border-slate-800 flex flex-col justify-between shadow-2xl space-y-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="font-bold text-white text-base">Current Customer Bill</h3>
              <button
                onClick={clearCart}
                className="text-xs text-rose-400 hover:text-rose-300 font-medium transition"
              >
                Clear Cart
              </button>
            </div>

            {/* Cart Items List */}
            <div className="max-h-72 overflow-y-auto space-y-2 pr-1 scrollbar-thin">
              {cartItems.length === 0 ? (
                <div className="py-12 text-center text-slate-500 text-xs font-mono">
                  No items scanned yet. Scan barcode gun or search products to begin billing.
                </div>
              ) : (
                cartItems.map((item) => (
                  <div
                    key={item.product_id}
                    className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 flex items-center justify-between gap-2"
                  >
                    <div className="truncate max-w-[170px]">
                      <span className="text-xs font-semibold text-white block truncate">{item.name}</span>
                      <span className="text-[10px] text-slate-400 font-mono">₹{item.price} each</span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <div className="flex items-center space-x-1 p-0.5 rounded-lg bg-slate-900 border border-slate-800">
                        <button
                          onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                          className="p-1 text-slate-400 hover:text-white"
                        >
                          <Minus className="w-3 h-3" />
                        </button>
                        <span className="w-5 text-center text-xs font-bold text-white font-mono">{item.quantity}</span>
                        <button
                          onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                          className="p-1 text-slate-400 hover:text-white"
                        >
                          <Plus className="w-3 h-3" />
                        </button>
                      </div>

                      <span className="w-16 text-right text-xs font-bold text-white font-mono">
                        ₹{item.subtotal.toFixed(2)}
                      </span>

                      <button
                        onClick={() => removeItem(item.product_id)}
                        className="text-slate-500 hover:text-rose-400 p-1"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Billing Totals & Tender Buttons */}
          <div className="pt-4 border-t border-slate-800 space-y-4">
            <div className="space-y-1.5 text-xs text-slate-400">
              <div className="flex justify-between">
                <span>Items Subtotal:</span>
                <span className="text-white font-mono">₹{subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>GST (5% Included):</span>
                <span className="text-white font-mono">₹{taxAmount.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-lg font-black text-white pt-2 border-t border-slate-800">
                <span>NET TOTAL:</span>
                <span className="text-emerald-400 font-mono">₹{finalTotal.toFixed(2)}</span>
              </div>
            </div>

            {/* Rapid Tender Buttons */}
            <div className="grid grid-cols-3 gap-2 pt-2">
              <button
                disabled={isCheckingOut || cartItems.length === 0}
                onClick={() => handlePosCheckout('CASH')}
                className="py-3 px-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white font-bold text-xs flex flex-col items-center justify-center space-y-1 shadow-md transition"
              >
                <Banknote className="w-5 h-5" />
                <span>[F1] CASH</span>
              </button>
              <button
                disabled={isCheckingOut || cartItems.length === 0}
                onClick={() => handlePosCheckout('UPI')}
                className="py-3 px-2 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white font-bold text-xs flex flex-col items-center justify-center space-y-1 shadow-md transition"
              >
                <Smartphone className="w-5 h-5" />
                <span>[F2] UPI QR</span>
              </button>
              <button
                disabled={isCheckingOut || cartItems.length === 0}
                onClick={() => handlePosCheckout('CARD')}
                className="py-3 px-2 rounded-xl bg-amber-600 hover:bg-amber-500 disabled:opacity-40 text-white font-bold text-xs flex flex-col items-center justify-center space-y-1 shadow-md transition"
              >
                <CreditCard className="w-5 h-5" />
                <span>[F3] CARD</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Printable Thermal Receipt Popup Modal */}
      <ReceiptModal
        isOpen={isReceiptOpen}
        onClose={() => setIsReceiptOpen(false)}
        receiptData={receiptData}
      />
    </div>
  );
}
