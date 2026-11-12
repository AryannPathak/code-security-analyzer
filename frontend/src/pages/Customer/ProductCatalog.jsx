import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, Filter, ShoppingCart, Check, SlidersHorizontal, ChevronLeft, ChevronRight } from 'lucide-react';
import api from '../../services/api';
import { useCart } from '../../context/CartContext';

export default function ProductCatalog() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(1);
  const [addedId, setAddedId] = useState(null);

  const { addToCart } = useCart();

  // URL state sync
  const search = searchParams.get('search') || '';
  const categoryId = searchParams.get('category_id') || '';
  const sort = searchParams.get('sort') || 'newest';
  const page = parseInt(searchParams.get('page') || '1', 10);

  useEffect(() => {
    api.get('/categories')
      .then((res) => {
        if (res.data.success) setCategories(res.data.categories);
      })
      .catch((err) => console.error(err));
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = {
      page,
      per_page: 24,
      search: search || undefined,
      category_id: categoryId || undefined,
      sort: sort || undefined,
    };

    api.get('/products', { params })
      .then((res) => {
        if (res.data.success) {
          setProducts(res.data.products);
          setTotal(res.data.total);
          setPages(res.data.pages);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [search, categoryId, sort, page]);

  const updateParam = (key, value) => {
    const next = new URLSearchParams(searchParams);
    if (value) {
      next.set(key, value);
    } else {
      next.delete(key);
    }
    next.set('page', '1'); // reset page on filter change
    setSearchParams(next);
  };

  const handleAddToCart = async (product) => {
    try {
      await addToCart(product.id, 1);
      setAddedId(product.id);
      setTimeout(() => setAddedId(null), 1500);
    } catch (err) {
      alert(err.message || 'Please log in to add products to cart');
    }
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Header & Search Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Master Product Catalog</h1>
          <p className="text-xs text-slate-400 mt-1">
            Displaying {total} items across centralized retail stores and e-commerce warehouses
          </p>
        </div>

        {/* Search Input */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => updateParam('search', e.target.value)}
            placeholder="Search name, brand, SKU..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 focus:border-blue-500 text-sm text-white placeholder-slate-500 transition"
          />
        </div>
      </div>

      {/* Filter Bar: Categories & Sorting */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Category Filter Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-thin">
          <button
            onClick={() => updateParam('category_id', '')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold shrink-0 transition ${
              !categoryId
                ? 'bg-blue-600 text-white'
                : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            All Categories
          </button>
          {categories.map((c) => (
            <button
              key={c.id}
              onClick={() => updateParam('category_id', String(c.id))}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold shrink-0 transition ${
                categoryId === String(c.id)
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {c.name}
            </button>
          ))}
        </div>

        {/* Sort Selector */}
        <div className="flex items-center space-x-2 shrink-0 text-xs">
          <span className="text-slate-400 font-medium">Sort by:</span>
          <select
            value={sort}
            onChange={(e) => updateParam('sort', e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-white font-medium focus:border-blue-500 transition"
          >
            <option value="newest">Newest Arrivals</option>
            <option value="price_asc">Price: Low to High</option>
            <option value="price_desc">Price: High to Low</option>
            <option value="name_asc">Name: A to Z</option>
          </select>
        </div>
      </div>

      {/* Products Grid */}
      {loading ? (
        <div className="py-20 text-center text-slate-500 font-mono text-sm">
          Loading catalog products...
        </div>
      ) : products.length === 0 ? (
        <div className="py-20 text-center rounded-3xl bg-slate-900 border border-slate-800">
          <p className="text-slate-400 text-sm">No products found matching your search filters.</p>
          <button
            onClick={() => setSearchParams({})}
            className="mt-4 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
          {products.map((prod) => (
            <div
              key={prod.id}
              className="rounded-2xl bg-slate-900 border border-slate-800 p-4 flex flex-col justify-between hover:border-slate-700 transition"
            >
              <div>
                <div className="aspect-square rounded-xl overflow-hidden bg-slate-950 mb-3 relative">
                  <img
                    src={prod.image_url}
                    alt={prod.name}
                    className="w-full h-full object-cover"
                  />
                  {prod.discount_percent > 0 && (
                    <span className="absolute top-2 left-2 px-2 py-0.5 rounded-full bg-rose-600 text-white text-[10px] font-bold">
                      {prod.discount_percent}% OFF
                    </span>
                  )}
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1">
                  <span className="font-semibold text-slate-300">{prod.brand}</span>
                  <span className="font-mono text-slate-500">{prod.sku}</span>
                </div>
                <h3 className="text-sm font-semibold text-white line-clamp-2 leading-snug mb-3">
                  {prod.name}
                </h3>
              </div>

              <div className="pt-3 border-t border-slate-800">
                <div className="flex items-baseline space-x-2 mb-3">
                  <span className="text-lg font-extrabold text-white">₹{prod.price}</span>
                  {prod.mrp > prod.price && (
                    <span className="text-xs text-slate-500 line-through">₹{prod.mrp}</span>
                  )}
                  <span className="text-[10px] text-slate-400 font-mono">/ {prod.unit}</span>
                </div>
                <button
                  onClick={() => handleAddToCart(prod)}
                  className={`w-full py-2.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 transition ${
                    addedId === prod.id
                      ? 'bg-emerald-600 text-white'
                      : 'bg-blue-600 hover:bg-blue-700 text-white shadow-md shadow-blue-500/10'
                  }`}
                >
                  {addedId === prod.id ? (
                    <>
                      <Check className="w-4 h-4" />
                      <span>Item Added</span>
                    </>
                  ) : (
                    <>
                      <ShoppingCart className="w-4 h-4" />
                      <span>Add to Cart</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {pages > 1 && (
        <div className="flex items-center justify-center space-x-3 pt-6 border-t border-slate-800 text-xs">
          <button
            disabled={page <= 1}
            onClick={() => {
              const next = new URLSearchParams(searchParams);
              next.set('page', String(page - 1));
              setSearchParams(next);
            }}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 disabled:opacity-30 hover:bg-slate-800 text-white transition"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-slate-400 font-mono">
            Page {page} of {pages}
          </span>
          <button
            disabled={page >= pages}
            onClick={() => {
              const next = new URLSearchParams(searchParams);
              next.set('page', String(page + 1));
              setSearchParams(next);
            }}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 disabled:opacity-30 hover:bg-slate-800 text-white transition"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
