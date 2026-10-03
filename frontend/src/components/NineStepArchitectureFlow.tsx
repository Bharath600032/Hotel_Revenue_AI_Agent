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
  RefreshCw,
} from 'lucide-react';

interface ArchitectureStep {
  step: number;
  name: string;
  status: string;
  details: string;
  metric: string;
}

interface NineStepArchitectureFlowProps {
  hotelId?: number;
  refreshKey?: number;
  onRefresh?: () => void;
}

export const NineStepArchitectureFlow: React.FC<NineStepArchitectureFlowProps> = ({
  hotelId,
  refreshKey = 0,
  onRefresh,
}) => {
  const [steps, setSteps] = useState<ArchitectureStep[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [lastSyncTime, setLastSyncTime] = useState<string>('');

  const fetchArchitectureFlow = async (showLoadingState = false) => {
    try {
      if (showLoadingState) setLoading(true);
      setIsRefreshing(true);
      const data = await apiService.getArchitectureFlow(hotelId);
      if (data && data.steps) {
        setSteps(data.steps);
      }
      setLastSyncTime(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Failed to load architecture flow:', err);
    } finally {
      setLoading(false);
      setTimeout(() => setIsRefreshing(false), 500);
    }
  };

  useEffect(() => {
    fetchArchitectureFlow(true);
  }, [hotelId, refreshKey]);

  // Real-time auto-polling every 5 minutes (300,000 ms)
  useEffect(() => {
    const interval = setInterval(() => {
      fetchArchitectureFlow(false);
    }, 300000);
    return () => clearInterval(interval);
  }, [hotelId]);

  // Global event listeners for immediate state updates
  useEffect(() => {
    const handleGlobalUpdate = () => {
      fetchArchitectureFlow(false);
    };

    window.addEventListener('pipeline-data-updated', handleGlobalUpdate);
    window.addEventListener('recommendation-approved', handleGlobalUpdate);
    window.addEventListener('hotel-data-changed', handleGlobalUpdate);

    return () => {
      window.removeEventListener('pipeline-data-updated', handleGlobalUpdate);
      window.removeEventListener('recommendation-approved', handleGlobalUpdate);
      window.removeEventListener('hotel-data-changed', handleGlobalUpdate);
    };
  }, [hotelId]);

  const handleManualSync = async () => {
    await fetchArchitectureFlow(true);
    window.dispatchEvent(new Event('pipeline-data-updated'));
    if (onRefresh) onRefresh();
  };

  const handleManualVerify = async () => {
    await fetchArchitectureFlow(true);
    if (onRefresh) onRefresh();
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
      {/* Dynamic Background Glow Effect */}
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none"></div>

      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-indigo-600 to-purple-600 rounded-2xl shadow-lg shadow-indigo-600/30 text-white relative">
            <Bot className="w-5 h-5" />
            <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
          </div>
          <div>
            <h3 className="text-base font-black text-white flex flex-wrap items-center gap-2">
              <span>Single AI Agent & End-to-End Revenue Data Pipeline</span>
              <span className="px-2.5 py-0.5 bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 text-xs font-mono font-bold rounded-full">
                9-Step Architecture Verified
              </span>
              <span className="flex items-center gap-1.5 px-2.5 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono font-bold rounded-full">
                <span className="relative flex h-1.5 w-1.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
                </span>
                LIVE AUTO-SYNC (5m)
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              SQL Server ➔ Revenue Data ➔ Forecasting ➔ Competitor Data ➔ Events+Holidays ➔ Pricing Engine ➔ Single AI Agent ➔ Dashboard ➔ Human Approval
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleManualSync}
            disabled={isRefreshing}
            className="px-3.5 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-xl transition-all flex items-center gap-2 shadow-lg shadow-indigo-600/20 cursor-pointer"
            title="Trigger Manual Pipeline Data Sync Now"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'Syncing...' : 'Manual Sync Now'}</span>
          </button>

          <button
            onClick={handleManualVerify}
            disabled={isRefreshing && loading}
            className="px-3.5 py-2 text-xs font-bold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700/80 rounded-xl border border-slate-700/60 transition-all flex items-center gap-2 shadow-sm cursor-pointer"
          >
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Verify Pipeline Health</span>
            {lastSyncTime && (
              <span className="text-[10px] text-slate-400 font-mono">({lastSyncTime})</span>
            )}
          </button>
        </div>
      </div>

      {/* Pipeline Grid View */}
      {loading ? (
        <div className="flex justify-center items-center h-32">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-9 gap-3">
          {steps.map((st) => {
            const Icon = getStepIcon(st.name);
            const color = getStepColor(st.step);

            return (
              <div
                key={st.step}
                className={`p-3 bg-gradient-to-b ${color} border rounded-2xl space-y-2 relative transition-all duration-300 hover:scale-[1.03] shadow-lg flex flex-col justify-between`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[9px] font-mono font-black text-white bg-slate-950/80 px-1.5 py-0.5 rounded border border-slate-800">
                      Step {st.step}
                    </span>
                    <Icon className="w-3.5 h-3.5" />
                  </div>

                  <h4 className="text-xs font-black text-white leading-tight">{st.name}</h4>
                  <p className="text-[10px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">{st.details}</p>
                </div>

                <div className="pt-2 border-t border-slate-800/60 text-[9px] font-mono font-bold text-emerald-400 flex items-center justify-between">
                  <span className="truncate">{st.metric}</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Horizontal Flow Indicator Sequence */}
      <div className="hidden lg:flex items-center justify-between p-3 bg-slate-950/80 border border-slate-800/80 rounded-2xl text-[11px] font-mono font-bold text-slate-300">
        <span className="text-blue-400 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-ping"></span>
          1. SQL Server
        </span>
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
        <span className="text-rose-400 flex items-center gap-1.5">
          9. Human Approval
          <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-ping"></span>
        </span>
      </div>
    </div>
  );
};
