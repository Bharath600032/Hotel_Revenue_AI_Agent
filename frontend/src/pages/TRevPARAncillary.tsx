import React, { useEffect, useState } from 'react';
import { useHotel } from '../context/HotelContext';
import { apiService } from '../services/api';
import {
  TRevPARSummaryResponse,
  AncillaryPackageRecommendationResponse,
  AncillaryRevenueEntry,
} from '../types';
import {
  TrendingUp,
  DollarSign,
  Utensils,
  Sparkles,
  RefreshCw,
  PieChart as PieChartIcon,
  BarChart2,
  Calendar,
  Layers,
  CheckCircle,
  Plus,
  ArrowUpRight,
  ShieldCheck,
  Tag,
  Percent,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';

const getTodayDateString = () => new Date().toISOString().split('T')[0];
const get7DaysAgoString = () => new Date(Date.now() - 7 * 86400000).toISOString().split('T')[0];

const formatINR = (val: number) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(val || 0);

const CATEGORY_COLORS = ['#10b981', '#6366f1', '#f59e0b', '#06b6d4', '#ec4899', '#8b5cf6'];

export const TRevPARAncillary: React.FC = () => {
  const { selectedHotel } = useHotel();
  const hotelId = selectedHotel?.hotel_id || 1;

  const [startDate, setStartDate] = useState(get7DaysAgoString());
  const [endDate, setEndDate] = useState(getTodayDateString());

  const [summary, setSummary] = useState<TRevPARSummaryResponse | null>(null);
  const [packages, setPackages] = useState<AncillaryPackageRecommendationResponse[]>([]);
  const [loading, setLoading] = useState(true);

  // Modal Logger State
  const [showLogModal, setShowLogModal] = useState(false);
  const [logDate, setLogDate] = useState(getTodayDateString());
  const [logCategory, setLogCategory] = useState<'FB' | 'SPA' | 'BANQUET' | 'PARKING' | 'LAUNDRY' | 'OTHER'>('FB');
  const [logSubCategory, setLogSubCategory] = useState('Restaurant Dining');
  const [logAmount, setLogAmount] = useState<number>(15000);
  const [logCovers, setLogCovers] = useState<number>(45);
  const [logCost, setLogCost] = useState<number>(3500);
  const [logNotes, setLogNotes] = useState('');
  const [loggingSuccess, setLoggingSuccess] = useState<string | null>(null);

  useEffect(() => {
    fetchTRevPARData();
  }, [hotelId, startDate, endDate]);

  const fetchTRevPARData = async () => {
    try {
      if (!summary || packages.length === 0) {
        setLoading(true);
      }
      const [sumData, pkgData] = await Promise.all([
        apiService.getTRevPARSummary(hotelId, startDate, endDate),
        apiService.getAncillaryPackages(hotelId),
      ]);
      setSummary(sumData);
      setPackages(pkgData);
    } catch (err) {
      console.error('Failed to load TRevPAR analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRecordEntry = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: AncillaryRevenueEntry = {
        entry_date: logDate,
        category: logCategory,
        sub_category: logSubCategory,
        revenue_amount: Number(logAmount),
        cover_count: Number(logCovers),
        cost_of_sales: Number(logCost),
        notes: logNotes,
      };
      await apiService.recordAncillaryEntry(hotelId, payload);
      setLoggingSuccess(`Successfully logged ₹${logAmount.toLocaleString('en-IN')} under ${logCategory}!`);
      setShowLogModal(false);
      fetchTRevPARData();
      setTimeout(() => setLoggingSuccess(null), 4000);
    } catch (err) {
      console.error('Failed to record ancillary revenue entry:', err);
    }
  };

  const pieChartData = summary
    ? summary.categories_breakdown.map((cat) => ({
        name: cat.category,
        value: cat.revenue_amount,
      }))
    : [];

  return (
    <div className="space-y-6 font-sans">
      {/* Page Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-2 border-b border-slate-800/60">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-3 tracking-tight">
            <Utensils className="w-7 h-7 text-emerald-400 flex-shrink-0" />
            <span>Total Revenue Management (TRevPAR) & Non-Room Revenue AI</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Optimize Total Revenue Per Available Room (TRevPAR), monitor F&B, Spa, Banquets & Ancillary streams, and deploy AI dynamic package bundles.
          </p>
        </div>

        {/* Action Controls & Date Picker */}
        <div className="flex items-center gap-3 flex-wrap lg:flex-nowrap flex-shrink-0">
          <button
            onClick={() => setShowLogModal(true)}
            className="flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-emerald-600/30 transition-all cursor-pointer whitespace-nowrap h-10"
          >
            <Plus className="w-4 h-4" />
            <span>Log Non-Room Revenue (₹)</span>
          </button>

          <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 p-1.5 rounded-xl text-xs h-10">
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-white px-2 py-1 rounded focus:outline-none focus:border-emerald-500"
            />
            <span className="text-slate-500 font-medium">to</span>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-white px-2 py-1 rounded focus:outline-none focus:border-emerald-500"
            />
            <button
              onClick={fetchTRevPARData}
              className="p-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded transition-colors"
              title="Refresh Data"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Success Notification Banner */}
      {loggingSuccess && (
        <div className="flex items-center gap-2 p-4 bg-emerald-950/80 border border-emerald-700/60 rounded-xl text-emerald-200 text-sm animate-fade-in">
          <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
          <span>{loggingSuccess}</span>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-500"></div>
        </div>
      ) : summary ? (
        <>
          {/* Key Financial Indicator Cards (TRevPAR vs RevPAR vs NRevPAR vs RevPOR) */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Card 1: TRevPAR */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2 shadow-xl relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Total RevPAR (TRevPAR)
                </span>
                <div className="p-2 bg-emerald-500/10 rounded-xl border border-emerald-500/20">
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                </div>
              </div>
              <div className="flex items-baseline justify-between">
                <span className="text-3xl font-extrabold text-white">
                  {formatINR(summary.trevpar)}
                </span>
                <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20 flex items-center gap-0.5">
                  +38.5% over RevPAR
                </span>
              </div>
              <p className="text-[11px] text-slate-500">
                Total Revenue / {summary.total_sellable_rooms} Sellable Rooms ({summary.occupancy_pct}% Occ)
              </p>
            </div>

            {/* Card 2: Room RevPAR */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2 shadow-xl">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Room Only RevPAR
                </span>
                <div className="p-2 bg-indigo-500/10 rounded-xl border border-indigo-500/20">
                  <BarChart2 className="w-4 h-4 text-indigo-400" />
                </div>
              </div>
              <div className="flex items-baseline justify-between">
                <span className="text-3xl font-extrabold text-white">
                  {formatINR(summary.revpar)}
                </span>
                <span className="text-xs text-slate-400">
                  ADR: {formatINR(summary.adr)}
                </span>
              </div>
              <p className="text-[11px] text-slate-500">
                Room Revenue: {formatINR(summary.room_revenue)}
              </p>
            </div>

            {/* Card 3: Net RevPAR (NRevPAR) */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2 shadow-xl">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Net RevPAR (NRevPAR)
                </span>
                <div className="p-2 bg-cyan-500/10 rounded-xl border border-cyan-500/20">
                  <Percent className="w-4 h-4 text-cyan-400" />
                </div>
              </div>
              <div className="flex items-baseline justify-between">
                <span className="text-3xl font-extrabold text-white">
                  {formatINR(summary.nrevpar)}
                </span>
                <span className="text-xs text-rose-400">
                  -{formatINR(summary.distribution_commission_costs)} OTA Costs
                </span>
              </div>
              <p className="text-[11px] text-slate-500">
                Adjusted Net Room Revenue after ~12.5% distribution commissions
              </p>
            </div>

            {/* Card 4: Ancillary RevPOR */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2 shadow-xl">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Non-Room RevPOR
                </span>
                <div className="p-2 bg-amber-500/10 rounded-xl border border-amber-500/20">
                  <Utensils className="w-4 h-4 text-amber-400" />
                </div>
              </div>
              <div className="flex items-baseline justify-between">
                <span className="text-3xl font-extrabold text-amber-400">
                  {formatINR(summary.ancillary_revpor)}
                </span>
                <span className="text-xs text-emerald-400 font-bold">
                  {formatINR(summary.total_ancillary_revenue)} Total
                </span>
              </div>
              <p className="text-[11px] text-slate-500">
                Ancillary spend captured per occupied room night ({summary.total_occupied_rooms} rooms)
              </p>
            </div>
          </div>

          {/* Non-Room Revenue Category Breakdown Charts & Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Chart Panel */}
            <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <PieChartIcon className="w-4 h-4 text-emerald-400" />
                  Non-Room Stream Share
                </h3>
                <span className="text-xs text-slate-400 font-mono">
                  {formatINR(summary.total_ancillary_revenue)}
                </span>
              </div>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieChartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {pieChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#38bdf8', borderRadius: '10px', fontSize: '13px', color: '#ffffff', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.7)' }}
                      itemStyle={{ color: '#38bdf8', fontWeight: 700 }}
                      labelStyle={{ color: '#f8fafc', fontWeight: 600 }}
                      formatter={(val: any) => [formatINR(Number(val)), 'Revenue']}
                    />
                    <Legend wrapperStyle={{ fontSize: '11px' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Right Table Breakdown */}
            <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-sm font-semibold text-white">Ancillary Revenue Stream Breakdown</h3>
                <span className="text-xs text-slate-400">Total Gross Revenue: {formatINR(summary.total_gross_revenue)}</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
                    <tr>
                      <th className="px-4 py-3">Ancillary Category</th>
                      <th className="px-4 py-3 text-right">Revenue (INR)</th>
                      <th className="px-4 py-3 text-center">Share %</th>
                      <th className="px-4 py-3 text-right">RevPOR</th>
                      <th className="px-4 py-3 text-center">Covers / Volume</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {summary.categories_breakdown.map((cat, idx) => (
                      <tr key={cat.category} className="hover:bg-slate-800/40">
                        <td className="px-4 py-3.5 font-medium text-white flex items-center gap-2">
                          <span
                            className="w-2.5 h-2.5 rounded-full"
                            style={{ backgroundColor: CATEGORY_COLORS[idx % CATEGORY_COLORS.length] }}
                          />
                          {cat.category}
                        </td>
                        <td className="px-4 py-3.5 text-right font-bold text-white font-mono">
                          {formatINR(cat.revenue_amount)}
                        </td>
                        <td className="px-4 py-3.5 text-center font-bold text-emerald-400 font-mono">
                          {cat.percentage_of_total_ancillary}%
                        </td>
                        <td className="px-4 py-3.5 text-right text-cyan-400 font-mono">
                          {formatINR(cat.revpor)} / room
                        </td>
                        <td className="px-4 py-3.5 text-center text-slate-400 font-mono">
                          {cat.cover_count}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* AI Non-Room Upsell Package & Bundle Recommendations */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-amber-400" />
                  AI Dynamic Non-Room Upsell Packages & Bundle Yield Optimization
                </h3>
                <p className="text-slate-400 text-xs mt-0.5">
                  AI-recommended room + ancillary bundles engineered to increase TRevPAR per room night.
                </p>
              </div>
              <span className="px-3 py-1 bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-xs rounded-full font-bold">
                {packages.length} Active AI Bundles
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {packages.map((pkg) => (
                <div
                  key={pkg.package_id}
                  className="bg-slate-950 border border-slate-800/80 rounded-xl p-5 hover:border-indigo-500/50 transition-all space-y-3"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="text-[10px] font-extrabold uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded">
                        {pkg.category}
                      </span>
                      <h4 className="text-sm font-bold text-white mt-1.5">{pkg.package_name}</h4>
                    </div>
                    <div className="text-right">
                      <span className="text-xs text-slate-500 line-through block">
                        {formatINR(pkg.standalone_price)}
                      </span>
                      <span className="text-base font-extrabold text-emerald-400 font-mono">
                        {formatINR(pkg.recommended_bundle_price)}
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-400 leading-relaxed">{pkg.description}</p>

                  <div className="grid grid-cols-2 gap-2 bg-slate-900/60 p-3 rounded-lg border border-slate-800 text-xs">
                    <div>
                      <span className="text-slate-500 text-[10px] block">Conversion Uplift</span>
                      <span className="font-bold text-emerald-400">+{pkg.projected_conversion_uplift_pct}%</span>
                    </div>
                    <div>
                      <span className="text-slate-500 text-[10px] block">TRevPAR Gain / Room</span>
                      <span className="font-bold text-indigo-400">+{formatINR(pkg.expected_trevpar_gain_per_room)}</span>
                    </div>
                  </div>

                  <div className="pt-1">
                    <span className="text-[11px] text-slate-400 font-mono block">
                      <strong className="text-indigo-400 font-semibold">AI Rationale:</strong> {pkg.strategy_reasoning}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : null}

      {/* RECORD NON-ROOM REVENUE MODAL */}
      {showLogModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Plus className="w-5 h-5 text-emerald-400" />
              Log Non-Room Ancillary Revenue Entry (₹)
            </h3>

            <form onSubmit={handleRecordEntry} className="space-y-4 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Entry Date</label>
                <input
                  type="date"
                  value={logDate}
                  onChange={(e) => setLogDate(e.target.value)}
                  required
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Ancillary Category</label>
                <select
                  value={logCategory}
                  onChange={(e: any) => setLogCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white"
                >
                  <option value="FB">Food & Beverage (F&B)</option>
                  <option value="SPA">Spa & Wellness</option>
                  <option value="BANQUET">Banquets & Event Rentals</option>
                  <option value="PARKING">Parking & Valet</option>
                  <option value="LAUNDRY">Laundry & Dry Cleaning</option>
                  <option value="OTHER">Miscellaneous Ancillary</option>
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Subcategory / Venue Name</label>
                <input
                  type="text"
                  value={logSubCategory}
                  onChange={(e) => setLogSubCategory(e.target.value)}
                  required
                  placeholder="e.g. Specialty Restaurant, Banquet Hall A"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-400 block mb-1">Revenue Amount (₹ INR)</label>
                  <input
                    type="number"
                    min="1"
                    value={logAmount}
                    onChange={(e) => setLogAmount(Number(e.target.value))}
                    required
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono"
                  />
                </div>

                <div>
                  <label className="text-slate-400 block mb-1">Covers / Volume</label>
                  <input
                    type="number"
                    min="0"
                    value={logCovers}
                    onChange={(e) => setLogCovers(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Direct Cost of Sales (₹ INR)</label>
                <input
                  type="number"
                  min="0"
                  value={logCost}
                  onChange={(e) => setLogCost(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Notes / Description</label>
                <input
                  type="text"
                  value={logNotes}
                  onChange={(e) => setLogNotes(e.target.value)}
                  placeholder="Optional notes..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowLogModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-emerald-600/30"
                >
                  Save Entry (₹)
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
