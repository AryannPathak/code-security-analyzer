import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  Activity, 
  ShoppingCart, 
  Building2, 
  LayoutDashboard, 
  LogOut, 
  LogIn, 
  User, 
  Package, 
  Cpu, 
  Sparkles,
  ClipboardList,
  Store
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';

export default function Navbar() {
  const { user, logout, login } = useAuth();
  const { cartCount } = useCart();
  const navigate = useNavigate();
  const location = useLocation();

  const handleDemoSwitch = async (role) => {
    try {
      if (role === 'ADMIN') {
        await login('admin', 'Admin@12345');
        navigate('/admin');
      } else if (role === 'EMPLOYEE') {
        await login('cashier_mumbai', 'Cashier@12345');
        navigate('/pos');
      } else {
        await login('customer_demo', 'Customer@12345');
        navigate('/');
      }
    } catch {
      // Fallback if demo customer doesn't exist yet
      if (role === 'CUSTOMER') {
        try {
          await login('aarav_sharma_1', 'Customer@12345');
          navigate('/');
        } catch {
          navigate('/login');
        }
      }
    }
  };

  const isActive = (path) => location.pathname === path;

  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand Logo & Mode Badge */}
        <div className="flex items-center space-x-6">
          <Link to="/" className="flex items-center space-x-2.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-sky-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="font-extrabold text-xl tracking-tight text-white flex items-center gap-1.5">
                SMARTFLOW
              </span>
              <span className="text-[10px] text-slate-400 block -mt-1 font-mono tracking-wider">
                RETAIL &bull; E-COM &bull; AI
              </span>
            </div>
          </Link>

          {/* Quick Role Demo Switcher Bar */}
          <div className="hidden lg:flex items-center space-x-1 p-1 rounded-xl bg-slate-950/70 border border-slate-800 text-xs font-medium">
            <span className="px-2 text-[10px] text-slate-500 uppercase tracking-wider font-mono">Demo Role:</span>
            <button
              onClick={() => handleDemoSwitch('ADMIN')}
              className={`px-2.5 py-1 rounded-lg transition ${
                user?.role === 'ADMIN'
                  ? 'bg-blue-600 text-white font-semibold shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              Admin
            </button>
            <button
              onClick={() => handleDemoSwitch('EMPLOYEE')}
              className={`px-2.5 py-1 rounded-lg transition ${
                user?.role === 'EMPLOYEE'
                  ? 'bg-emerald-600 text-white font-semibold shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              DMart POS Cashier
            </button>
            <button
              onClick={() => handleDemoSwitch('CUSTOMER')}
              className={`px-2.5 py-1 rounded-lg transition ${
                user?.role === 'CUSTOMER'
                  ? 'bg-amber-600 text-white font-semibold shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              Amazon Shopper
            </button>
          </div>
        </div>

        {/* Dynamic Center Navigation Links based on active role */}
        <nav className="hidden md:flex items-center space-x-1 text-sm font-medium">
          {/* Customer links */}
          <Link
            to="/"
            className={`px-3 py-1.5 rounded-lg transition ${
              isActive('/') ? 'text-white bg-slate-800 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Storefront
          </Link>
          <Link
            to="/products"
            className={`px-3 py-1.5 rounded-lg transition ${
              isActive('/products') ? 'text-white bg-slate-800 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Catalog
          </Link>

          {/* DMart POS Terminal shortcut */}
          <Link
            to="/pos"
            className={`px-3 py-1.5 rounded-lg flex items-center space-x-1.5 transition ${
              isActive('/pos')
                ? 'text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 font-semibold'
                : 'text-emerald-400/80 hover:text-emerald-300 hover:bg-slate-800'
            }`}
          >
            <Store className="w-4 h-4" />
            <span>DMart POS</span>
          </Link>

          {/* Admin link */}
          <Link
            to="/admin"
            className={`px-3 py-1.5 rounded-lg flex items-center space-x-1.5 transition ${
              location.pathname.startsWith('/admin')
                ? 'text-blue-400 bg-blue-950/60 border border-blue-800/60 font-semibold'
                : 'text-blue-400/80 hover:text-blue-300 hover:bg-slate-800'
            }`}
          >
            <LayoutDashboard className="w-4 h-4" />
            <span>Admin</span>
          </Link>

          {/* AIML Insights link */}
          <Link
            to="/admin/aiml"
            className={`px-3 py-1.5 rounded-lg flex items-center space-x-1.5 transition ${
              isActive('/admin/aiml')
                ? 'text-sky-400 bg-sky-950/60 border border-sky-800/60 font-semibold'
                : 'text-sky-400/80 hover:text-sky-300 hover:bg-slate-800'
            }`}
          >
            <Cpu className="w-4 h-4" />
            <span>AIML</span>
          </Link>
        </nav>

        {/* Right Action Icons: Cart & Profile */}
        <div className="flex items-center space-x-3">
          {/* Cart Icon with Counter */}
          <Link
            to="/cart"
            className="relative p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 transition"
            title="Shopping Cart"
          >
            <ShoppingCart className="w-5 h-5" />
            {cartCount > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-amber-500 text-slate-950 text-xs font-bold flex items-center justify-center animate-pulse">
                {cartCount}
              </span>
            )}
          </Link>

          {/* User state */}
          {user ? (
            <div className="flex items-center space-x-2 pl-2 border-l border-slate-800">
              <Link
                to="/orders"
                className="hidden sm:inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition"
              >
                <ClipboardList className="w-3.5 h-3.5 text-blue-400" />
                <span>My Orders</span>
              </Link>
              <div className="text-right hidden sm:block">
                <span className="text-xs font-semibold text-white block leading-tight">{user.username}</span>
                <span className="text-[10px] text-blue-400 uppercase font-mono">{user.role}</span>
              </div>
              <button
                onClick={logout}
                className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-950/40 transition"
                title="Log Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="inline-flex items-center space-x-1.5 py-2 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-md transition"
            >
              <LogIn className="w-4 h-4" />
              <span>Sign In</span>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
