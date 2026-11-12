import React, { useState, useEffect } from 'react';
import { Package, Plus, Search, Edit2, Trash2, X, Check, Tag } from 'lucide-react';
import api from '../../services/api';

export default function ProductManagement() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editId, setEditId] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    category_id: 1,
    brand: '',
    unit: 'piece',
    mrp: '',
    price: '',
    cost_price: '',
    initial_stock: 50,
    description: '',
  });

  const fetchProducts = () => {
    setLoading(true);
    api.get('/products', {
      params: {
        page,
        per_page: 20,
        search: search || undefined,
        category_id: selectedCategory || undefined,
      },
    })
      .then((res) => {
        if (res.data.success) {
          setProducts(res.data.products);
          setTotal(res.data.total);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    api.get('/categories').then((res) => {
      if (res.data.success) setCategories(res.data.categories);
    });
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [page, search, selectedCategory]);

  const handleOpenAdd = () => {
    setIsEditing(false);
    setEditId(null);
    setFormData({
      name: '',
      category_id: categories[0]?.id || 1,
      brand: 'SmartFlow Basics',
      unit: 'piece',
      mrp: '199',
      price: '149',
      cost_price: '100',
      initial_stock: 50,
      description: 'High quality supermarket retail staple.',
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (p) => {
    setIsEditing(true);
    setEditId(p.id);
    setFormData({
      name: p.name,
      category_id: p.category_id,
      brand: p.brand || '',
      unit: p.unit || 'piece',
      mrp: String(p.mrp),
      price: String(p.price),
      cost_price: String(p.cost_price),
      initial_stock: 0,
      description: p.description || '',
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isEditing) {
        await api.put(`/products/${editId}`, formData);
        alert('Product updated successfully.');
      } else {
        await api.post('/products', formData);
        alert('Product created and allocated across store inventories.');
      }
      setIsModalOpen(false);
      fetchProducts();
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to save product.');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete or deactivate this product?')) return;
    try {
      await api.delete(`/products/${id}`);
      fetchProducts();
    } catch (err) {
      alert(err.response?.data?.error || 'Delete failed.');
    }
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Product Catalog Management</h1>
          <p className="text-xs text-slate-400 mt-1">Master product directory shared between DMart POS &amp; Amazon online shopping</p>
        </div>
        <button
          onClick={handleOpenAdd}
          className="py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs flex items-center space-x-2 shadow-md transition self-start sm:self-center"
        >
          <Plus className="w-4 h-4" />
          <span>Add New Product</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Search by name, SKU, or barcode..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 focus:border-blue-500 text-xs text-white placeholder-slate-500 transition"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto text-xs">
          <span className="text-slate-400 shrink-0">Category:</span>
          <select
            value={selectedCategory}
            onChange={(e) => { setSelectedCategory(e.target.value); setPage(1); }}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white font-medium focus:border-blue-500 transition w-full sm:w-56"
          >
            <option value="">All Categories ({categories.length})</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="text-slate-400 border-b border-slate-800">
              <th className="pb-3">Product Name</th>
              <th className="pb-3">SKU</th>
              <th className="pb-3">Barcode</th>
              <th className="pb-3">Brand</th>
              <th className="pb-3 text-right">MRP (₹)</th>
              <th className="pb-3 text-right">Selling Price (₹)</th>
              <th className="pb-3 text-center">Status</th>
              <th className="pb-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {products.map((p) => (
              <tr key={p.id} className="hover:bg-slate-800/40 transition">
                <td className="py-3 font-sans font-semibold text-white max-w-xs truncate">{p.name}</td>
                <td className="py-3 text-slate-300 font-bold">{p.sku}</td>
                <td className="py-3 text-slate-400">{p.barcode}</td>
                <td className="py-3 font-sans text-slate-300">{p.brand}</td>
                <td className="py-3 text-right text-slate-400">₹{p.mrp}</td>
                <td className="py-3 text-right text-emerald-400 font-bold">₹{p.price}</td>
                <td className="py-3 text-center">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    p.is_available ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                  }`}>
                    {p.is_available ? 'AVAILABLE' : 'OFFLINE'}
                  </span>
                </td>
                <td className="py-3 text-right space-x-2">
                  <button
                    onClick={() => handleOpenEdit(p)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-blue-400 hover:bg-slate-800 transition"
                    title="Edit"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleDelete(p.id)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition"
                    title="Delete"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Add / Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="font-bold text-white text-base">
                {isEditing ? 'Edit Product Details' : 'Onboard New Master Product'}
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Product Title *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white text-sm"
                  placeholder="e.g. Tata Tea Gold 500g"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Category *</label>
                  <select
                    value={formData.category_id}
                    onChange={(e) => setFormData({ ...formData, category_id: Number(e.target.value) })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white"
                  >
                    {categories.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Brand Name</label>
                  <input
                    type="text"
                    value={formData.brand}
                    onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">MRP (₹) *</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={formData.mrp}
                    onChange={(e) => setFormData({ ...formData, mrp: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Selling Price (₹) *</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Cost Price (₹)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.cost_price}
                    onChange={(e) => setFormData({ ...formData, cost_price: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white font-mono"
                  />
                </div>
              </div>

              {!isEditing && (
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Initial Stock per Store Branch</label>
                  <input
                    type="number"
                    value={formData.initial_stock}
                    onChange={(e) => setFormData({ ...formData, initial_stock: Number(e.target.value) })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white font-mono"
                  />
                </div>
              )}

              <div className="pt-3 border-t border-slate-800 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs shadow-md"
                >
                  {isEditing ? 'Save Changes' : 'Create Product'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
