import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Sparkles, 
  ArrowRight, 
  ShoppingCart, 
  Star, 
  TrendingUp, 
  ShieldCheck, 
  Tag, 
  Zap,
  Check
} from 'lucide-react';
import api from '../../services/api';
import { useCart } from '../../context/CartContext';

export default function CustomerHome() {
  const [categories, setCategories] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addedId, setAddedId] = useState(null);

  const { addToCart } = useCart();

  useEffect(() => {
    Promise.all([
      api.get('/categories'),
      api.get('/ai/recommendations?limit=6'),
      api.get('/products?per_page=8&sort=newest')
    ])
      .then(([catRes, recRes, prodRes]) => {
        if (catRes.data.success) setCategories(catRes.data.categories);
        if (recRes.data.success) setRecommendations(recRes.data.recommendations);
        if (prodRes.data.success) setFeaturedProducts(prodRes.data.products);
      })
      .catch((err) => console.error('Error fetching home data', err))
      .finally(() => setLoading(false));
  }, []);

  const handleAddToCart = async (product) => {
    try {
      await addToCart(product.id, 1);
      setAddedId(product.id);
      setTimeout(() => setAddedId(null), 1500);
    } catch (err) {
      alert(err.message || 'Please log in to add items to cart.');
    }
  };

  return (
    <div className="space-y-12 pb-16">
      {/* Amazon-style Hero Banner */}
      <section className="relative rounded-3xl overflow-hidden bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 border border-slate-800 p-8 sm:p-12 shadow-2xl">
        <div className="max-w-2xl space-y-5 relative z-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold">
            <Zap className="w-3.5 h-3.5" />
            <span>Grand Omnichannel Megastore &bull; 10,000+ Verified Transactions</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
            DMart Supermarket Savings, Delivered with Amazon Speed.
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Shop wholesale groceries, electronics, and daily essentials backed by real-time inventory synchronization across Mumbai &amp; Bengaluru regional fulfillment hubs.
          </p>
          <div className="flex flex-wrap gap-4 pt-2">
            <Link
              to="/products"
              className="inline-flex items-center space-x-2 py-3 px-6 rounded-xl bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-sm shadow-lg shadow-amber-500/20 transition"
            >
              <span>Explore 1,000+ Products</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/pos"
              className="inline-flex items-center space-x-2 py-3 px-6 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-sm border border-slate-700 transition"
            >
              <span>Launch DMart POS Cashier</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Categories Grid */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Shop by Category</h2>
            <p className="text-xs text-slate-400">Discover handpicked essentials across our aisles</p>
          </div>
          <Link to="/products" className="text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center gap-1">
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3.5">
          {categories.map((cat) => (
            <Link
              key={cat.id}
              to={`/products?category_id=${cat.id}`}
              className="group p-4 rounded-2xl bg-slate-900 border border-slate-800 hover:border-blue-500/50 hover:bg-slate-800/60 transition text-center flex flex-col items-center"
            >
              <div className="w-14 h-14 rounded-xl overflow-hidden mb-3 bg-slate-800 group-hover:scale-105 transition">
                <img
                  src={cat.image_url}
                  alt={cat.name}
                  className="w-full h-full object-cover"
                />
              </div>
              <span className="text-xs font-semibold text-slate-200 group-hover:text-blue-400 transition leading-snug line-clamp-2">
                {cat.name}
              </span>
              <span className="text-[10px] text-slate-500 mt-1 font-mono">{cat.products_count || 140}+ Items</span>
            </Link>
          ))}
        </div>
      </section>

      {/* FEATURE 2: AIML Popularity Recommendations Section */}
      <section className="rounded-3xl bg-slate-900/60 border border-blue-900/30 p-6 sm:p-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-xl font-bold text-white tracking-tight">AI Recommended For You</h2>
                <span className="px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 text-[10px] font-mono border border-blue-500/30 font-semibold">
                  Popularity Algorithm
                </span>
              </div>
              <p className="text-xs text-slate-400">Collaborative frequency ranking derived from 10,000+ past purchases</p>
            </div>
          </div>
          <Link
            to="/admin/aiml"
            className="text-xs text-blue-400 hover:text-blue-300 font-medium inline-flex items-center gap-1 self-start sm:self-center"
          >
            <span>Inspect AIML Logic</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {recommendations.map((prod) => (
            <div
              key={prod.id}
              className="rounded-2xl bg-slate-900 border border-slate-800 p-3.5 flex flex-col justify-between hover:border-slate-700 transition group"
            >
              <div>
                <div className="relative aspect-square rounded-xl overflow-hidden bg-slate-950 mb-3">
                  <img
                    src={prod.image_url}
                    alt={prod.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition"
                  />
                  <span className="absolute top-2 left-2 px-1.5 py-0.5 rounded bg-blue-600/90 text-white text-[10px] font-bold">
                    Top Trending
                  </span>
                </div>
                <span className="text-[10px] text-slate-500 font-mono uppercase tracking-wider block mb-1">
                  {prod.brand}
                </span>
                <h3 className="text-xs font-semibold text-slate-100 line-clamp-2 leading-snug mb-2">
                  {prod.name}
                </h3>
              </div>

              <div className="pt-2 border-t border-slate-800/80">
                <div className="flex items-baseline space-x-1.5 mb-2.5">
                  <span className="text-base font-bold text-white">₹{prod.price}</span>
                  {prod.mrp > prod.price && (
                    <span className="text-[11px] text-slate-500 line-through">₹{prod.mrp}</span>
                  )}
                </div>
                <button
                  onClick={() => handleAddToCart(prod)}
                  className={`w-full py-1.5 px-3 rounded-lg text-xs font-semibold flex items-center justify-center space-x-1 transition ${
                    addedId === prod.id
                      ? 'bg-emerald-600 text-white'
                      : 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm'
                  }`}
                >
                  {addedId === prod.id ? (
                    <>
                      <Check className="w-3.5 h-3.5" />
                      <span>Added!</span>
                    </>
                  ) : (
                    <>
                      <ShoppingCart className="w-3.5 h-3.5" />
                      <span>Add to Cart</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Featured Products Grid */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Today's Featured Deals</h2>
            <p className="text-xs text-slate-400">Exclusive discounts on branded supermarket favorites</p>
          </div>
          <Link to="/products" className="text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center gap-1">
            <span>Explore All 1,000+</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-5">
          {featuredProducts.map((prod) => (
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
                  <span>{prod.brand}</span>
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
                      : 'bg-amber-500 hover:bg-amber-600 text-slate-950 shadow-md shadow-amber-500/10'
                  }`}
                >
                  {addedId === prod.id ? (
                    <>
                      <Check className="w-4 h-4" />
                      <span>Item Added to Cart</span>
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
      </section>
    </div>
  );
}
