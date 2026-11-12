import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LogIn, ShieldAlert, CheckCircle2, UserCheck, Lock, Activity } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function Login() {
  const [identifier, setIdentifier] = useState('admin');
  const [password, setPassword] = useState('Admin@12345');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await login(identifier, password);
      if (data.user.role === 'ADMIN') {
        navigate('/admin');
      } else if (data.user.role === 'EMPLOYEE') {
        navigate('/pos');
      } else {
        navigate('/');
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillCredentials = (user, pass) => {
    setIdentifier(user);
    setPassword(pass);
    setError('');
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
        {/* Subtle decorative glow */}
        <div className="absolute top-0 right-0 w-48 h-48 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 to-sky-400 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-500/20">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Sign In to SmartFlow</h2>
          <p className="text-xs text-slate-400 mt-1">Access Omnichannel Retail &amp; E-Commerce Console</p>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded-xl bg-rose-950/60 border border-rose-800/60 flex items-center space-x-2 text-rose-400 text-xs">
            <ShieldAlert className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Username or Email</label>
            <input
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              required
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-sm text-white placeholder-slate-500 transition"
              placeholder="e.g. admin or cashier_mumbai"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-sm text-white placeholder-slate-500 transition"
              placeholder="Enter your password"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold text-sm shadow-lg shadow-blue-500/20 transition duration-200 mt-2"
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        {/* 1-Click Demo Credentials Buttons for Quick Viva & Examiner Testing */}
        <div className="mt-8 pt-6 border-t border-slate-800">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-3 text-center">
            Quick Fill Demo Accounts:
          </p>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <button
              type="button"
              onClick={() => fillCredentials('admin', 'Admin@12345')}
              className="p-2.5 rounded-xl bg-slate-800/80 hover:bg-blue-950/60 border border-slate-700/60 hover:border-blue-500/50 text-center transition"
            >
              <span className="font-bold text-blue-400 block">Admin</span>
              <span className="text-[10px] text-slate-400">Master</span>
            </button>
            <button
              type="button"
              onClick={() => fillCredentials('cashier_mumbai', 'Cashier@12345')}
              className="p-2.5 rounded-xl bg-slate-800/80 hover:bg-emerald-950/60 border border-slate-700/60 hover:border-emerald-500/50 text-center transition"
            >
              <span className="font-bold text-emerald-400 block">Cashier</span>
              <span className="text-[10px] text-slate-400">DMart POS</span>
            </button>
            <button
              type="button"
              onClick={() => fillCredentials('aarav_sharma_1', 'Customer@12345')}
              className="p-2.5 rounded-xl bg-slate-800/80 hover:bg-amber-950/60 border border-slate-700/60 hover:border-amber-500/50 text-center transition"
            >
              <span className="font-bold text-amber-400 block">Customer</span>
              <span className="text-[10px] text-slate-400">Amazon Shopper</span>
            </button>
          </div>
        </div>

        <p className="text-center text-xs text-slate-400 mt-6">
          Don't have a customer account?{' '}
          <Link to="/register" className="text-blue-400 hover:text-blue-300 font-semibold underline">
            Register Here
          </Link>
        </p>
      </div>
    </div>
  );
}
