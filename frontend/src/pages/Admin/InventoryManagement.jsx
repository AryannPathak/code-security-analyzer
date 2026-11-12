import React, { useState, useEffect } from 'react';
import { Package, AlertTriangle, Plus, Search, Store, ArrowDownLeft, X } from 'lucide-react';
import api from '../../services/api';

export default function InventoryManagement() {
  const [inventory, setInventory] = useState([]);
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState('');
  const [lowStockOnly, setLowStockOnly] = useState(false);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

  // Restock Modal
  const [isRestockOpen, setIsRestockOpen] = useState(false);
  const [selectedInv, setSelectedInv] = useState(null);
  const [restockQty, setRestockQty] = useState(50);
  const [refId, setRefId] = useState('INVOICE-SHIP-01');

  const fetchInventory = () => {
    setLoading(true);
    api.get('/inventory', {
      params: {
        store_id: selectedStore || undefined,
        low_stock: lowStockOnly || undefined,
        search: search || undefined,
        per_page: 30,
      },
    })
      .then((res) => {
        if (res.data.success) {
          setInventory(res.data.inventory);
          setTotal(res.data.total);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    api.get('/stores').then((res) => {
      if (res.data.success) setStores(res.data.stores);
    });
  }, []);

  useEffect(() => {
    fetchInventory();
  }, [selectedStore, lowStockOnly, search]);

  const handleOpenRestock = (item) => {
    setSelectedInv(item);
    setRestockQty(60);
    setRefId(`RESTOCK-${Date.now().toString().slice(-6)}`);
    setIsRestockOpen(true);
  };

  const handleRestockSubmit = async (e) => {
    e.preventDefault();
    if (!selectedInv) return;

    try {
      await api.post('/inventory/restock', {
        store_id: selectedInv.store_id,
        product_id: selectedInv.product_id,
        quantity: Number(restockQty),
        reference_id: refId,
        notes: 'Warehouse batch shipment delivery',
      });
      alert(`Restocked ${restockQty} units successfully.`);
      setIsRestockOpen(false);
      fetchInventory();
    } catch (err) {
      alert(err.response?.data?.error || 'Restock failed.');
    }
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Centralized Inventory Auditor</h1>
          <p className="text-xs text-slate-400 mt-1">Multi-store physical stock levels &bull; Safety thresholds &bull; Low-stock alerts</p>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          <button
            onClick={() => setLowStockOnly(!lowStockOnly)}
            className={`py-2 px-3.5 rounded-xl border flex items-center space-x-1.5 font-semibold transition ${
              lowStockOnly
                ? 'bg-rose-950/60 border-rose-500 text-rose-400'
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Low-Stock Alerts Only</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search product name, SKU..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 focus:border-blue-500 text-xs text-white placeholder-slate-500 transition"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto text-xs">
          <span className="text-slate-400 shrink-0">Store Branch:</span>
          <select
            value={selectedStore}
            onChange={(e) => setSelectedStore(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white font-medium focus:border-blue-500 transition w-full sm:w-60"
          >
            <option value="">All Physical Branches ({stores.length})</option>
            {stores.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="text-slate-400 border-b border-slate-800">
              <th className="pb-3">Store Branch</th>
              <th className="pb-3">Product Name</th>
              <th className="pb-3">SKU</th>
              <th className="pb-3 text-center">In-Stock Qty</th>
              <th className="pb-3 text-center">Safety Level</th>
              <th className="pb-3 text-center">Stock Health</th>
              <th className="pb-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {inventory.map((inv) => (
              <tr key={inv.id} className="hover:bg-slate-800/40 transition">
                <td className="py-3 font-sans font-medium text-slate-300">{inv.store_name}</td>
                <td className="py-3 font-sans font-semibold text-white max-w-xs truncate">{inv.product_name}</td>
                <td className="py-3 text-slate-400">{inv.product_sku}</td>
                <td className="py-3 text-center text-sm font-bold text-white">{inv.stock_quantity}</td>
                <td className="py-3 text-center text-slate-400">{inv.safety_stock_level}</td>
                <td className="py-3 text-center">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    inv.is_low_stock
                      ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  }`}>
                    {inv.is_low_stock ? 'CRITICAL LOW' : 'OPTIMAL'}
                  </span>
                </td>
                <td className="py-3 text-right">
                  <button
                    onClick={() => handleOpenRestock(inv)}
                    className="py-1 px-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition"
                  >
                    + Restock
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Restock Shipment Modal */}
      {isRestockOpen && selectedInv && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="font-bold text-white text-base">Receive Restock Shipment</h3>
              <button onClick={() => setIsRestockOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleRestockSubmit} className="space-y-4 text-xs">
              <div>
                <span className="text-slate-400 block mb-1">Target Product:</span>
                <span className="font-bold text-white text-sm block">{selectedInv.product_name}</span>
                <span className="text-slate-500 font-mono">Store: {selectedInv.store_name}</span>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Received Shipment Quantity *</label>
                <input
                  type="number"
                  min="1"
                  required
                  value={restockQty}
                  onChange={(e) => setRestockQty(Number(e.target.value))}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white text-sm font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Supplier Invoice Reference</label>
                <input
                  type="text"
                  value={refId}
                  onChange={(e) => setRefId(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs font-mono"
                />
              </div>

              <div className="pt-3 border-t border-slate-800 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setIsRestockOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs shadow-md"
                >
                  Confirm &amp; Audit Stock
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
