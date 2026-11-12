import React from 'react';
import { Activity, ShieldCheck, Cpu } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-800 bg-slate-950/80 py-8 text-xs text-slate-500 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
            <Activity className="w-3.5 h-3.5" />
          </div>
          <span className="font-bold text-slate-300">SMARTFLOW</span>
          <span>&bull; AI-Powered Omnichannel Retail &amp; E-Commerce Architecture</span>
        </div>

        <div className="flex items-center space-x-6 text-[11px]">
          <span className="flex items-center gap-1 text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
            Row-Lock Concurrency &bull; Idempotent Checkout
          </span>
          <span className="flex items-center gap-1 text-slate-400">
            <Cpu className="w-3.5 h-3.5 text-blue-400" />
            4 Machine Learning Pipelines
          </span>
          <span>3rd-Year AIML Major Project</span>
        </div>
      </div>
    </footer>
  );
}
