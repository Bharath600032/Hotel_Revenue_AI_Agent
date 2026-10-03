import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { ForecastItem, RoomType } from '../types';
import { LineChart as LineChartIcon, Play, Cpu, Calendar, TrendingUp, CheckCircle2 } from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

import { useHotel } from '../context/HotelContext';

export const Forecasting: React.FC = () => {
  const { selectedHotel } = useHotel();
  const hotelId = selectedHotel?.hotel_id || 1;
  const [roomTypes, setRoomTypes] = useState<RoomType[]>([]);
  const [roomTypeId, setRoomTypeId] = useState(1);
  const [horizonDays, setHorizonDays] = useState(30);
  const [forecasts, setForecasts] = useState<ForecastItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    fetchRoomTypes();
  }, [hotelId]);

  useEffect(() => {
    if (roomTypeId) {
      loadForecasts();
    }
  }, [hotelId, roomTypeId]);

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
      setLoading(true);
      const today = new Date().toISOString().split('T')[0];
      const endDate = new Date(Date.now() + horizonDays * 86400000).toISOString().split('T')[0];
      const data = await apiService.getForecasts(hotelId, roomTypeId, today, endDate);
      setForecasts(data);
    } catch (err) {
      console.error('Failed to load forecasts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunPipeline = async () => {
    try {
      setRunning(true);
      const today = new Date().toISOString().split('T')[0];
      await apiService.runForecast(hotelId, roomTypeId, today, horizonDays);
      await loadForecasts();
    } catch (err) {
      console.error('Failed to execute forecast pipeline:', err);
    } finally {
      setRunning(false);
    }
  };

  const chartData = forecasts.map((f) => ({
    date: f.stay_date.slice(5),
    Demand: Math.round(f.predicted_demand),
    UpperBound: Math.round(f.upper_bound),
    LowerBound: Math.round(f.lower_bound),
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <LineChartIcon className="w-7 h-7 text-indigo-400" />
            Demand Forecasting Engine
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Execute Naive, Moving Average, Seasonal Naive, SARIMAX, and XGBoost machine learning models.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          <select
            value={roomTypeId}
            onChange={(e) => setRoomTypeId(Number(e.target.value))}
            className="bg-slate-900 border border-slate-800 text-white text-xs px-3 py-2 rounded-xl cursor-pointer"
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

          <button
            onClick={handleRunPipeline}
            disabled={running}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-600/30 transition-all"
          >
            {running ? (
              <>
                <div className="animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-white"></div>
                Executing Pipeline...
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5" />
                Run Forecast Pipeline
              </>
            )}
          </button>
        </div>
      </div>

      {/* Ensemble Models Banner */}
      <div className="p-6 bg-slate-900/80 border border-slate-800 rounded-2xl grid grid-cols-1 md:grid-cols-5 gap-3 text-center">
        {['Naive Baseline', 'Moving Average', 'Seasonal Naive', 'SARIMAX Time-Series', 'XGBoost Machine Learning'].map(
          (m, idx) => (
            <div key={idx} className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 flex items-center gap-2 text-left">
              <Cpu className="w-4 h-4 text-indigo-400 flex-shrink-0" />
              <div>
                <p className="text-xs font-bold text-white leading-tight">{m}</p>
                <span className="text-[10px] text-emerald-400">Active Pipeline</span>
              </div>
            </div>
          )
        )}
      </div>

      {/* Visual Demand Forecast Chart */}
      {forecasts.length > 0 && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-emerald-400" />
              30-Day Projected Demand Curve & Confidence Bounds
            </h3>
            <span className="text-xs text-indigo-400 font-mono font-semibold">Ensemble AI Model</span>
          </div>

          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData}>
                <defs>
                  <linearGradient id="colorBound" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" />
                <YAxis stroke="#64748b" label={{ value: 'Rooms', angle: -90, position: 'insideLeft', fill: '#64748b' }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} />
                <Legend />
                <Area type="monotone" dataKey="UpperBound" fill="url(#colorBound)" stroke="#059669" strokeDasharray="3 3" name="Upper Confidence Bound" />
                <Line type="monotone" dataKey="Demand" stroke="#6366f1" strokeWidth={3} dot={{ r: 4 }} name="Predicted Demand" />
                <Line type="monotone" dataKey="LowerBound" stroke="#f59e0b" strokeDasharray="3 3" name="Lower Confidence Bound" />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Forecast Output Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
        <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-indigo-400" />
          Predicted Room Demand Horizon ({forecasts.length} Days)
        </h3>

        {loading ? (
          <div className="flex justify-center items-center h-48">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
          </div>
        ) : forecasts.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider">
                  <th className="pb-3 px-3">Stay Date</th>
                  <th className="pb-3 px-3">Model Used</th>
                  <th className="pb-3 px-3">Predicted Demand</th>
                  <th className="pb-3 px-3">Confidence Interval (Lower - Upper)</th>
                  <th className="pb-3 px-3">Confidence Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {forecasts.map((f, i) => (
                  <tr key={i} className="hover:bg-slate-800/30">
                    <td className="py-3 px-3 font-mono font-medium text-white">{f.stay_date}</td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 bg-indigo-500/10 text-indigo-400 text-xs rounded border border-indigo-500/20 font-semibold">
                        {f.model_name}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-bold text-emerald-400">{Math.round(f.predicted_demand)} Rooms</td>
                    <td className="py-3 px-3 text-slate-300">
                      {Math.round(f.lower_bound)} - {Math.round(f.upper_bound)} Rooms
                    </td>
                    <td className="py-3 px-3">
                      <span className="text-xs text-emerald-400 font-semibold">
                        {(f.confidence_score * 100).toFixed(0)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
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
  );
};

