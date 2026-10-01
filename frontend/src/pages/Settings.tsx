import React from 'react';
import { Settings as SettingsIcon, Shield, Cpu, Database, CheckCircle2, Lock } from 'lucide-react';

export const Settings: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <SettingsIcon className="w-7 h-7 text-indigo-400" />
          System Configuration & AI Agent Settings
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Review execution modes, AI foundation model selection, and deterministic guardrail configurations.
        </p>
      </div>

      {/* Execution Mode Card */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Database className="w-5 h-5 text-emerald-400" />
          Active Execution Mode
        </h3>

        <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">DEMO MODE (Active)</span>
            <p className="text-xs text-slate-300 mt-1">
              Zero external paid dependencies. Operating on local SQLite DB & seeded synthetic dataset (5 properties, 365-day horizon).
            </p>
          </div>
          <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 text-xs font-bold rounded-full">
            Local Fallback
          </span>
        </div>
      </div>

      {/* AI Model Configuration */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Cpu className="w-5 h-5 text-indigo-400" />
          Foundation LLM & ReAct Orchestrator
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-2">
            <span className="text-xs text-slate-400">LLM Provider</span>
            <p className="text-lg font-bold text-white">Gemini / Claude / Local Fallback</p>
            <span className="text-[10px] text-indigo-400">22+ Autonomous Domain Tools Connected</span>
          </div>

          <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-2">
            <span className="text-xs text-slate-400">Vector Embeddings Store</span>
            <p className="text-lg font-bold text-white">FAISS Vector Engine</p>
            <span className="text-[10px] text-emerald-400 font-semibold">Loaded Strategy Documents & SOPs</span>
          </div>
        </div>
      </div>

      {/* Safety & Compliance */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Shield className="w-5 h-5 text-amber-400" />
          Deterministic Safety Rules & Thresholds
        </h3>

        <div className="space-y-3 text-xs">
          <div className="flex justify-between items-center p-3 bg-slate-950/60 rounded-xl border border-slate-800">
            <span className="text-slate-300">Mandatory Human Approval Threshold</span>
            <span className="font-bold text-amber-400">Rate variation &gt; 10.0%</span>
          </div>

          <div className="flex justify-between items-center p-3 bg-slate-950/60 rounded-xl border border-slate-800">
            <span className="text-slate-300">Hard Daily Rate Ceiling Shift Limit</span>
            <span className="font-bold text-emerald-400">Max ±20.0% per 24 hours</span>
          </div>

          <div className="flex justify-between items-center p-3 bg-slate-950/60 rounded-xl border border-slate-800">
            <span className="text-slate-300">Minimum Price Floor Guardrail</span>
            <span className="font-bold text-white">₹3,500 Absolute Floor</span>
          </div>
        </div>
      </div>
    </div>
  );
};
