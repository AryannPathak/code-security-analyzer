import React, { useState, useEffect } from 'react';
import { Download, Search, Filter, ShieldAlert, CheckCircle2, AlertTriangle, FileSpreadsheet } from 'lucide-react';
import api from '../../services/api';

export default function TransactionManagement() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [source, setSource] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('');
  const [anomaliesOnly, setAnomaliesOnly] = useState(false);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const fetchTransactions = () => {
    setLoading(true);
    api.get('/transactions', {
      params: {
        page,
        per_page: 25,
        source: source || undefined,
        payment_method: paymentMethod || undefined,
        anomalies_only: anomaliesOnly || undefined,
        search: search || undefined,
      },
    })
      .then((res) => {
        if (res.data.success) {
          setTransactions(res.data.transactions);
          setTotal(res.data.total);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchTransactions();
  }, [page, source, paymentMethod, anomaliesOnly, search]);

  const handleDownloadCsv = () => {
    window.open('/api/transactions/export', '_blank');
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Centralized Transaction Ledger</h1>
          <p className="text-xs text-slate-400 mt-1">
            Single unified financial truth for {total.toLocaleString()} DMart physical retail and Amazon online transactions
          </p>
        </div>
        <button
          onClick={handleDownloadCsv}
          className="py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs flex items-center space-x-2 shadow-md transition self-start sm:self-center"
        >
          <FileSpreadsheet className="w-4 h-4" />
          <span>Export Transactions (CSV)</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Search transaction ID..."
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-800 focus:border-blue-500 text-xs text-white placeholder-slate-500 transition"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3 text-xs">
          <select
            value={source}
            onChange={(e) => { setSource(e.target.value); setPage(1); }}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white font-medium"
          >
            <option value="">All Channels (Online + Store)</option>
            <option value="STORE">DMart Store POS Only</option>
            <option value="ONLINE">Amazon Online E-Commerce</option>
          </select>

          <select
            value={paymentMethod}
            onChange={(e) => { setPaymentMethod(e.target.value); setPage(1); }}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white font-medium"
          >
            <option value="">All Tenders</option>
            <option value="CASH">Cash Tender</option>
            <option value="UPI">UPI Simulation</option>
            <option value="CARD">Debit / Credit Card</option>
            <option value="ONLINE_NETBANKING">Netbanking</option>
          </select>

          <button
            onClick={() => { setAnomaliesOnly(!anomaliesOnly); setPage(1); }}
            className={`py-2 px-3 rounded-xl border flex items-center space-x-1.5 font-semibold transition ${
              anomaliesOnly
                ? 'bg-rose-950/60 border-rose-500 text-rose-400'
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>AI Flagged Outliers</span>
          </button>
        </div>
      </div>

      {/* Ledger Table */}
      <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="text-slate-400 border-b border-slate-800">
              <th className="pb-3">Transaction ID</th>
              <th className="pb-3">Order Number</th>
              <th className="pb-3">Source Channel</th>
              <th className="pb-3">Store Branch</th>
              <th className="pb-3">Customer</th>
              <th className="pb-3">Payment Method</th>
              <th className="pb-3 text-right">Amount (₹)</th>
              <th className="pb-3 text-center">AI Anomaly Flag</th>
              <th className="pb-3 text-right">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {transactions.map((t) => (
              <tr key={t.id} className="hover:bg-slate-800/40 transition">
                <td className="py-3 font-bold text-white">{t.transaction_id}</td>
                <td className="py-3 text-slate-400">{t.order_number || 'N/A'}</td>
                <td className="py-3 font-sans">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    t.source === 'STORE' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-blue-500/10 text-blue-400'
                  }`}>
                    {t.source}
                  </span>
                </td>
                <td className="py-3 font-sans text-slate-300">{t.store_name}</td>
                <td className="py-3 font-sans text-slate-300">{t.customer_name}</td>
                <td className="py-3 text-slate-400">{t.payment_method}</td>
                <td className="py-3 text-right font-bold text-white">₹{t.amount.toFixed(2)}</td>
                <td className="py-3 text-center">
                  {t.is_flagged_anomaly ? (
                    <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 text-[10px] font-bold inline-flex items-center gap-1">
                      <ShieldAlert className="w-3 h-3" /> FLAGGED
                    </span>
                  ) : (
                    <span className="text-slate-600 font-sans text-[11px]">Normal</span>
                  )}
                </td>
                <td className="py-3 text-right text-slate-500 text-[11px]">
                  {t.created_at ? new Date(t.created_at).toLocaleString() : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
