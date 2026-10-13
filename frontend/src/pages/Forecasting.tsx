import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { ForecastItem, RoomType, PriceForecastItem } from '../types';
import {
  LineChart as LineChartIcon,
  Play,
  Cpu,
  Calendar,
  TrendingUp,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  IndianRupee,
  Layers,
  BarChart3,
  Sliders,
  Users,
  Sparkles,
  Building2,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
} from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  LineChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

import { useHotel } from '../context/HotelContext';

const formatINR = (val: number) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(val);

const getShortHotelName = (name: string): string => {
  if (!name) return 'Hotel';
  if (name.toLowerCase().includes('market compset') || name.toLowerCase().includes('market average')) {
    return 'Market Avg';
  }
  let cleaned = name
    .replace(/\s*\(Main Hotel.*?\)/gi, '')
    .replace(/\s*\(Main\)/gi, '')
    .replace(/\s*\(₹\)/gi, '')
    .trim();

  const words = cleaned.split(/\s+/);
  if (words.length > 2) {
    const lastWord = words[words.length - 1].toLowerCase();
    if (['hotel', 'resort', 'residences', 'suites', 'inn'].includes(lastWord)) {
      words.pop();
      cleaned = words.join(' ');
    }
  }
  return cleaned;
};

const competitorColors = [
  '#10b981', // Emerald
  '#06b6d4', // Cyan
  '#f43f5e', // Rose
  '#a855f7', // Purple
  '#ec4899', // Pink
  '#3b82f6', // Blue
  '#eab308', // Amber
  '#14b8a6', // Teal
];

const getCompetitorColor = (idx: number) => competitorColors[idx % competitorColors.length];

const CustomPriceTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload || !payload.length) return null;

  return (
    <div className="bg-slate-950/95 border border-slate-700/80 rounded-xl p-3 shadow-2xl backdrop-blur-md min-w-[220px] space-y-2">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-xs">
        <span className="font-bold text-sky-400 font-mono">Date: {label}</span>
        <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Pricing Benchmark</span>
      </div>
      <div className="space-y-1.5">
        {payload.map((item: any, idx: number) => {
          const shortName = getShortHotelName(item.name || item.dataKey);
          const color = item.color || '#6366f1';
          return (
            <div key={idx} className="flex items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-1.5 min-w-0">
                <span className="w-2.5 h-2.5 rounded-full flex-shrink-0 shadow-sm" style={{ backgroundColor: color }} />
                <span
                  className="font-bold truncate max-w-[130px] text-xs"
                  style={{ color: color }}
                  title={item.name}
                >
                  {shortName}
                </span>
              </div>
              <span className="font-mono font-bold text-white text-xs">
                {formatINR(Number(item.value))}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export const Forecasting: React.FC = () => {
  const { selectedHotel } = useHotel();
  const hotelId = selectedHotel?.hotel_id || 1;
  const hotelName = selectedHotel?.hotel_name || 'Current Property';

  const [roomTypes, setRoomTypes] = useState<RoomType[]>([]);
  const [roomTypeId, setRoomTypeId] = useState<number>(1);
  const [horizonDays, setHorizonDays] = useState<7 | 14 | 30>(30);
  const [activeTab, setActiveTab] = useState<'both' | 'room_demand' | 'price_competitor'>('both');

  // Room Demand state
  const [forecasts, setForecasts] = useState<ForecastItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [running, setRunning] = useState<boolean>(false);
  const [roomDemandPage, setRoomDemandPage] = useState<number>(1);
  const roomPageSize = 5;

  // Price & Competitor Forecasting state
  const [priceForecasts, setPriceForecasts] = useState<PriceForecastItem[]>([]);
  const [priceLoading, setPriceLoading] = useState<boolean>(false);
  const [priceForecastPage, setPriceForecastPage] = useState<number>(1);
  const pricePageSize = 5;

  useEffect(() => {
    fetchRoomTypes();
  }, [hotelId]);

  useEffect(() => {
    if (roomTypeId) {
      loadForecasts();
      loadPriceForecasts();
    }
  }, [hotelId, roomTypeId, horizonDays]);

  const fetchRoomTypes = async () => {
    try {
      const rts = await apiService.getRoomTypes(hotelId);
      if (rts && rts.length > 0) {
        setRoomTypes(rts);
        setRoomTypeId(rts[0].room_type_id);
      }
    } catch (err) {
      console.error('Failed to load room types:', err);
    }
  };

  const loadForecasts = async () => {
    try {
      if (forecasts.length === 0) {
        setLoading(true);
      }
      const today = new Date().toISOString().split('T')[0];
      const endDate = new Date(Date.now() + horizonDays * 86400000).toISOString().split('T')[0];
      const data = await apiService.getForecasts(hotelId, roomTypeId, today, endDate);
      setForecasts(data.slice(0, horizonDays));
      setRoomDemandPage(1);
    } catch (err) {
      console.error('Failed to load room demand forecasts:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadPriceForecasts = async () => {
    try {
      setPriceLoading(true);
      const data = await apiService.getPriceForecast(hotelId, horizonDays, roomTypeId);
      setPriceForecasts(data.slice(0, horizonDays));
      setPriceForecastPage(1);
    } catch (err) {
      console.error('Failed to load price forecasts:', err);
    } finally {
      setPriceLoading(false);
    }
  };

  const handleRunPipeline = async () => {
    try {
      setRunning(true);
      const today = new Date().toISOString().split('T')[0];
      await apiService.runForecast(hotelId, roomTypeId, today, horizonDays);
      await Promise.all([loadForecasts(), loadPriceForecasts()]);
    } catch (err) {
      console.error('Failed to execute forecast pipeline:', err);
    } finally {
      setRunning(false);
    }
  };

  const handleHorizonChange = (days: 7 | 14 | 30) => {
    setHorizonDays(days);
    setRoomDemandPage(1);
    setPriceForecastPage(1);
  };

  // Chart Data preparation
  const roomChartData = forecasts.slice(0, horizonDays).map((f) => ({
    date: f.stay_date.slice(5),
    Demand: Math.round(f.predicted_demand),
    UpperBound: Math.round(f.upper_bound),
    LowerBound: Math.round(f.lower_bound),
  }));

  // Unique Competitor list for dynamic lines
  const competitorKeys = React.useMemo(() => {
    const keys = new Set<string>();
    priceForecasts.forEach((pf) => {
      if (pf.competitors) {
        pf.competitors.forEach((c) => keys.add(c.name));
      }
    });
    return Array.from(keys);
  }, [priceForecasts]);

  const competitorColors = ['#10b981', '#38bdf8', '#f43f5e', '#c084fc', '#ec4899'];

  const priceChartData = priceForecasts.slice(0, horizonDays).map((p) => {
    const entry: Record<string, any> = {
      date: p.stay_date.slice(5),
      [hotelName]: p.main_hotel_rate,
      'Market Average': p.comp_average,
    };
    if (p.competitors) {
      p.competitors.forEach((c) => {
        entry[c.name] = c.rate;
      });
    }
    return entry;
  });

  // Room Demand Pagination calculations
  const totalRoomItems = forecasts.length;
  const totalRoomPages = Math.max(1, Math.ceil(totalRoomItems / roomPageSize));
  const paginatedRoomForecasts = forecasts.slice(
    (roomDemandPage - 1) * roomPageSize,
    roomDemandPage * roomPageSize
  );

  // Price Forecasting Pagination calculations
  const totalPriceItems = priceForecasts.length;
  const totalPricePages = Math.max(1, Math.ceil(totalPriceItems / pricePageSize));
  const paginatedPriceForecasts = priceForecasts.slice(
    (priceForecastPage - 1) * pricePageSize,
    priceForecastPage * pricePageSize
  );

  return (
    <div className="space-y-6">
      {/* Top Header & Global Horizon Selection Bar */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 pb-2 border-b border-slate-800/60">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-3 tracking-tight">
            <LineChartIcon className="w-7 h-7 text-indigo-400 flex-shrink-0" />
            <span>Demand & Dynamic Price Forecasting Engine</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Simulate room demand volume and dynamic competitive pricing across 7-day, 14-day, and 30-day forecast horizons.
          </p>
        </div>

        {/* Action Controls & Horizon Pill Selectors */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Horizon Duration Selection (7, 14, 30 Days) */}
          <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-1.5 rounded-xl shadow-inner">
            <span className="text-[11px] font-semibold text-slate-400 px-2 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-indigo-400" />
              <span>Horizon:</span>
            </span>
            {([7, 14, 30] as const).map((d) => (
              <button
                key={d}
                onClick={() => handleHorizonChange(d)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
                  horizonDays === d
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                {d} Days
              </button>
            ))}
          </div>

          {/* Room Type Selector */}
          <select
            value={roomTypeId}
            onChange={(e) => setRoomTypeId(Number(e.target.value))}
            className="bg-slate-900 border border-slate-800 text-white text-xs px-3 py-2 rounded-xl cursor-pointer focus:outline-none focus:border-indigo-500"
          >
            {roomTypes.length > 0 ? (
              roomTypes.map((rt) => (
                <option key={rt.room_type_id} value={rt.room_type_id}>
                  {rt.room_type_name} ({rt.room_type_code})
                </option>
              ))
            ) : (
              <>
                <option value={1}>Superior Comfort Room (SUP)</option>
                <option value={2}>Deluxe Executive Room (DLX)</option>
                <option value={3}>Luxury Executive Suite (STE)</option>
              </>
            )}
          </select>

          {/* Run Forecast Pipeline Button */}
          <button
            onClick={handleRunPipeline}
            disabled={running}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-600/30 transition-all cursor-pointer"
          >
            {running ? (
              <>
                <div className="animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-white"></div>
                <span>Executing Pipeline...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5" />
                <span>Run Forecast Pipeline</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* View Switcher Tabs */}
      <div className="flex items-center gap-2 bg-slate-900/60 p-1.5 rounded-xl border border-slate-800/80 w-fit">
        <button
          onClick={() => setActiveTab('both')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 cursor-pointer ${
            activeTab === 'both'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Complete Dashboard (Both)</span>
        </button>
        <button
          onClick={() => setActiveTab('room_demand')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 cursor-pointer ${
            activeTab === 'room_demand'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
          }`}
        >
          <BarChart3 className="w-4 h-4 text-emerald-400" />
          <span>Room Demand Forecasting ({horizonDays}d)</span>
        </button>
        <button
          onClick={() => setActiveTab('price_competitor')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 cursor-pointer ${
            activeTab === 'price_competitor'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
          }`}
        >
          <IndianRupee className="w-4 h-4 text-indigo-400" />
          <span>Price Forecasting vs Competitors ({horizonDays}d)</span>
        </button>
      </div>

      {/* Ensemble ML Pipeline Model Badges */}
      <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-2xl grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 text-center">
        {['Naive Baseline', 'Moving Average', 'Seasonal Naive', 'SARIMAX Time-Series', 'XGBoost Machine Learning'].map(
          (m, idx) => (
            <div key={idx} className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 flex items-center gap-2 text-left">
              <Cpu className="w-4 h-4 text-indigo-400 flex-shrink-0" />
              <div>
                <p className="text-xs font-bold text-white leading-tight">{m}</p>
                <span className="text-[10px] text-emerald-400 font-medium">Active Pipeline</span>
              </div>
            </div>
          )
        )}
      </div>

      {/* ========================================================================= */}
      {/* SECTION 1: ROOM DEMAND FORECASTING (GRAPH + HORIZON 5-RECORD PAGINATION)   */}
      {/* ========================================================================= */}
      {(activeTab === 'both' || activeTab === 'room_demand') && (
        <div className="space-y-6">
          {/* Room Demand Visual Chart */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-emerald-400" />
                  <span>{horizonDays}-Day Projected Room Demand Curve & Confidence Bounds</span>
                </h3>
                <p className="text-slate-400 text-xs mt-0.5">
                  Multi-model ensemble predicted room nights demand with upper and lower statistical confidence bounds.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 text-xs rounded-lg border border-emerald-500/20 font-semibold font-mono">
                  {horizonDays} Days Window
                </span>
                <span className="px-2.5 py-1 bg-indigo-500/10 text-indigo-400 text-xs rounded-lg border border-indigo-500/20 font-mono font-semibold">
                  Ensemble AI
                </span>
              </div>
            </div>

            {loading ? (
              <div className="flex justify-center items-center h-80">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
              </div>
            ) : forecasts.length > 0 ? (
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={roomChartData}>
                    <defs>
                      <linearGradient id="colorBound" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0.05} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 11 }} label={{ value: 'Rooms', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#10b981', borderRadius: '10px', color: '#fff' }}
                      itemStyle={{ color: '#f8fafc', fontWeight: 600 }}
                      labelStyle={{ color: '#38bdf8', fontWeight: 700 }}
                    />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                    <Area type="monotone" dataKey="UpperBound" fill="url(#colorBound)" stroke="#059669" strokeDasharray="3 3" name="Upper Confidence Bound" />
                    <Line type="monotone" dataKey="Demand" stroke="#6366f1" strokeWidth={3} dot={{ r: 4 }} name="Predicted Demand" />
                    <Line type="monotone" dataKey="LowerBound" stroke="#f59e0b" strokeDasharray="3 3" name="Lower Confidence Bound" />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="text-center py-16 text-slate-500 text-xs">
                No room demand forecast data available. Click "Run Forecast Pipeline" above.
              </div>
            )}
          </div>

          {/* Predicted Room Demand Horizon Table (Paginated: 5 Records per Page) */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-indigo-400" />
                  <span>Predicted Room Demand Horizon ({forecasts.length} Days)</span>
                </h3>
                <p className="text-slate-400 text-xs mt-0.5">
                  Displaying room demand predictions in slides of 5 records per page.
                </p>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-slate-400">Page</span>
                <span className="px-2 py-0.5 bg-indigo-600/30 text-indigo-300 font-bold rounded border border-indigo-500/40 font-mono">
                  {roomDemandPage} / {totalRoomPages}
                </span>
              </div>
            </div>

            {loading ? (
              <div className="flex justify-center items-center h-48">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
              </div>
            ) : forecasts.length > 0 ? (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 bg-slate-950 text-slate-400 uppercase tracking-wider text-[11px]">
                        <th className="py-3 px-3.5">Stay Date</th>
                        <th className="py-3 px-3.5">Model Used</th>
                        <th className="py-3 px-3.5 text-center">Predicted Demand</th>
                        <th className="py-3 px-3.5 text-center">Confidence Interval (Lower - Upper)</th>
                        <th className="py-3 px-3.5 text-center">Confidence Score</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 font-mono">
                      {paginatedRoomForecasts.map((f, i) => (
                        <tr key={f.stay_date || i} className="hover:bg-slate-800/40 transition-colors">
                          <td className="py-3.5 px-3.5 font-medium text-white font-sans flex items-center gap-2">
                            <Calendar className="w-4 h-4 text-indigo-400 flex-shrink-0" />
                            <span>{f.stay_date}</span>
                          </td>
                          <td className="py-3.5 px-3.5">
                            <span className="px-2.5 py-1 bg-indigo-500/10 text-indigo-400 text-xs rounded border border-indigo-500/20 font-semibold font-sans">
                              {f.model_name || 'Ensemble'}
                            </span>
                          </td>
                          <td className="py-3.5 px-3.5 text-center font-bold text-emerald-400 text-sm">
                            {Math.round(f.predicted_demand)} Rooms
                          </td>
                          <td className="py-3.5 px-3.5 text-center text-slate-300">
                            {Math.round(f.lower_bound)} - {Math.round(f.upper_bound)} Rooms
                          </td>
                          <td className="py-3.5 px-3.5 text-center">
                            <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded text-xs font-semibold">
                              {(f.confidence_score * 100).toFixed(0)}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* 5-Record Pagination Footer with Slide Controls */}
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800 text-xs">
                  <div className="text-slate-400">
                    Showing <span className="text-white font-medium">{totalRoomItems > 0 ? (roomDemandPage - 1) * roomPageSize + 1 : 0}</span> to{' '}
                    <span className="text-white font-medium">{Math.min(roomDemandPage * roomPageSize, totalRoomItems)}</span> of{' '}
                    <span className="text-white font-medium">{totalRoomItems}</span> days (5 per page)
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setRoomDemandPage((p) => Math.max(1, p - 1))}
                      disabled={roomDemandPage <= 1}
                      className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800 text-slate-300 rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer disabled:cursor-not-allowed"
                    >
                      <ChevronLeft className="w-4 h-4" />
                      <span>Previous</span>
                    </button>

                    <div className="flex items-center gap-1">
                      {Array.from({ length: totalRoomPages }, (_, i) => i + 1).map((pageNum) => (
                        <button
                          key={pageNum}
                          onClick={() => setRoomDemandPage(pageNum)}
                          className={`w-7 h-7 rounded-lg text-xs font-semibold flex items-center justify-center transition-all cursor-pointer ${
                            roomDemandPage === pageNum
                              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                              : 'bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white'
                          }`}
                        >
                          {pageNum}
                        </button>
                      ))}
                    </div>

                    <button
                      onClick={() => setRoomDemandPage((p) => Math.min(totalRoomPages, p + 1))}
                      disabled={roomDemandPage >= totalRoomPages}
                      className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:hover:bg-indigo-600 text-white rounded-lg transition-colors flex items-center gap-1.5 shadow-md shadow-indigo-600/20 cursor-pointer disabled:cursor-not-allowed"
                    >
                      <span>Slide to Next Page</span>
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-12">
                <LineChartIcon className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                <p className="text-slate-400 text-sm">No forecast predictions found for this selection.</p>
                <button
                  onClick={handleRunPipeline}
                  className="mt-3 text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
                >
                  Click here to run the multi-model forecasting engine
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SECTION 2: PRICE FORECASTING VS COMPETITORS (GRAPH + 5-RECORD PAGINATION)  */}
      {/* ========================================================================= */}
      {(activeTab === 'both' || activeTab === 'price_competitor') && (
        <div className="space-y-6 pt-4 border-t border-slate-800/80">
          {/* Section Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 className="text-xl font-bold text-white flex items-center gap-2.5">
                <IndianRupee className="w-6 h-6 text-indigo-400" />
                <span>Price Forecasting: Main Hotel vs Competitive Set (₹ INR)</span>
              </h2>
              <p className="text-slate-400 text-xs mt-0.5">
                Compare {hotelName} forecasted optimal rates with live competitor pricing over {horizonDays} days horizon.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 bg-indigo-500/10 text-indigo-400 text-xs rounded-xl border border-indigo-500/20 font-semibold flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" />
                Dynamic Price Intelligence
              </span>
            </div>
          </div>

          {/* Price Forecasting Graph */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-indigo-400" />
                  <span>{horizonDays}-Day Price Trajectory: {hotelName} vs Competitors (₹ INR)</span>
                </h3>
                <p className="text-slate-400 text-xs mt-0.5">
                  Visual rate positioning across weekdays, weekends, and high-demand events in INR.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 bg-indigo-600 text-white font-bold text-xs rounded-lg shadow-sm">
                  {horizonDays} Days
                </span>
              </div>
            </div>

            {priceLoading ? (
              <div className="flex justify-center items-center h-80">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
              </div>
            ) : priceForecasts.length > 0 ? (
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={priceChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 11 }} />
                    <YAxis
                      stroke="#64748b"
                      tick={{ fontSize: 11 }}
                      tickFormatter={(val) => `₹${val.toLocaleString('en-IN')}`}
                      label={{ value: 'Rate (₹)', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }}
                    />
                    <Tooltip
                      formatter={(value: any) => [formatINR(Number(value)), 'Rate']}
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#6366f1', borderRadius: '10px', color: '#fff' }}
                      itemStyle={{ color: '#f8fafc', fontWeight: 600 }}
                      labelStyle={{ color: '#38bdf8', fontWeight: 700 }}
                    />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />

                    {/* Main Hotel Recommended Rate Line (Primary) */}
                    <Line
                      type="monotone"
                      dataKey={hotelName}
                      stroke="#6366f1"
                      strokeWidth={3.5}
                      dot={{ r: 4.5, fill: '#6366f1', stroke: '#fff', strokeWidth: 1.5 }}
                      activeDot={{ r: 7 }}
                      name={`${hotelName} (Main Hotel ₹)`}
                    />

                    {/* Market Average Line */}
                    <Line
                      type="monotone"
                      dataKey="Market Average"
                      stroke="#f59e0b"
                      strokeWidth={2}
                      strokeDasharray="4 4"
                      dot={{ r: 3, fill: '#f59e0b' }}
                      name="Market Compset Average (₹)"
                    />

                    {/* Individual Competitor Lines */}
                    {competitorKeys.map((cName, idx) => (
                      <Line
                        key={cName}
                        type="monotone"
                        dataKey={cName}
                        stroke={competitorColors[idx % competitorColors.length]}
                        strokeWidth={1.8}
                        dot={false}
                        name={`${cName} (₹)`}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="text-center py-16 text-slate-500 text-xs">
                No competitor price forecast available.
              </div>
            )}
          </div>

          {/* Predicted Price Demand Horizon Table (Paginated: 5 Records per Page) */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-indigo-400" />
                  <span>Predicted Price Demand Horizon ({priceForecasts.length} Days)</span>
                </h3>
                <p className="text-slate-400 text-xs mt-0.5">
                  Detailed day-by-day rate benchmark vs competitors, market positioning %, and predicted room demand (5 per page).
                </p>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-slate-400">Page</span>
                <span className="px-2 py-0.5 bg-indigo-600/30 text-indigo-300 font-bold rounded border border-indigo-500/40 font-mono">
                  {priceForecastPage} / {totalPricePages}
                </span>
              </div>
            </div>

            {priceLoading ? (
              <div className="flex justify-center items-center h-48">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
              </div>
            ) : priceForecasts.length > 0 ? (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 bg-slate-950 text-slate-400 uppercase tracking-wider text-[11px]">
                        <th className="py-3 px-3.5">Stay Date</th>
                        <th className="py-3 px-3.5 text-right font-bold text-indigo-300">{hotelName} Rate</th>
                        <th className="py-3 px-3.5 text-center">Market Average</th>
                        <th className="py-3 px-3.5">Competitor Pricing Benchmark</th>
                        <th className="py-3 px-3.5 text-center">Market Position</th>
                        <th className="py-3 px-3.5 text-center">Predicted Demand</th>
                        <th className="py-3 px-3.5 text-right">AI Strategy</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 font-mono">
                      {paginatedPriceForecasts.map((p, i) => {
                        const diff = p.market_diff_pct;
                        return (
                          <tr key={p.stay_date || i} className="hover:bg-slate-800/40 transition-colors">
                            <td className="py-3.5 px-3.5 font-medium text-white font-sans">
                              <div className="flex items-center gap-2">
                                <Calendar className="w-4 h-4 text-indigo-400 flex-shrink-0" />
                                <div>
                                  <span className="block font-bold">{p.stay_date}</span>
                                  <span className="text-[10px] text-slate-400 font-mono">
                                    {p.day_name || new Date(p.stay_date).toLocaleDateString('en-US', { weekday: 'short' })}
                                  </span>
                                </div>
                              </div>
                            </td>
                            <td className="py-3.5 px-3.5 text-right font-bold text-indigo-300 text-sm">
                              {formatINR(p.main_hotel_rate)}
                            </td>
                            <td className="py-3.5 px-3.5 text-center font-bold text-slate-300">
                              {formatINR(p.comp_average)}
                            </td>
                            <td className="py-3.5 px-3.5 font-sans">
                              <div className="flex flex-wrap gap-1.5 max-w-md">
                                {p.competitors && p.competitors.length > 0 ? (
                                  p.competitors.map((c, cIdx) => (
                                    <span
                                      key={cIdx}
                                      className="px-2 py-0.5 bg-slate-800/80 rounded border border-slate-700/60 text-[10px] text-slate-300 flex items-center gap-1 font-mono"
                                      title={c.name}
                                    >
                                      <Building2 className="w-2.5 h-2.5 text-slate-400" />
                                      <span className="font-sans truncate max-w-[110px]">{c.name.split(' ')[0]}</span>:
                                      <span className="text-white font-semibold">{formatINR(c.rate)}</span>
                                    </span>
                                  ))
                                ) : (
                                  <span className="text-slate-500 text-[11px]">Comp rates tracked</span>
                                )}
                              </div>
                            </td>
                            <td className="py-3.5 px-3.5 text-center font-sans">
                              <span
                                className={`px-2.5 py-1 rounded-full text-[10px] font-bold border flex items-center justify-center gap-1 mx-auto w-fit ${
                                  diff > 3
                                    ? 'bg-rose-500/10 text-rose-300 border-rose-500/30'
                                    : diff < -3
                                    ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                                    : 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                                }`}
                              >
                                {diff > 0 ? (
                                  <ArrowUpRight className="w-3 h-3" />
                                ) : diff < 0 ? (
                                  <ArrowDownRight className="w-3 h-3" />
                                ) : (
                                  <Minus className="w-3 h-3" />
                                )}
                                <span>{p.market_position || `${diff}%`}</span>
                              </span>
                            </td>
                            <td className="py-3.5 px-3.5 text-center font-sans">
                              <div className="font-bold text-emerald-400 text-xs font-mono">
                                {p.predicted_demand_rooms || 12} Rooms
                              </div>
                              <span className="text-[10px] text-slate-400">
                                {p.demand_level || 'Normal Demand'}
                              </span>
                            </td>
                            <td className="py-3.5 px-3.5 text-right font-sans">
                              <span className="px-2 py-1 bg-indigo-500/15 text-indigo-300 rounded border border-indigo-500/30 font-semibold text-[10px]">
                                {p.recommended_strategy || 'Optimize ADR'}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                {/* 5-Record Pagination Footer with Slide Controls */}
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800 text-xs">
                  <div className="text-slate-400">
                    Showing <span className="text-white font-medium">{totalPriceItems > 0 ? (priceForecastPage - 1) * pricePageSize + 1 : 0}</span> to{' '}
                    <span className="text-white font-medium">{Math.min(priceForecastPage * pricePageSize, totalPriceItems)}</span> of{' '}
                    <span className="text-white font-medium">{totalPriceItems}</span> days (5 per page)
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setPriceForecastPage((p) => Math.max(1, p - 1))}
                      disabled={priceForecastPage <= 1}
                      className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800 text-slate-300 rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer disabled:cursor-not-allowed"
                    >
                      <ChevronLeft className="w-4 h-4" />
                      <span>Previous</span>
                    </button>

                    <div className="flex items-center gap-1">
                      {Array.from({ length: totalPricePages }, (_, i) => i + 1).map((pageNum) => (
                        <button
                          key={pageNum}
                          onClick={() => setPriceForecastPage(pageNum)}
                          className={`w-7 h-7 rounded-lg text-xs font-semibold flex items-center justify-center transition-all cursor-pointer ${
                            priceForecastPage === pageNum
                              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                              : 'bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white'
                          }`}
                        >
                          {pageNum}
                        </button>
                      ))}
                    </div>

                    <button
                      onClick={() => setPriceForecastPage((p) => Math.min(totalPricePages, p + 1))}
                      disabled={priceForecastPage >= totalPricePages}
                      className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:hover:bg-indigo-600 text-white rounded-lg transition-colors flex items-center gap-1.5 shadow-md shadow-indigo-600/20 cursor-pointer disabled:cursor-not-allowed"
                    >
                      <span>Slide to Next Page</span>
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-12">
                <IndianRupee className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                <p className="text-slate-400 text-sm">No price forecast data available.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
