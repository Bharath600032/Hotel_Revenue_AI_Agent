import React, { useEffect, useState } from 'react';
import { useHotel } from '../context/HotelContext';
import { apiService } from '../services/api';
import {
  GroupDisplacementRequest,
  GroupDisplacementResponse,
  LOSRuleResponse,
} from '../types';
import {
  Users,
  Calculator,
  Calendar,
  IndianRupee,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  XCircle,
  AlertTriangle,
  RefreshCw,
  ShieldCheck,
  Edit3,
  Layers,
  Sparkles,
  Sliders,
  History,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

const getTodayDateString = () => new Date().toISOString().split('T')[0];
const getFutureDateString = (days: number) =>
  new Date(Date.now() + days * 86400000).toISOString().split('T')[0];

const formatINR = (val: number) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(val);

export const GroupDisplacement: React.FC = () => {
  const { selectedHotel } = useHotel();
  const hotelId = selectedHotel?.hotel_id || 1;

  const [activeTab, setActiveTab] = useState<'calculator' | 'los_rules' | 'audit_logs'>('calculator');

  // Group Calculator Form state
  const [startDate, setStartDate] = useState(getFutureDateString(3));
  const [endDate, setEndDate] = useState(getFutureDateString(10));
  const [roomsRequested, setRoomsRequested] = useState<number>(20);
  const [offeredRate, setOfferedRate] = useState<number>(7500);
  const [fAndBRevenue, setFAndBRevenue] = useState<number>(85000);
  const [meetingRental, setMeetingRental] = useState<number>(45000);
  const [otherAncillary, setOtherAncillary] = useState<number>(15000);

  const [evaluating, setEvaluating] = useState<boolean>(false);
  const [evalResult, setEvalResult] = useState<GroupDisplacementResponse | null>(null);

  // LOS Rules state
  const [losStartDate, setLosStartDate] = useState(getTodayDateString());
  const [losEndDate, setLosEndDate] = useState(getFutureDateString(14));
  const [losRules, setLosRules] = useState<LOSRuleResponse[]>([]);
  const [loadingLOS, setLoadingLOS] = useState<boolean>(false);
  const [editingRule, setEditingRule] = useState<LOSRuleResponse | null>(null);
  const [editMlos, setEditMlos] = useState<number>(1);
  const [editCta, setEditCta] = useState<boolean>(false);
  const [editCtd, setEditCtd] = useState<boolean>(false);

  // History state
  const [evaluationLogs, setEvaluationLogs] = useState<any[]>([]);
  const [loadingLogs, setLoadingLogs] = useState<boolean>(false);

  useEffect(() => {
    fetchEvaluationLogs();
    runInitial7DayEvaluation();
    if (activeTab === 'los_rules') {
      fetchLOSRules(losStartDate, losEndDate);
    }
  }, [hotelId, activeTab]);

  const runInitial7DayEvaluation = async () => {
    try {
      const sDate = getFutureDateString(3);
      const eDate = getFutureDateString(10);
      const payload: GroupDisplacementRequest = {
        hotel_id: hotelId,
        start_date: sDate,
        end_date: eDate,
        rooms_requested: 20,
        offered_rate: 7500,
        f_and_b_revenue: 85000,
        meeting_room_rental: 45000,
        other_ancillary_revenue: 15000,
      };
      const response = await apiService.evaluateGroupDisplacement(payload);
      setEvalResult(response);
    } catch (err) {
      console.warn('Initial 7-day evaluation fetch fallback:', err);
    }
  };

  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchLOSRules = async (sDate?: string, eDate?: string) => {
    try {
      setLoadingLOS(true);
      const start = sDate || losStartDate;
      const end = eDate || losEndDate;
      let days = 14;
      if (start && end) {
        const d1 = new Date(start).getTime();
        const d2 = new Date(end).getTime();
        const diff = Math.ceil((d2 - d1) / (1000 * 3600 * 24));
        if (diff > 0) days = diff;
      }
      const rules = await apiService.getLOSRules(hotelId, start, days);
      setLosRules(rules);
    } catch (err: any) {
      console.error('Failed to fetch LOS rules:', err);
    } finally {
      setLoadingLOS(false);
    }
  };

  const fetchEvaluationLogs = async () => {
    try {
      setLoadingLogs(true);
      const logs = await apiService.getGroupDisplacementLogs(hotelId);
      setEvaluationLogs(logs);
    } catch (err: any) {
      console.error('Failed to fetch evaluation logs:', err);
    } finally {
      setLoadingLogs(false);
    }
  };

  const handleEvaluate = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    try {
      setEvaluating(true);
      const payload: GroupDisplacementRequest = {
        hotel_id: hotelId,
        start_date: startDate,
        end_date: endDate,
        rooms_requested: Number(roomsRequested),
        offered_rate: Number(offeredRate),
        f_and_b_revenue: Number(fAndBRevenue),
        meeting_room_rental: Number(meetingRental),
        other_ancillary_revenue: Number(otherAncillary),
      };
      const response = await apiService.evaluateGroupDisplacement(payload);
      setEvalResult(response);
      fetchEvaluationLogs();
    } catch (err: any) {
      console.error('Error evaluating group displacement:', err);
      const detail = err.response?.data?.detail;
      setErrorMsg(typeof detail === 'string' ? detail : 'Failed to evaluate group displacement. Please verify inputs.');
    } finally {
      setEvaluating(false);
    }
  };

  const handleSaveLOSRule = async () => {
    if (!editingRule) return;
    try {
      await apiService.updateLOSRule(hotelId, editingRule.stay_date, {
        min_length_of_stay: editMlos,
        closed_to_arrival: editCta,
        closed_to_departure: editCtd,
      });
      setEditingRule(null);
      fetchLOSRules();
    } catch (err: any) {
      console.error('Failed to update LOS rule:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-2 border-b border-slate-800/60">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-3 tracking-tight">
            <Users className="w-7 h-7 text-indigo-400 flex-shrink-0" />
            <span>Group Displacement & Length of Stay (LOS) AI</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Quantify transient revenue cannibalization, compute exact group breakeven rate thresholds in INR (₹), and automate MLOS/CTA/CTD restrictions.
          </p>
        </div>

        {/* Tab Navigation Controls */}
        <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-1.5 rounded-xl flex-shrink-0">
          <button
            onClick={() => setActiveTab('calculator')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'calculator'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            <Calculator className="w-4 h-4" />
            <span>Displacement Calculator (INR)</span>
          </button>
          <button
            onClick={() => setActiveTab('los_rules')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'los_rules'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            <Sliders className="w-4 h-4" />
            <span>LOS & MLOS Restrictions</span>
          </button>
          <button
            onClick={() => setActiveTab('audit_logs')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'audit_logs'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            <History className="w-4 h-4" />
            <span>Audit History Log</span>
          </button>
        </div>
      </div>


      {/* TAB 1: GROUP DISPLACEMENT CALCULATOR */}
      {activeTab === 'calculator' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Form Column */}
          <div className="lg:col-span-4 bg-slate-900 border border-slate-800/80 rounded-2xl p-6 shadow-xl space-y-5">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-4">
              <Calculator className="w-5 h-5 text-indigo-400" />
              <h2 className="text-lg font-semibold text-white">Group Lead Inputs (INR ₹)</h2>
            </div>

            <form onSubmit={handleEvaluate} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1.5">
                  Arrival & Departure Dates
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    required
                    className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  />
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    required
                    className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1.5">
                  Rooms Requested per Night
                </label>
                <input
                  type="number"
                  min="1"
                  max="500"
                  value={roomsRequested}
                  onChange={(e) => setRoomsRequested(Number(e.target.value))}
                  required
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1.5">
                  Offered Group Room Rate (₹ INR / night)
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-2.5 text-slate-400 text-xs font-semibold">₹</span>
                  <input
                    type="number"
                    step="1"
                    min="1"
                    value={offeredRate}
                    onChange={(e) => setOfferedRate(Number(e.target.value))}
                    required
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-7 pr-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                  />
                </div>
              </div>

              <div className="border-t border-slate-800 pt-3 space-y-3">
                <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider block">
                  Ancillary Revenue Inputs (₹ INR)
                </span>

                <div>
                  <label className="text-xs text-slate-400 block mb-1">Total F&B Spend (₹ INR)</label>
                  <div className="relative">
                    <span className="absolute left-3 top-2 text-slate-500 text-xs">₹</span>
                    <input
                      type="number"
                      value={fAndBRevenue}
                      onChange={(e) => setFAndBRevenue(Number(e.target.value))}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-7 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-xs text-slate-400 block mb-1">Meeting Room Rental (₹ INR)</label>
                  <div className="relative">
                    <span className="absolute left-3 top-2 text-slate-500 text-xs">₹</span>
                    <input
                      type="number"
                      value={meetingRental}
                      onChange={(e) => setMeetingRental(Number(e.target.value))}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-7 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-xs text-slate-400 block mb-1">Other Ancillary (₹ INR)</label>
                  <div className="relative">
                    <span className="absolute left-3 top-2 text-slate-500 text-xs">₹</span>
                    <input
                      type="number"
                      value={otherAncillary}
                      onChange={(e) => setOtherAncillary(Number(e.target.value))}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-7 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                    />
                  </div>
                </div>
              </div>

              <button
                type="submit"
                disabled={evaluating}
                className="w-full mt-2 py-3 px-4 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-medium text-xs rounded-xl shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {evaluating ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Calculating Displacement in INR...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Evaluate Group Displacement (INR)
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Right Evaluation Results Column */}
          <div className="lg:col-span-8 space-y-6">
            {errorMsg && (
              <div className="p-4 bg-rose-950/80 border border-rose-700/60 rounded-xl text-rose-200 text-xs flex items-center gap-2">
                <XCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}
            {!evalResult ? (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center space-y-4">
                <div className="w-16 h-16 bg-indigo-500/10 text-indigo-400 rounded-2xl flex items-center justify-center mx-auto border border-indigo-500/20">
                  <Calculator className="w-8 h-8" />
                </div>
                <h3 className="text-lg font-semibold text-white">Run Group Lead Evaluation (INR ₹)</h3>
                <p className="text-slate-400 text-xs max-w-md mx-auto">
                  Submit group dates, room volume, and proposed rate in INR (₹) on the left to trigger the AI displacement engine.
                </p>
              </div>
            ) : (
              <>
                {/* Status Recommendation Card */}
                <div
                  className={`rounded-2xl p-6 border shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
                    evalResult.recommendation === 'ACCEPT'
                      ? 'bg-emerald-950/40 border-emerald-500/30'
                      : evalResult.recommendation === 'COUNTER_OFFER'
                      ? 'bg-amber-950/40 border-amber-500/30'
                      : 'bg-rose-950/40 border-rose-500/30'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    {evalResult.recommendation === 'ACCEPT' && (
                      <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl border border-emerald-500/30">
                        <CheckCircle className="w-8 h-8" />
                      </div>
                    )}
                    {evalResult.recommendation === 'COUNTER_OFFER' && (
                      <div className="p-3 bg-amber-500/20 text-amber-400 rounded-xl border border-amber-500/30">
                        <AlertTriangle className="w-8 h-8" />
                      </div>
                    )}
                    {evalResult.recommendation === 'REJECT' && (
                      <div className="p-3 bg-rose-500/20 text-rose-400 rounded-xl border border-rose-500/30">
                        <XCircle className="w-8 h-8" />
                      </div>
                    )}

                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">
                          AI Recommendation Decision
                        </span>
                        <span className="text-[10px] bg-slate-900 border border-slate-700 text-slate-300 px-2 py-0.5 rounded font-mono">
                          XAI Guardrails Passed
                        </span>
                      </div>
                      <h3 className="text-2xl font-bold text-white mt-1">
                        {evalResult.recommendation === 'ACCEPT' && 'ACCEPT GROUP BOOKING'}
                        {evalResult.recommendation === 'COUNTER_OFFER' && 'ISSUE COUNTER OFFER'}
                        {evalResult.recommendation === 'REJECT' && 'REJECT PROPOSED GROUP RATE'}
                      </h3>
                    </div>
                  </div>

                  <div className="text-right border-t md:border-t-0 md:border-l border-slate-800 pt-3 md:pt-0 md:pl-6">
                    <span className="text-xs text-slate-400 block">Recommended Action Rate</span>
                    <span className="text-2xl font-extrabold text-white">
                      {formatINR(
                        evalResult.recommendation === 'ACCEPT'
                          ? evalResult.offered_group_rate
                          : evalResult.recommended_counter_offer_rate
                      )}
                      <span className="text-xs text-slate-400 font-normal"> / room night</span>
                    </span>
                  </div>
                </div>

                {/* Key Financial Indicators Grid (INR) */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                    <span className="text-slate-400 text-xs">Total Room Nights</span>
                    <div className="text-xl font-bold text-white mt-1">
                      {evalResult.total_room_nights_requested}
                      <span className="text-xs text-slate-500 font-normal"> ({evalResult.total_nights} nights)</span>
                    </div>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                    <span className="text-slate-400 text-xs">Transient Displaced</span>
                    <div className="text-xl font-bold text-amber-400 mt-1">
                      -{formatINR(evalResult.total_transient_revenue_displaced)}
                    </div>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                    <span className="text-slate-400 text-xs">Gross Group + Ancillary</span>
                    <div className="text-xl font-bold text-emerald-400 mt-1">
                      +{formatINR(evalResult.total_gross_group_revenue)}
                    </div>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                    <span className="text-slate-400 text-xs">Breakeven Rate Floor</span>
                    <div className="text-xl font-bold text-indigo-400 mt-1">
                      {formatINR(evalResult.breakeven_group_rate)}
                    </div>
                  </div>
                </div>

                {/* Decision Rationale Box */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
                  <h4 className="text-xs font-semibold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4" />
                    AI Decision Rationale & Financial Breakdown (INR)
                  </h4>
                  <p className="text-slate-300 text-xs leading-relaxed font-mono bg-slate-950 p-4 rounded-xl border border-slate-800">
                    {evalResult.decision_rationale}
                  </p>
                </div>

                {/* Daily Displacement Chart */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-semibold text-white">Daily Revenue Displacement Breakdown (INR ₹)</h4>
                    <span className="text-xs text-indigo-400 font-mono font-semibold bg-indigo-500/10 px-2.5 py-1 rounded-lg border border-indigo-500/20">
                      {evalResult.daily_breakdown.length}-Day Daily Horizon Projected
                    </span>
                  </div>

                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={evalResult.daily_breakdown}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis dataKey="stay_date" stroke="#64748b" tick={{ fontSize: 11 }} />
                        <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                        <Tooltip
                          contentStyle={{ backgroundColor: '#0f172a', borderColor: '#f59e0b', borderRadius: '8px', fontSize: '12px', color: '#fff' }}
                          itemStyle={{ color: '#f8fafc', fontWeight: 600 }}
                          labelStyle={{ color: '#f59e0b', fontWeight: 700 }}
                          formatter={(value: any, name: any) => [
                            name.includes('Lost') ? formatINR(Number(value)) : value,
                            name,
                          ]}
                        />
                        <Legend wrapperStyle={{ fontSize: '12px' }} />
                        <Bar dataKey="displaced_transient_rooms" name="Displaced Rooms" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="transient_revenue_lost" name="Transient Revenue Lost (₹)" fill="#ef4444" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  {/* 7-Day Breakdown Table Grid */}
                  <div className="pt-4 border-t border-slate-800/80">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
                          <tr>
                            <th className="py-2.5 px-3">Stay Date</th>
                            <th className="py-2.5 px-3 text-center">Group Rooms</th>
                            <th className="py-2.5 px-3 text-center">Avail Capacity</th>
                            <th className="py-2.5 px-3 text-center">Displaced Rooms</th>
                            <th className="py-2.5 px-3 text-right">Transient ADR (₹)</th>
                            <th className="py-2.5 px-3 text-right">Revenue Lost (₹)</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/60 font-mono">
                          {evalResult.daily_breakdown.map((row: any, idx: number) => (
                            <tr key={idx} className="hover:bg-slate-800/40">
                              <td className="py-2.5 px-3 text-white font-sans font-medium">{row.stay_date}</td>
                              <td className="py-2.5 px-3 text-center text-slate-300 font-bold">{row.group_rooms || roomsRequested}</td>
                              <td className="py-2.5 px-3 text-center text-slate-400">{row.available_capacity ?? 80}</td>
                              <td className="py-2.5 px-3 text-center text-amber-400 font-bold">{row.displaced_transient_rooms}</td>
                              <td className="py-2.5 px-3 text-right text-slate-300">{formatINR(row.transient_rate || 8500)}</td>
                              <td className="py-2.5 px-3 text-right text-rose-400 font-bold">{formatINR(row.transient_revenue_lost)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: LENGTH OF STAY (LOS) RULES GRID */}
      {activeTab === 'los_rules' && (
        <div className="space-y-6">
          {/* Date Range Selector */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-4 rounded-2xl">
            <div>
              <h3 className="text-sm font-semibold text-white">Length of Stay (LOS) Restrictions Grid</h3>
              <p className="text-slate-400 text-xs">Manage Minimum Length of Stay (MLOS), Closed to Arrival (CTA), and Closed to Departure (CTD) controls.</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <input
                type="date"
                value={losStartDate}
                onChange={(e) => {
                  const val = e.target.value;
                  setLosStartDate(val);
                  if (val) fetchLOSRules(val, losEndDate);
                }}
                className="bg-slate-950 border border-slate-800 text-white px-3 py-1.5 rounded-lg"
              />
              <span className="text-slate-500">to</span>
              <input
                type="date"
                value={losEndDate}
                onChange={(e) => {
                  const val = e.target.value;
                  setLosEndDate(val);
                  if (val) fetchLOSRules(losStartDate, val);
                }}
                className="bg-slate-950 border border-slate-800 text-white px-3 py-1.5 rounded-lg"
              />
              <button
                onClick={() => fetchLOSRules(losStartDate, losEndDate)}
                className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors flex items-center gap-1.5"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingLOS ? 'animate-spin' : ''}`} />
                Fetch Rules
              </button>
            </div>
          </div>

          {/* Table Grid */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[11px] border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3">Stay Date</th>
                    <th className="px-4 py-3 text-center">Min LOS (MLOS)</th>
                    <th className="px-4 py-3 text-center">Max LOS</th>
                    <th className="px-4 py-3 text-center">CTA (Closed Arrival)</th>
                    <th className="px-4 py-3 text-center">CTD (Closed Departure)</th>
                    <th className="px-4 py-3">AI Recommendation Context</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {losRules.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                        No restriction rules found for selected date window. Click "Fetch Rules" to populate.
                      </td>
                    </tr>
                  ) : (
                    losRules.map((rule) => (
                      <tr key={rule.rule_id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="px-4 py-3.5 font-medium text-white flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-indigo-400" />
                          {rule.stay_date}
                        </td>
                        <td className="px-4 py-3.5 text-center">
                          <span className="px-2.5 py-1 bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full font-bold">
                            {rule.min_length_of_stay} {rule.min_length_of_stay === 1 ? 'Night' : 'Nights'}
                          </span>
                        </td>
                        <td className="px-4 py-3.5 text-center text-slate-400">
                          {rule.max_length_of_stay || 'Unlimited'}
                        </td>
                        <td className="px-4 py-3.5 text-center">
                          {rule.closed_to_arrival ? (
                            <span className="px-2 py-0.5 bg-rose-500/20 text-rose-300 border border-rose-500/30 rounded font-semibold text-[10px]">
                              CTA ACTIVE
                            </span>
                          ) : (
                            <span className="text-slate-500">Open</span>
                          )}
                        </td>
                        <td className="px-4 py-3.5 text-center">
                          {rule.closed_to_departure ? (
                            <span className="px-2 py-0.5 bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded font-semibold text-[10px]">
                              CTD ACTIVE
                            </span>
                          ) : (
                            <span className="text-slate-500">Open</span>
                          )}
                        </td>
                        <td className="px-4 py-3.5">
                          <div className="text-slate-300 text-[11px]">
                            {rule.recommendation_reason || 'Base inventory policy.'}
                          </div>
                          {rule.is_system_recommended && (
                            <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400 mt-0.5">
                              <Sparkles className="w-3 h-3" /> System Dynamic MLOS
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3.5 text-right">
                          <button
                            onClick={() => {
                              setEditingRule(rule);
                              setEditMlos(rule.min_length_of_stay);
                              setEditCta(rule.closed_to_arrival);
                              setEditCtd(rule.closed_to_departure);
                            }}
                            className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-indigo-300 rounded text-[11px] transition-colors border border-slate-700 flex items-center gap-1 ml-auto"
                          >
                            <Edit3 className="w-3 h-3" />
                            Edit
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: AUDIT HISTORY LOG */}
      {activeTab === 'audit_logs' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Group Evaluation Log Audit Trail</h3>
              <p className="text-slate-400 text-xs">Historical group displacement simulations logged in INR (₹).</p>
            </div>
            <button
              onClick={fetchEvaluationLogs}
              className="p-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loadingLogs ? 'animate-spin' : ''}`} />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3">Timestamp</th>
                  <th className="px-4 py-3">Stay Dates</th>
                  <th className="px-4 py-3 text-center">Rooms</th>
                  <th className="px-4 py-3 text-right">Offered Rate (INR)</th>
                  <th className="px-4 py-3 text-right">Breakeven Rate (INR)</th>
                  <th className="px-4 py-3 text-center">Recommendation</th>
                  <th className="px-4 py-3 text-right">Net Impact (INR)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {evaluationLogs.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-6 text-center text-slate-500">
                      No evaluation history logged yet. Run a group displacement calculation to record entries.
                    </td>
                  </tr>
                ) : (
                  evaluationLogs.map((log, idx) => {
                    const sDate = log.start_date || log.checkin_date || 'N/A';
                    const eDate = log.end_date || log.checkout_date || 'N/A';
                    const recStatus = log.recommendation || log.decision || 'ACCEPT';
                    const netImp = log.net_revenue_impact ?? log.net_displacement_impact ?? 0;
                    return (
                      <tr key={log.displacement_id || idx} className="hover:bg-slate-800/40">
                        <td className="px-4 py-3 font-mono text-[11px] text-slate-400">
                          {log.created_at ? new Date(log.created_at).toLocaleString() : 'Just now'}
                        </td>
                        <td className="px-4 py-3 text-white font-medium">
                          {sDate} to {eDate}
                        </td>
                        <td className="px-4 py-3 text-center text-slate-300 font-bold">
                          {log.rooms_requested}
                        </td>
                        <td className="px-4 py-3 text-right text-slate-300 font-mono">
                          {formatINR(log.offered_group_rate || log.offered_rate || 0)}
                        </td>
                        <td className="px-4 py-3 text-right text-indigo-400 font-bold font-mono">
                          {formatINR(log.breakeven_group_rate || 0)}
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span
                            className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                              recStatus === 'ACCEPT'
                                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                                : recStatus === 'COUNTER_OFFER'
                                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                                : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                            }`}
                          >
                            {recStatus}
                          </span>
                        </td>
                        <td
                          className={`px-4 py-3 text-right font-bold font-mono ${
                            netImp >= 0 ? 'text-emerald-400' : 'text-rose-400'
                          }`}
                        >
                          {netImp >= 0 ? '+' : ''}
                          {formatINR(netImp)}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* EDIT LOS RULE MODAL */}
      {editingRule && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Edit3 className="w-5 h-5 text-indigo-400" />
              Edit LOS Controls ({editingRule.stay_date})
            </h3>

            <div className="space-y-4 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Minimum Length of Stay (MLOS)</label>
                <input
                  type="number"
                  min="1"
                  max="14"
                  value={editMlos}
                  onChange={(e) => setEditMlos(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white"
                />
              </div>

              <div className="flex items-center justify-between bg-slate-950 p-3 rounded-lg border border-slate-800">
                <div>
                  <span className="text-white font-medium block">Closed to Arrival (CTA)</span>
                  <span className="text-slate-500 text-[11px]">Restrict check-ins on this date</span>
                </div>
                <input
                  type="checkbox"
                  checked={editCta}
                  onChange={(e) => setEditCta(e.target.checked)}
                  className="w-4 h-4 accent-indigo-600 rounded"
                />
              </div>

              <div className="flex items-center justify-between bg-slate-950 p-3 rounded-lg border border-slate-800">
                <div>
                  <span className="text-white font-medium block">Closed to Departure (CTD)</span>
                  <span className="text-slate-500 text-[11px]">Restrict check-outs on this date</span>
                </div>
                <input
                  type="checkbox"
                  checked={editCtd}
                  onChange={(e) => setEditCtd(e.target.checked)}
                  className="w-4 h-4 accent-indigo-600 rounded"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                onClick={() => setEditingRule(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveLOSRule}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-indigo-600/30"
              >
                Save Restriction Rule
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
