import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import {
  Database,
  BarChart3,
  TrendingUp,
  Globe,
  Calendar,
  Calculator,
  Bot,
  LayoutDashboard,
  ShieldCheck,
  ArrowRight,
  CheckCircle2,
  Sparkles,
} from 'lucide-react';

interface ArchitectureStep {
  step: number;
  name: string;
  status: string;
  details: string;
  metric: string;
}

export const NineStepArchitectureFlow: React.FC = () => {
  const [steps, setSteps] = useState<ArchitectureStep[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchArchitectureFlow();
  }, []);

  const fetchArchitectureFlow = async () => {
    try {
      setLoading(true);
      const data = await apiService.getArchitectureFlow();
      if (data && data.steps) {
        setSteps(data.steps);
      }
    } catch (err) {
      console.error('Failed to load architecture flow:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStepIcon = (name: string) => {
    switch (name) {
      case 'SQL Server':
        return Database;
      case 'Revenue Data':
        return BarChart3;
      case 'Forecasting':
        return TrendingUp;
      case 'Competitor Data':
        return Globe;
      case 'Events + Holidays':
        return Calendar;
      case 'Pricing Engine':
        return Calculator;
      case 'Single AI Agent':
        return Bot;
      case 'AI Revenue Dashboard':
        return LayoutDashboard;
      case 'Human Approval':
        return ShieldCheck;
      default:
        return Sparkles;
    }
  };

  const getStepColor = (step: number) => {
    const colors = [
      'from-blue-600/20 to-indigo-600/10 border-blue-500/40 text-blue-400',
      'from-indigo-600/20 to-cyan-600/10 border-indigo-500/40 text-indigo-400',
      'from-cyan-600/20 to-teal-600/10 border-cyan-500/40 text-cyan-400',
      'from-teal-600/20 to-emerald-600/10 border-teal-500/40 text-teal-400',
      'from-emerald-600/20 to-green-600/10 border-emerald-500/40 text-emerald-400',
      'from-green-600/20 to-amber-600/10 border-amber-500/40 text-amber-400',
      'from-amber-600/20 to-purple-600/10 border-purple-500/40 text-purple-400',
      'from-purple-600/20 to-pink-600/10 border-pink-500/40 text-pink-400',
      'from-pink-600/20 to-rose-600/10 border-rose-500/40 text-rose-400',
    ];
    return colors[(step - 1) % colors.length];
  };

  return (
    <div className="p-6 bg-slate-900/90 backdrop-blur-xl border border-indigo-500/30 rounded-3xl space-y-6 shadow-2xl relative overflow-hidden">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-indigo-600 to-purple-600 rounded-2xl shadow-lg shadow-indigo-600/30 text-white">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-black text-white flex items-center gap-2">
              Single AI Agent & End-to-End Revenue Data Pipeline
              <span className="px-2.5 py-0.5 bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 text-xs font-mono font-bold rounded-full">
                9-Step Architecture Verified
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              SQL Server ➔ Revenue Data ➔ Forecasting ➔ Competitor Data ➔ Events+Holidays ➔ Pricing Engine ➔ Single AI Agent ➔ Dashboard ➔ Human Approval
            </p>
          </div>
        </div>

        <button
          onClick={fetchArchitectureFlow}
          className="px-3.5 py-2 text-xs font-bold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700/80 rounded-xl border border-slate-700/60 transition-all flex items-center gap-2"
        >
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          Verify Pipeline Health
        </button>
      </div>

      {/* Pipeline Grid View */}
      {loading ? (
        <div className="flex justify-center items-center h-32">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-9 gap-3">
          {steps.map((st, idx) => {
            const Icon = getStepIcon(st.name);
            const color = getStepColor(st.step);

            return (
              <div
                key={st.step}
                className={`p-3 bg-gradient-to-b ${color} border rounded-2xl space-y-2 relative transition-all duration-300 hover:scale-[1.03] shadow-lg`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[9px] font-mono font-black text-white bg-slate-950/80 px-1.5 py-0.5 rounded border border-slate-800">
                    Step {st.step}
                  </span>
                  <Icon className="w-3.5 h-3.5" />
                </div>

                <div>
                  <h4 className="text-xs font-black text-white leading-tight">{st.name}</h4>
                  <p className="text-[10px] text-slate-400 mt-1 line-clamp-2">{st.details}</p>
                </div>

                <div className="pt-1 border-t border-slate-800/60 text-[9px] font-mono font-bold text-emerald-400">
                  {st.metric}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Horizontal Flow Indicator Sequence */}
      <div className="hidden lg:flex items-center justify-between p-3 bg-slate-950/80 border border-slate-800/80 rounded-2xl text-[11px] font-mono font-bold text-slate-300">
        <span className="text-blue-400">1. SQL Server</span>
        <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
        <span className="text-indigo-400">2. Revenue Data</span>
        <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
        <span className="text-cyan-400">3. Forecasting</span>
        <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
        <span className="text-teal-400">4. Competitor Data</span>
        <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
        <span className="text-emerald-400">5. Events + Holidays</span>
        <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
        <span className="text-amber-400">6. Pricing Engine</span>
        <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
        <span className="text-purple-400">7. Single AI Agent</span>
        <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
        <span className="text-pink-400">8. AI Revenue Dashboard</span>
        <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
        <span className="text-rose-400">9. Human Approval</span>
      </div>
    </div>
  );
};
