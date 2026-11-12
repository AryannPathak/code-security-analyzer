import React, { useState, useEffect } from 'react';
import { 
  Cpu, 
  TrendingUp, 
  AlertTriangle, 
  Sparkles, 
  Package, 
  ShieldAlert, 
  CheckCircle2, 
  RefreshCw, 
  Layers, 
  BarChart3,
  Calendar,
  Zap
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import api from '../../services/api';

export default function AimlInsights() {
  const [salesForecast, setSalesForecast] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [demandForecast, setDemandForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [runningDetection, setRunningDetection] = useState(false);
  const [activeTab, setActiveTab] = useState('sales');

  const fetchAimlData = () => {
    setLoading(true);
    Promise.all([
      api.get('/ai/predict-sales?days_ahead=7'),
      api.get('/ai/recommendations?limit=8'),
      api.get('/ai/anomalies'),
      api.get('/ai/inventory-forecast?limit=25')
    ])
      .then(([salesRes, recRes, anomRes, demandRes]) => {
        if (salesRes.data.success) setSalesForecast(salesRes.data);
        if (recRes.data.success) setRecommendations(recRes.data.recommendations);
        if (anomRes.data.success) setAnomalies(anomRes.data.anomalies);
        if (demandRes.data.success) setDemandForecast(demandRes.data.forecasts);
      })
      .catch((err) => console.error('Error fetching AIML data', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAimlData();
  }, []);

  const handleRunAnomalyDetection = async () => {
    setRunningDetection(true);
    try {
      const res = await api.post('/ai/anomalies/run-detection?contamination=0.04');
      if (res.data.success) {
        alert(res.data.results.message);
        fetchAimlData();
      }
    } catch (err) {
      alert(err.response?.data?.error || 'Anomaly detection failed.');
    } finally {
      setRunningDetection(false);
    }
  };

  if (loading) {
    return <div className="py-20 text-center text-slate-500 font-mono text-sm">Evaluating AIML Predictive Engines...</div>;
  }

  // Feature 1: Actual vs Predicted Sales Chart
  const salesChartData = salesForecast ? {
    labels: salesForecast.history_comparison?.map((d) => d.display_date) || [],
    datasets: [
      {
        label: 'Actual Historical Sales (₹)',
        data: salesForecast.history_comparison?.map((d) => d.actual) || [],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.3,
        borderWidth: 2,
      },
      {
        label: 'Linear Regression Fit (₹)',
        data: salesForecast.history_comparison?.map((d) => d.predicted) || [],
        borderColor: '#38bdf8',
        borderDash: [5, 5],
        tension: 0.3,
        borderWidth: 2,
      },
    ],
  } : null;

  // Next 7-Day Forecast Bar Chart
  const forecastBarData = salesForecast ? {
    labels: salesForecast.future_forecast?.map((f) => `${f.display_date} (${f.day_name.slice(0, 3)})`) || [],
    datasets: [
      {
        label: 'Predicted Sales Forecast (₹)',
        data: salesForecast.future_forecast?.map((f) => f.predicted_sales) || [],
        backgroundColor: '#3b82f6',
        borderRadius: 8,
      },
    ],
  } : null;

  return (
    <div className="space-y-8 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-3xl font-bold text-white tracking-tight">AIML Intelligence Hub</h1>
            <span className="px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-mono font-semibold">
              4 Applied Models
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Scikit-Learn &amp; algorithmic machine learning pipelines integrated into enterprise retail operations
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center space-x-1 p-1 rounded-2xl bg-slate-900 border border-slate-800 text-xs font-medium">
          <button
            onClick={() => setActiveTab('sales')}
            className={`px-3 py-1.5 rounded-xl transition ${
              activeTab === 'sales' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
            }`}
          >
            1. Sales Forecast
          </button>
          <button
            onClick={() => setActiveTab('recommendation')}
            className={`px-3 py-1.5 rounded-xl transition ${
              activeTab === 'recommendation' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
            }`}
          >
            2. Recommendations
          </button>
          <button
            onClick={() => setActiveTab('anomaly')}
            className={`px-3 py-1.5 rounded-xl transition ${
              activeTab === 'anomaly' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
            }`}
          >
            3. Unusual Txns
          </button>
          <button
            onClick={() => setActiveTab('demand')}
            className={`px-3 py-1.5 rounded-xl transition ${
              activeTab === 'demand' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
            }`}
          >
            4. Stock Demand
          </button>
        </div>
      </div>

      {/* ============================================================== */}
      {/* TAB 1: SALES PREDICTION (LINEAR REGRESSION) */}
      {/* ============================================================== */}
      {activeTab === 'sales' && salesForecast && (
        <div className="space-y-6">
          {/* Model Metrics Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 text-center">
              <span className="text-[11px] font-semibold text-slate-400 block mb-1">Mean Absolute Error (MAE)</span>
              <span className="text-xl font-black text-white font-mono">₹{salesForecast.metrics.mae}</span>
              <span className="text-[10px] text-slate-500 block mt-1">Average forecast variance</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 text-center">
              <span className="text-[11px] font-semibold text-slate-400 block mb-1">Root Mean Squared Error (RMSE)</span>
              <span className="text-xl font-black text-white font-mono">₹{salesForecast.metrics.rmse}</span>
              <span className="text-[10px] text-slate-500 block mt-1">Penalizes large errors</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 text-center">
              <span className="text-[11px] font-semibold text-slate-400 block mb-1">R² Goodness of Fit</span>
              <span className="text-xl font-black text-emerald-400 font-mono">{salesForecast.metrics.r2_score}</span>
              <span className="text-[10px] text-emerald-500 block mt-1">High correlation fit (&gt; 0.80)</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 text-center">
              <span className="text-[11px] font-semibold text-slate-400 block mb-1">Algorithm Used</span>
              <span className="text-base font-bold text-sky-400 block mt-1">Linear Regression</span>
              <span className="text-[10px] text-slate-500 font-mono">OLS Normal Equations</span>
            </div>
          </div>

          {/* Actual vs Predicted Graph */}
          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div>
                <h3 className="font-bold text-white text-base">Historical Actual vs. Model Predicted Sales</h3>
                <p className="text-xs text-slate-400">Validating Linear Regression convergence on historical daily sales</p>
              </div>
              <span className="text-xs font-mono text-emerald-400">Green: Actual &bull; Blue: OLS Fit</span>
            </div>
            <div className="h-64">
              {salesChartData && (
                <Line
                  data={salesChartData}
                  options={{
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#94a3b8' } } },
                    scales: {
                      x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
                      y: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } },
                    },
                  }}
                />
              )}
            </div>
          </div>

          {/* Next 7-Day Forecast */}
          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div>
                <h3 className="font-bold text-white text-base">Next 7-Day Sales Volume Forecast</h3>
                <p className="text-xs text-slate-400">Extrapolated forward from calendar &amp; day-of-week trend features</p>
              </div>
              <span className="text-xs font-mono text-blue-400">Future Projections</span>
            </div>
            <div className="h-56">
              {forecastBarData && (
                <Bar
                  data={forecastBarData}
                  options={{
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                      x: { ticks: { color: '#94a3b8', font: { size: 10 } } },
                      y: { ticks: { color: '#94a3b8' } },
                    },
                  }}
                />
              )}
            </div>
          </div>
        </div>
      )}

      {/* ============================================================== */}
      {/* TAB 2: PRODUCT RECOMMENDATIONS (POPULARITY RANKING) */}
      {/* ============================================================== */}
      {activeTab === 'recommendation' && (
        <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h3 className="font-bold text-white text-base">Trending Product Recommendations</h3>
              <p className="text-xs text-slate-400">
                Algorithm: Normalized popularity frequency across 10,000+ transaction line items
              </p>
            </div>
            <span className="text-xs font-mono text-blue-400">Collaborative Frequency Engine</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-400 border-b border-slate-800">
                  <th className="pb-2">Rank</th>
                  <th className="pb-2">Product Name</th>
                  <th className="pb-2">Brand</th>
                  <th className="pb-2">SKU</th>
                  <th className="pb-2 text-right">Selling Price</th>
                  <th className="pb-2 text-center">Historical Units Sold</th>
                  <th className="pb-2 text-right">Popularity Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {recommendations.map((p, idx) => (
                  <tr key={p.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 font-bold text-amber-400">#{idx + 1}</td>
                    <td className="py-3 font-sans font-semibold text-white">{p.name}</td>
                    <td className="py-3 font-sans text-slate-300">{p.brand}</td>
                    <td className="py-3 text-slate-400">{p.sku}</td>
                    <td className="py-3 text-right font-bold text-white">₹{p.price}</td>
                    <td className="py-3 text-center text-emerald-400 font-bold">{p.total_units_sold} units</td>
                    <td className="py-3 text-right text-blue-400 font-bold">{p.popularity_score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ============================================================== */}
      {/* TAB 3: UNUSUAL TRANSACTION DETECTION (ISOLATION FOREST) */}
      {/* ============================================================== */}
      {activeTab === 'anomaly' && (
        <div className="space-y-6">
          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
              <div>
                <h3 className="font-bold text-white text-base">Isolation Forest Anomaly Inspector</h3>
                <p className="text-xs text-slate-400">
                  Unsupervised outlier detection: flags statistical deviations in spend velocity &amp; tender distribution
                </p>
              </div>
              <button
                disabled={runningDetection}
                onClick={handleRunAnomalyDetection}
                className="py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold text-xs flex items-center space-x-2 transition self-start sm:self-center"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${runningDetection ? 'animate-spin' : ''}`} />
                <span>{runningDetection ? 'Scanning 10,000 Txns...' : 'Run Isolation Forest Scan'}</span>
              </button>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 text-xs text-slate-400 leading-relaxed">
              <strong className="text-white">College Project Safety Principle:</strong> Isolation Forest identifies statistical outliers for administrator review. Legitimate transactions are not automatically blocked, ensuring real-world checkout safety.
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="text-slate-400 border-b border-slate-800">
                    <th className="pb-2">Transaction ID</th>
                    <th className="pb-2">Source</th>
                    <th className="pb-2">Payment Method</th>
                    <th className="pb-2 text-right">Amount (₹)</th>
                    <th className="pb-2 text-center">Anomaly Score</th>
                    <th className="pb-2">Detection Reason</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {anomalies.map((anom) => (
                    <tr key={anom.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-2.5 font-bold text-rose-400">{anom.transaction_id}</td>
                      <td className="py-2.5">{anom.source}</td>
                      <td className="py-2.5">{anom.payment_method}</td>
                      <td className="py-2.5 text-right font-bold text-white">₹{anom.amount.toFixed(2)}</td>
                      <td className="py-2.5 text-center text-rose-400 font-bold">{anom.anomaly_score}</td>
                      <td className="py-2.5 font-sans text-slate-300">
                        Statistical outlier in {anom.payment_method} amount distribution
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================== */}
      {/* TAB 4: INVENTORY DEMAND PREDICTION (MOVING AVERAGE) */}
      {/* ============================================================== */}
      {activeTab === 'demand' && (
        <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h3 className="font-bold text-white text-base">Moving Average Inventory Demand &amp; Restock Estimator</h3>
              <p className="text-xs text-slate-400">
                Algorithm: Blended 7-Day &amp; 30-Day moving average daily sales rate projection
              </p>
            </div>
            <span className="text-xs font-mono text-emerald-400">Demand Model Active</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-400 border-b border-slate-800">
                  <th className="pb-2">Store Branch</th>
                  <th className="pb-2">Product Name</th>
                  <th className="pb-2">SKU</th>
                  <th className="pb-2 text-center">Stock</th>
                  <th className="pb-2 text-center">7d Sales</th>
                  <th className="pb-2 text-center">Daily Demand</th>
                  <th className="pb-2 text-center">Runway (Days)</th>
                  <th className="pb-2 text-center">Priority</th>
                  <th className="pb-2 text-right">Suggested Reorder</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {demandForecast.map((f) => (
                  <tr key={f.inventory_id} className="hover:bg-slate-800/40 transition">
                    <td className="py-2.5 font-sans font-medium text-slate-300">{f.store_name}</td>
                    <td className="py-2.5 font-sans font-semibold text-white">{f.product_name}</td>
                    <td className="py-2.5 text-slate-400">{f.sku}</td>
                    <td className="py-2.5 text-center font-bold text-white">{f.current_stock}</td>
                    <td className="py-2.5 text-center text-slate-300">{f.sales_7d}</td>
                    <td className="py-2.5 text-center text-blue-400">{f.daily_demand_rate}/day</td>
                    <td className="py-2.5 text-center font-bold text-amber-400">{f.days_remaining}d</td>
                    <td className="py-2.5 text-center">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        f.priority === 'CRITICAL'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : f.priority === 'HIGH'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      }`}>
                        {f.priority}
                      </span>
                    </td>
                    <td className="py-2.5 text-right font-bold text-emerald-400">+{f.suggested_reorder} units</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
