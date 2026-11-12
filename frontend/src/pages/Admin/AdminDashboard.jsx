import React, { useState, useEffect } from 'react';
import { 
  DollarSign, 
  ShoppingCart, 
  Package, 
  Users, 
  TrendingUp, 
  AlertTriangle, 
  ArrowUpRight, 
  Store, 
  Globe,
  Clock,
  CheckCircle2,
  XCircle,
  FileText
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import api from '../../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function AdminDashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/analytics/dashboard')
      .then((res) => {
        if (res.data.success) {
          setDashboardData(res.data);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !dashboardData) {
    return <div className="py-20 text-center text-slate-500 font-mono text-sm">Loading Enterprise Dashboard...</div>;
  }

  const { kpis, daily_sales, top_products, category_performance, recent_transactions, recent_orders } = dashboardData;

  // Chart 1: Daily Sales Trend (Line)
  const lineChartData = {
    labels: daily_sales.map((d) => d.date),
    datasets: [
      {
        label: 'Daily Revenue (₹)',
        data: daily_sales.map((d) => d.amount),
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.1)',
        fill: true,
        tension: 0.35,
        borderWidth: 2,
        pointBackgroundColor: '#38bdf8',
      },
    ],
  };

  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#0f172a',
        titleColor: '#f8fafc',
        bodyColor: '#38bdf8',
        borderColor: '#334155',
        borderWidth: 1,
      },
    },
    scales: {
      x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 10 } } },
      y: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8', font: { size: 10 } } },
    },
  };

  // Chart 2: Online vs Store Channels (Doughnut)
  const channelChartData = {
    labels: ['Store (DMart POS)', 'Online (Amazon Storefront)'],
    datasets: [
      {
        data: [kpis.store_sales, kpis.online_sales],
        backgroundColor: ['#10b981', '#3b82f6'],
        borderColor: ['#0f172a', '#0f172a'],
        borderWidth: 2,
      },
    ],
  };

  // Chart 3: Top Selling Products (Bar)
  const barChartData = {
    labels: top_products.map((p) => p.name.substring(0, 16) + '...'),
    datasets: [
      {
        label: 'Units Sold',
        data: top_products.map((p) => p.units_sold),
        backgroundColor: '#f59e0b',
        borderRadius: 8,
      },
    ],
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Enterprise Master Dashboard</h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time omnichannel sales, centralized inventory, and AIML health telemetry
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-emerald-400 font-semibold font-mono">Telemetry Synchronized (10,000+ Txns)</span>
        </div>
      </div>

      {/* KPI Stats Cards (Grid of 4) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between shadow-lg">
          <div>
            <span className="text-xs font-semibold text-slate-400 block mb-1">Total Gross Revenue</span>
            <span className="text-2xl font-black text-white font-mono">₹{kpis.total_revenue.toLocaleString()}</span>
            <span className="text-[11px] text-emerald-400 flex items-center gap-0.5 mt-1 font-semibold">
              <TrendingUp className="w-3.5 h-3.5" /> +14.8% vs last month
            </span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center">
            <DollarSign className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between shadow-lg">
          <div>
            <span className="text-xs font-semibold text-slate-400 block mb-1">Total Transactions</span>
            <span className="text-2xl font-black text-white font-mono">{kpis.total_transactions.toLocaleString()}</span>
            <span className="text-[11px] text-slate-400 mt-1 block">
              Store: {kpis.store_transactions} &bull; Online: {kpis.online_transactions}
            </span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center">
            <ShoppingCart className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between shadow-lg">
          <div>
            <span className="text-xs font-semibold text-slate-400 block mb-1">Catalog Master Products</span>
            <span className="text-2xl font-black text-white font-mono">{kpis.total_products}</span>
            <span className="text-[11px] text-amber-400 flex items-center gap-1 mt-1 font-semibold">
              <AlertTriangle className="w-3.5 h-3.5" /> {kpis.low_stock_count} Low-Stock Alerts
            </span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center">
            <Package className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between shadow-lg">
          <div>
            <span className="text-xs font-semibold text-slate-400 block mb-1">Customer Profiles</span>
            <span className="text-2xl font-black text-white font-mono">{kpis.total_customers}</span>
            <span className="text-[11px] text-slate-400 mt-1 block font-mono">
              Completed Orders: {kpis.completed_orders}
            </span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-400 flex items-center justify-center">
            <Users className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Interactive Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Daily Sales Trend Chart (2 cols) */}
        <div className="lg:col-span-2 p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-white text-base">Daily Sales Velocity (Last 14 Days)</h3>
              <p className="text-xs text-slate-400">Aggregated revenue trend across all stores &amp; e-commerce</p>
            </div>
            <span className="text-xs font-mono font-bold text-sky-400 px-2.5 py-1 rounded-lg bg-sky-500/10 border border-sky-500/20">
              Live Chart.js
            </span>
          </div>
          <div className="h-64">
            <Line data={lineChartData} options={lineChartOptions} />
          </div>
        </div>

        {/* Channel Breakdown Chart (1 col) */}
        <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-white text-base mb-1">Omnichannel Revenue Split</h3>
            <p className="text-xs text-slate-400">Physical DMart retail vs Amazon e-commerce</p>
          </div>
          <div className="h-48 flex items-center justify-center">
            <Doughnut data={channelChartData} options={{ maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 10 } } } } }} />
          </div>
          <div className="pt-2 border-t border-slate-800 flex justify-between text-xs font-mono">
            <span className="text-emerald-400">Store: ₹{kpis.store_sales.toLocaleString()}</span>
            <span className="text-blue-400">Online: ₹{kpis.online_sales.toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Top Products & Category Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Selling Products */}
        <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="font-bold text-white text-base">Top 6 Selling Products</h3>
            <span className="text-xs text-slate-400 font-mono">By units sold</span>
          </div>
          <div className="h-56">
            <Bar data={barChartData} options={{ maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 } } }, y: { ticks: { color: '#94a3b8' } } } }} />
          </div>
        </div>

        {/* Category Performance Breakdown */}
        <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="font-bold text-white text-base">Category Performance</h3>
            <span className="text-xs text-slate-400 font-mono">Revenue &bull; Items</span>
          </div>
          <div className="space-y-3 max-h-56 overflow-y-auto pr-1 scrollbar-thin text-xs">
            {category_performance.map((cat, idx) => (
              <div key={idx} className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 flex items-center justify-between">
                <div>
                  <span className="font-semibold text-white block">{cat.category}</span>
                  <span className="text-[10px] text-slate-400 font-mono">{cat.product_count} Catalog Products</span>
                </div>
                <span className="font-mono font-bold text-emerald-400">₹{cat.total_sales.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Transactions Table */}
      <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h3 className="font-bold text-white text-base">Recent Financial Transactions</h3>
            <p className="text-xs text-slate-400">Live transaction stream across POS counters and online checkout</p>
          </div>
          <span className="text-xs font-mono text-slate-400">Central Ledger</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="text-slate-400 border-b border-slate-800">
                <th className="pb-2">Transaction ID</th>
                <th className="pb-2">Source</th>
                <th className="pb-2">Store Branch</th>
                <th className="pb-2">Customer</th>
                <th className="pb-2">Tender</th>
                <th className="pb-2 text-right">Amount</th>
                <th className="pb-2 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {recent_transactions.map((t) => (
                <tr key={t.id} className="hover:bg-slate-800/40 transition">
                  <td className="py-2.5 font-bold text-white">{t.transaction_id}</td>
                  <td className="py-2.5">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      t.source === 'STORE' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-blue-500/10 text-blue-400'
                    }`}>
                      {t.source}
                    </span>
                  </td>
                  <td className="py-2.5 text-slate-300 font-sans">{t.store_name}</td>
                  <td className="py-2.5 text-slate-300 font-sans">{t.customer_name}</td>
                  <td className="py-2.5 text-slate-400">{t.payment_method}</td>
                  <td className="py-2.5 text-right font-bold text-white">₹{t.amount.toFixed(2)}</td>
                  <td className="py-2.5 text-center">
                    <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-semibold text-[10px]">
                      {t.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
