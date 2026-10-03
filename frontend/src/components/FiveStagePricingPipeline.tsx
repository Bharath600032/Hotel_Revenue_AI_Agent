import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import {
  BrainCircuit,
  Calculator,
  UserCheck,
  Send,
  Zap,
  Play,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  ShieldCheck,
  RotateCw,
} from 'lucide-react';

interface FiveStagePricingPipelineProps {
  hotelId?: number;
  refreshKey?: number;
  onCycleComplete?: () => void;
}

interface PipelineStatus {
  hotel_id: number;
  total_recommendations: number;
  stage_1_status: string;
  stage_2_status: string;
  stage_3_pending_approvals: number;
  stage_4_published_prices: number;
  stage_5_autonomous_mode: string;
  last_updated: string;
}

export const FiveStagePricingPipeline: React.FC<FiveStagePricingPipelineProps> = ({
  hotelId = 1,
  refreshKey = 0,
  onCycleComplete,
}) => {
  const [status, setStatus] = useState<PipelineStatus | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [cycleMetrics, setCycleMetrics] = useState<any>(null);
  const [activeStage, setActiveStage] = useState<number | null>(null);

  useEffect(() => {
    fetchStatus();
  }, [hotelId, refreshKey]);

  // Automatic status polling every 5 minutes (300,000 ms)
  useEffect(() => {
    const interval = setInterval(() => {
      fetchStatus();
    }, 300000);
    return () => clearInterval(interval);
  }, [hotelId]);

  const fetchStatus = async () => {
    try {
      const data = await apiService.getPipelineStatus(hotelId);
      setStatus(data);
    } catch (err) {
      console.error('Failed to load pipeline status:', err);
    }
  };

  const handleRunAutonomousCycle = async () => {
    try {
      setIsRunning(true);
      setActiveStage(1);

      // Visual step-by-step feedback
      setTimeout(() => setActiveStage(2), 500);
      setTimeout(() => setActiveStage(3), 1000);
      setTimeout(() => setActiveStage(4), 1500);
      setTimeout(() => setActiveStage(5), 2000);

      const result = await apiService.runAutonomousCycle(hotelId, 30);
      setCycleMetrics(result);
      await fetchStatus();
      if (onCycleComplete) onCycleComplete();
    } catch (err) {
      console.error('Autonomous pricing cycle failed:', err);
    } finally {
      setTimeout(async () => {
        setIsRunning(false);
        setActiveStage(null);
        await fetchStatus();
      }, 2200);
    }
  };

  const stages = [
    {
      num: 1,
      title: 'Stage 1',
      subtitle: 'AI Analyzes Data',
      desc: 'Occupancy, pickup pace, competitor median, local events & holidays',
      icon: BrainCircuit,
      color: 'from-blue-500/20 to-indigo-500/10 border-blue-500/30 text-blue-400',
      badge: status ? `${status.total_recommendations * 5} Signals` : 'Active',
      statusText: 'Continuous Data Crawl',
    },
    {
      num: 2,
      title: 'Stage 2',
      subtitle: 'AI Recommends Price',
      desc: 'Calculates dynamic base rate, confidence score & safety guardrails',
      icon: Calculator,
      color: 'from-indigo-500/20 to-violet-500/10 border-indigo-500/30 text-indigo-400',
      badge: status ? `${status.total_recommendations} Rates` : 'Calculated',
      statusText: 'Guardrails Enforced',
    },
    {
      num: 3,
      title: 'Stage 3',
      subtitle: 'Revenue Manager Approves',
      desc: 'Human approval queue flags high-impact rate changes ≥ 10%',
      icon: UserCheck,
      color: 'from-amber-500/20 to-orange-500/10 border-amber-500/30 text-amber-400',
      badge: status ? `${status.stage_3_pending_approvals} Pending` : 'Queue Ready',
      statusText: status?.stage_3_pending_approvals ? 'Action Required' : 'Queue Clear',
    },
    {
      num: 4,
      title: 'Stage 4',
      subtitle: 'System Publishes Price',
      desc: 'Deploys approved rates to live RoomInventory & booking engine',
      icon: Send,
      color: 'from-emerald-500/20 to-teal-500/10 border-emerald-500/30 text-emerald-400',
      badge: status ? `${status.stage_4_published_prices} Live` : 'Deployed',
      statusText: 'Sync Complete',
    },
    {
      num: 5,
      title: 'Stage 5',
      subtitle: 'Controlled Autonomous Pricing',
      desc: 'Feedback loop auto-publishes safe rates <10% and routes ≥10% to Manager',
      icon: Zap,
      color: 'from-purple-500/20 to-pink-500/10 border-purple-500/30 text-purple-400',
      badge: 'Controlled AI Active',
      statusText: '±10% Guardrail Limit',
    },
  ];

  return (
    <div className="p-6 bg-slate-900/90 backdrop-blur-xl border border-indigo-500/30 rounded-3xl space-y-6 shadow-2xl relative overflow-hidden">
      {/* Background Glow Effect */}
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header Bar */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div className="flex items-center gap-3.5">
          <div className="p-3 bg-indigo-500/10 rounded-2xl border border-indigo-500/30 text-indigo-400">
            <Sparkles className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-black text-white tracking-wide">
                5-Stage Controlled Autonomous Pricing Flow
              </h2>
              <span className="px-3 py-1 bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-bold rounded-full flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5" />
                Live Architecture
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Cute Orange Hotel • End-to-end multi-stage AI revenue execution pipeline
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchStatus}
            className="p-2.5 text-slate-400 hover:text-white bg-slate-800/80 hover:bg-slate-700/80 rounded-2xl border border-slate-700/50 transition-all"
            title="Refresh Status"
          >
            <RotateCw className="w-4 h-4" />
          </button>

          <button
            onClick={handleRunAutonomousCycle}
            disabled={isRunning}
            className={`px-5 py-3 text-xs font-extrabold rounded-2xl transition-all shadow-lg flex items-center gap-2 ${
              isRunning
                ? 'bg-indigo-600/50 text-indigo-200 cursor-not-allowed border border-indigo-500/30'
                : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-indigo-600/30 hover:scale-[1.02] active:scale-[0.98]'
            }`}
          >
            {isRunning ? (
              <>
                <RotateCw className="w-4 h-4 animate-spin text-white" />
                Executing Pipeline (Stage {activeStage || 1}/5)...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                Run 5-Stage Autonomous Cycle
              </>
            )}
          </button>
        </div>
      </div>

      {/* Cycle Metrics Alert if available */}
      {cycleMetrics && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl text-xs space-y-2 animate-fadeIn">
          <div className="flex items-center justify-between font-bold text-emerald-400">
            <span className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              Autonomous Pricing Cycle Completed Successfully
            </span>
            <span className="text-[10px] text-emerald-500 font-mono">
              Horizon: {cycleMetrics.horizon_days} Days
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-slate-300 pt-1 border-t border-emerald-500/20">
            <div>
              <span className="text-[10px] text-slate-500 uppercase font-bold">Stage 1 Analyzed</span>
              <p className="font-mono font-bold text-white">{cycleMetrics.stage_1_data_points_analyzed} Date Points</p>
            </div>
            <div>
              <span className="text-[10px] text-slate-500 uppercase font-bold">Stage 2 Recommended</span>
              <p className="font-mono font-bold text-white">{cycleMetrics.stage_2_recommendations_generated} Rates</p>
            </div>
            <div>
              <span className="text-[10px] text-slate-500 uppercase font-bold">Stage 3 Routed</span>
              <p className="font-mono font-bold text-amber-400">{cycleMetrics.stage_3_pending_approvals} Pending Manager</p>
            </div>
            <div>
              <span className="text-[10px] text-slate-500 uppercase font-bold">Stage 4 Published</span>
              <p className="font-mono font-bold text-emerald-400">{cycleMetrics.stage_4_auto_published} Auto-Deployed</p>
            </div>
          </div>
        </div>
      )}

      {/* 5-Stage Visual Workflow Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3.5 relative">
        {stages.map((st, index) => {
          const Icon = st.icon;
          const isActive = activeStage === st.num;

          return (
            <React.Fragment key={st.num}>
              <div
                className={`p-4 bg-gradient-to-b ${st.color} border rounded-2xl space-y-3 relative transition-all duration-300 ${
                  isActive
                    ? 'ring-2 ring-indigo-400 scale-105 shadow-xl shadow-indigo-500/20 bg-slate-800'
                    : 'hover:border-slate-600'
                }`}
              >
                {/* Stage Header */}
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-black uppercase font-mono tracking-wider px-2 py-0.5 bg-slate-900/80 rounded-full border border-slate-700/60 text-slate-300">
                    {st.title}
                  </span>
                  <div className={`p-1.5 rounded-xl bg-slate-900/70`}>
                    <Icon className="w-4 h-4" />
                  </div>
                </div>

                {/* Subtitle & Desc */}
                <div>
                  <h4 className="text-xs font-black text-white leading-snug">{st.subtitle}</h4>
                  <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">{st.desc}</p>
                </div>

                {/* Footer Badge */}
                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px]">
                  <span className="font-mono font-extrabold px-2 py-0.5 rounded-md bg-slate-900/90 text-white border border-slate-800">
                    {st.badge}
                  </span>
                  <span className="text-slate-500 font-medium">{st.statusText}</span>
                </div>
              </div>
            </React.Fragment>
          );
        })}
      </div>

      {/* Flow Diagram Connector Banner */}
      <div className="p-3 bg-slate-950/80 border border-slate-800/80 rounded-2xl flex flex-wrap items-center justify-around text-xs text-slate-400 gap-2 font-mono">
        <span className="text-blue-400 font-bold">Stage 1: AI Analyzes Data</span>
        <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
        <span className="text-indigo-400 font-bold">Stage 2: AI Recommends Price</span>
        <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
        <span className="text-amber-400 font-bold">Stage 3: Manager Approves</span>
        <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
        <span className="text-emerald-400 font-bold">Stage 4: System Publishes</span>
        <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
        <span className="text-purple-400 font-bold">Stage 5: Autonomous Pricing</span>
      </div>
    </div>
  );
};
