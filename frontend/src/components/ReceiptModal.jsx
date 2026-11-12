import React from 'react';
import { Printer, CheckCircle2, X } from 'lucide-react';

export default function ReceiptModal({ isOpen, onClose, receiptData }) {
  if (!isOpen || !receiptData) return null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="bg-white text-slate-900 rounded-2xl max-w-md w-full shadow-2xl overflow-hidden border border-slate-200 animate-in fade-in zoom-in-95 duration-200">
        {/* Receipt Header Actions */}
        <div className="bg-slate-100 px-6 py-3 border-b border-slate-200 flex items-center justify-between no-print">
          <div className="flex items-center space-x-2 text-emerald-600 font-semibold text-sm">
            <CheckCircle2 className="w-4 h-4" />
            <span>Transaction Approved</span>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Printable Thermal Receipt Content */}
        <div id="thermal-receipt" className="p-6 font-mono text-xs leading-relaxed">
          <div className="text-center pb-4 border-b border-dashed border-slate-300">
            <h2 className="text-xl font-bold font-sans tracking-tight text-slate-950 uppercase">
              SMARTFLOW RETAIL
            </h2>
            <p className="text-[11px] text-slate-600">{receiptData.store_name || 'DMart Retail Store'}</p>
            <p className="text-[10px] text-slate-500">{receiptData.store_location || 'Sector 18, Commercial Hub'}</p>
            <p className="text-[10px] text-slate-500 mt-1">GSTIN: 27AABCS1429B1Z8</p>
          </div>

          <div className="py-3 border-b border-dashed border-slate-300 space-y-1 text-[11px]">
            <div className="flex justify-between">
              <span className="text-slate-500">Bill No:</span>
              <span className="font-bold text-slate-900">{receiptData.bill_number}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Date:</span>
              <span>{receiptData.date}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Tender:</span>
              <span className="font-semibold text-emerald-700">{receiptData.payment_method}</span>
            </div>
            {receiptData.payment_ref && (
              <div className="flex justify-between">
                <span className="text-slate-500">Auth Ref:</span>
                <span className="text-[10px] text-slate-600">{receiptData.payment_ref}</span>
              </div>
            )}
          </div>

          {/* Line Items Table */}
          <div className="py-3 border-b border-dashed border-slate-300">
            <table className="w-full text-left">
              <thead>
                <tr className="text-slate-500 border-b border-slate-200">
                  <th className="pb-1">Item Description</th>
                  <th className="pb-1 text-center">Qty</th>
                  <th className="pb-1 text-right">Price</th>
                  <th className="pb-1 text-right">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-[11px]">
                {receiptData.items?.map((it, idx) => (
                  <tr key={idx} className="py-1">
                    <td className="py-1 truncate max-w-[130px] font-sans font-medium text-slate-800">{it.name}</td>
                    <td className="py-1 text-center">{it.quantity}</td>
                    <td className="py-1 text-right">₹{it.price}</td>
                    <td className="py-1 text-right font-semibold">₹{(it.quantity * it.price).toFixed(2)}</td>
                  </tr>
                )) || (
                  <tr>
                    <td colSpan="4" className="py-2 text-center text-slate-400">
                      Purchased items ({receiptData.items_count || 1} units)
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Totals Calculation */}
          <div className="py-3 border-b border-dashed border-slate-300 space-y-1.5 text-[11px]">
            <div className="flex justify-between text-slate-600">
              <span>Subtotal:</span>
              <span>₹{Number(receiptData.subtotal).toFixed(2)}</span>
            </div>
            {Number(receiptData.discount) > 0 && (
              <div className="flex justify-between text-emerald-600 font-medium">
                <span>Discount Applied:</span>
                <span>-₹{Number(receiptData.discount).toFixed(2)}</span>
              </div>
            )}
            <div className="flex justify-between text-slate-600">
              <span>GST (5% Included):</span>
              <span>₹{Number(receiptData.tax_5pct).toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-base font-bold text-slate-950 pt-2 border-t border-slate-300">
              <span>NET PAYABLE:</span>
              <span>₹{Number(receiptData.final_total).toFixed(2)}</span>
            </div>
          </div>

          {/* Barcode Graphic */}
          <div className="pt-4 text-center">
            <div className="inline-block bg-slate-900 text-white font-mono text-center px-4 py-1.5 tracking-[6px] text-xs font-bold rounded">
              ||||||||||||||||||||||||||
            </div>
            <p className="text-[10px] text-slate-500 mt-1">Thank you for shopping at SmartFlow!</p>
            <p className="text-[9px] text-slate-400">Please retain bill for warranty &amp; exchange</p>
          </div>
        </div>

        {/* Modal Bottom Buttons */}
        <div className="bg-slate-50 px-6 py-4 border-t border-slate-200 flex space-x-3 no-print">
          <button
            onClick={handlePrint}
            className="flex-1 inline-flex items-center justify-center space-x-2 py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm shadow-md transition"
          >
            <Printer className="w-4 h-4" />
            <span>Print Receipt</span>
          </button>
          <button
            onClick={onClose}
            className="flex-1 py-2.5 px-4 rounded-xl bg-slate-200 hover:bg-slate-300 text-slate-800 font-semibold text-sm transition"
          >
            New Transaction
          </button>
        </div>
      </div>
    </div>
  );
}
