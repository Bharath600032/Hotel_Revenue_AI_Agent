import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
  CartesianGrid,
} from 'recharts';
import { TrendingUp, DollarSign, Percent, Bed, ArrowUpRight, ShieldCheck, Sparkles } from 'lucide-react';
import { ApprovalQueueWidget } from '../components/ApprovalQueueWidget';
import { FiveStagePricingPipeline } from '../components/FiveStagePricingPipeline';
import { NineStepArchitectureFlow } from '../components/NineStepArchitectureFlow';

import { useHotel } from '../context/HotelContext';

const mockTrendData = [
  { date: 'Oct 01', Occupancy: 65, ADR: 5200, RevPAR: 3380 },
  { date: 'Oct 02', Occupancy: 70, ADR: 5400, RevPAR: 3780 },
  { date: 'Oct 03', Occupancy: 75, ADR: 5800, RevPAR: 4350 },
  { date: 'Oct 04', Occupancy: 82, ADR: 6200, RevPAR: 5084 },
  { date: 'Oct 05', Occupancy: 88, ADR: 6500, RevPAR: 5720 },
  { date: 'Oct 06', Occupancy: 92, ADR: 6800, RevPAR: 6256 },
  { date: 'Oct 07', Occupancy: 78, ADR: 5900, RevPAR: 4602 },
];

const mockCompData = [
  { hotel: 'Our Property', rate: 6200 },
  { hotel: 'Taj Coromandel', rate: 6500 },
  { hotel: 'The Park Chennai', rate: 6000 },
  { hotel: 'Radisson Blu', rate: 6800 },
  { hotel: 'ITC Grand Chola', rate: 7200 },
];

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { selectedHotel } = useHotel();
  const [activeTab, setActiveTab] = useState<'overview' | 'analytics' | 'approvals'>('overview');
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefreshData = () => {
    setRefreshKey((prev) => prev + 1);
  };

  const activeHotelId = selectedHotel?.hotel_id || 1;

  return (
    <div className="space-y-8 font-sans">
      {/* Top Banner & Action Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
            Revenue Performance Overview
            <span className="px-2.5 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs rounded-full font-bold">
              {selectedHotel?.hotel_name ? selectedHotel.hotel_name.toUpperCase() : 'CUTE ORANGE HOTEL'}
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">Real-time occupancy metrics, rate recommendations, and automated price guardrails.</p>
        </div>

        {/* Tab Selection Pills with Full Navigation */}
        <div className="flex items-center gap-2 bg-slate-900/80 p-1.5 rounded-2xl border border-slate-800">
          <button
            onClick={() => {
              setActiveTab('overview');
              navigate('/');
            }}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'overview'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => {
              setActiveTab('analytics');
              navigate('/revenue');
            }}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'analytics'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Analytics
          </button>
          <button
            onClick={() => {
              setActiveTab('approvals');
              navigate('/pricing');
            }}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === 'approvals'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <span>Approvals</span>
            <span className="px-1.5 py-0.2 bg-amber-500/20 text-amber-300 text-[10px] rounded-full font-extrabold">Queue</span>
          </button>
        </div>
      </div>

      {/* 9-STEP AI REVENUE PIPELINE ARCHITECTURE */}
      <NineStepArchitectureFlow />

      {/* 5-STAGE CONTROLLED AUTONOMOUS PRICING PIPELINE */}
      <FiveStagePricingPipeline hotelId={activeHotelId} onCycleComplete={handleRefreshData} />


      {/* Autonomous Rate Optimization Alert Card */}
      <div className="bg-gradient-to-r from-indigo-950/80 via-slate-900 to-slate-900 p-6 rounded-3xl border border-indigo-500/30 shadow-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="flex items-center space-x-2">
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <span>Autonomous AI Optimization Engine</span>
              <Sparkles className="w-4 h-4 text-amber-400 animate-pulse" />
            </h3>
            <span className="px-2 py-0.5 bg-indigo-500/20 text-indigo-300 text-[10px] font-bold rounded-full border border-indigo-500/30">
              Multi-Tenant AI Agent
            </span>
          </div>
          <p className="text-xs text-slate-300">
            Active demand signal for <strong className="text-white">{selectedHotel?.hotel_name || 'Cute Orange Hotel'}</strong>: <strong className="text-emerald-400">City Tech Summit & Festival Demand</strong> (+18% projected pickup uplift).
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="px-3.5 py-2 bg-slate-950/80 border border-slate-800 rounded-2xl text-xs font-semibold text-slate-300 flex items-center space-x-2 shadow-inner">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Guardrails Active (±20% Max Shift)</span>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid (Shadcn Metric Cards) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 backdrop-blur border border-slate-800 p-5 rounded-2xl space-y-3 shadow-xl hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Occupancy Rate</span>
            <div className="p-2 bg-emerald-500/10 rounded-xl border border-emerald-500/20">
              <Percent className="w-4 h-4 text-emerald-400" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-white">78.5%</span>
            <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20 flex items-center gap-0.5">
              +5.2% <ArrowUpRight className="w-3 h-3" />
            </span>
          </div>
          <p className="text-[11px] text-slate-500 font-medium">vs. previous period 73.3%</p>
        </div>

        <div className="bg-slate-900/80 backdrop-blur border border-slate-800 p-5 rounded-2xl space-y-3 shadow-xl hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Average Daily Rate</span>
            <div className="p-2 bg-indigo-500/10 rounded-xl border border-indigo-500/20">
              <DollarSign className="w-4 h-4 text-indigo-400" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-white">₹5,970</span>
            <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20 flex items-center gap-0.5">
              +₹320 <ArrowUpRight className="w-3 h-3" />
            </span>
          </div>
          <p className="text-[11px] text-slate-500 font-medium">Target Recommended ADR: ₹6,200</p>
        </div>

        <div className="bg-slate-900/80 backdrop-blur border border-slate-800 p-5 rounded-2xl space-y-3 shadow-xl hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">RevPAR</span>
            <div className="p-2 bg-amber-500/10 rounded-xl border border-amber-500/20">
              <TrendingUp className="w-4 h-4 text-amber-400" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-white">₹4,686</span>
            <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20 flex items-center gap-0.5">
              +8.4% <ArrowUpRight className="w-3 h-3" />
            </span>
          </div>
          <p className="text-[11px] text-slate-500 font-medium">TRevPAR (incl. F&B): ₹5,450</p>
        </div>

        <div className="bg-slate-900/80 backdrop-blur border border-slate-800 p-5 rounded-2xl space-y-3 shadow-xl hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">3-Day Room Pickup</span>
            <div className="p-2 bg-cyan-500/10 rounded-xl border border-cyan-500/20">
              <Bed className="w-4 h-4 text-cyan-400" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-white">+14 Rooms</span>
            <span className="text-xs font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded-full border border-cyan-500/20">
              Fast Pace
            </span>
          </div>
          <p className="text-[11px] text-slate-500 font-medium">Avg Lead Time: 14.2 Days</p>
        </div>
      </div>

      {/* Human Approval Queue Section */}
      {(activeTab === 'overview' || activeTab === 'approvals') && (
        <ApprovalQueueWidget hotelId={activeHotelId} />
      )}

      {/* Charts Grid */}
      {(activeTab === 'overview' || activeTab === 'analytics') && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Occupancy & RevPAR Performance Chart */}
          <div className="lg:col-span-2 bg-slate-900/80 backdrop-blur border border-slate-800 p-6 rounded-3xl space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
              <div>
                <h3 className="text-base font-extrabold text-white">7-Day Occupancy & RevPAR Trend</h3>
                <p className="text-xs text-slate-400">Historical performance vs. AI demand projection</p>
              </div>
              <span className="text-xs text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-full border border-indigo-500/20 font-mono font-bold">
                Live Data Stream
              </span>
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={mockTrendData}>
                  <defs>
                    <linearGradient id="colorRevPAR" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 12 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', color: '#fff', fontSize: '12px' }}
                  />
                  <Area type="monotone" dataKey="RevPAR" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#colorRevPAR)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Competitor Rate Positioning Bar Chart */}
          <div className="bg-slate-900/80 backdrop-blur border border-slate-800 p-6 rounded-3xl space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
              <div>
                <h3 className="text-base font-extrabold text-white">Competitor Rate Positioning</h3>
                <p className="text-xs text-slate-400">Market benchmark across Goa 5-star set</p>
              </div>
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={mockCompData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="hotel" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }} />
                  <Bar dataKey="rate" fill="#10b981" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};


