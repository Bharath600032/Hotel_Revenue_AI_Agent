import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { CompetitorHotel, CompetitorAnalysis } from '../types';
import {
  Users2,
  MapPin,
  Star,
  AlertTriangle,
  TrendingUp,
  Search,
  BarChart3,
  Globe,
  RefreshCw,
  CheckCircle2,
  Plus,
  Pencil,
  Trash2,
  Tag,
  ChevronDown,
  ChevronUp,
  X,
  ExternalLink,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from 'recharts';

import { useHotel } from '../context/HotelContext';

const getTodayDateString = () => new Date().toISOString().split('T')[0];

export const Competitors: React.FC = () => {
  const { selectedHotel } = useHotel();
  const hotelId = selectedHotel?.hotel_id || 1;
  const [stayDate, setStayDate] = useState(getTodayDateString());
  const [myRate, setMyRate] = useState(8500);

  const [competitors, setCompetitors] = useState<CompetitorHotel[]>([]);
  const [analysis, setAnalysis] = useState<CompetitorAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSyncingGoogle, setIsSyncingGoogle] = useState(false);
  const [syncStatusMsg, setSyncStatusMsg] = useState<string | null>(null);
  const [expandedCompId, setExpandedCompId] = useState<number | null>(null);

  // Modal States
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingComp, setEditingComp] = useState<CompetitorHotel | null>(null);
  const [formData, setFormData] = useState({
    competitor_name: '',
    city: selectedHotel?.city || 'Goa',
    star_rating: 4.0,
  });

  useEffect(() => {
    fetchCompetitorData();
  }, [hotelId, stayDate, myRate]);

  const fetchCompetitorData = async () => {
    try {
      setLoading(true);
      const [compList, compAnalysis] = await Promise.all([
        apiService.getCompetitors(hotelId),
        apiService.getCompetitorAnalysis(hotelId, stayDate, myRate),
      ]);
      setCompetitors(compList);
      setAnalysis(compAnalysis);
    } catch (err) {
      console.error('Failed to load competitor data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFetchGoogleLiveRates = async () => {
    try {
      setIsSyncingGoogle(true);
      setSyncStatusMsg(null);
      const res = await apiService.syncGoogleCompetitorRates(hotelId, stayDate);
      setSyncStatusMsg(res.message || `Fetched live rates from Google for ${res.synced_count} competitors.`);
      await fetchCompetitorData();
    } catch (err) {
      console.error('Failed to sync live rates from Google:', err);
      setSyncStatusMsg('Failed to sync live Google rates. Please try again.');
    } finally {
      setIsSyncingGoogle(false);
      setTimeout(() => {
        setSyncStatusMsg(null);
      }, 5000);
    }
  };

  const handleSaveCompetitor = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingComp) {
        await apiService.updateCompetitor(hotelId, editingComp.competitor_id, formData);
        setSyncStatusMsg(`Updated competitor "${formData.competitor_name}".`);
      } else {
        await apiService.addCompetitor(hotelId, formData);
        setSyncStatusMsg(`Added new competitor "${formData.competitor_name}".`);
      }
      setShowAddModal(false);
      setEditingComp(null);
      setFormData({ competitor_name: '', city: selectedHotel?.city || 'Goa', star_rating: 4.0 });
      await fetchCompetitorData();
    } catch (err) {
      console.error('Failed to save competitor:', err);
      alert('Error saving competitor details.');
    }
  };

  const handleDeleteCompetitor = async (competitorId: number, name: string) => {
    if (!window.confirm(`Are you sure you want to remove "${name}" from your competitive set?`)) return;
    try {
      await apiService.deleteCompetitor(hotelId, competitorId);
      setSyncStatusMsg(`Removed competitor "${name}".`);
      await fetchCompetitorData();
    } catch (err) {
      console.error('Failed to delete competitor:', err);
      alert('Error deleting competitor.');
    }
  };

  const openEditModal = (comp: CompetitorHotel) => {
    setEditingComp(comp);
    setFormData({
      competitor_name: comp.competitor_name,
      city: comp.city,
      star_rating: comp.star_rating,
    });
    setShowAddModal(true);
  };

  const chartData = analysis
    ? [
        {
          name: selectedHotel?.hotel_name || 'Our Hotel',
          rate: analysis.my_rate || analysis.my_hotel_rate,
          isSelf: true,
          ota: 'Direct Rate',
          source: 'PMS_LIVE',
        },
        ...(analysis.competitor_rates || []).map((cr) => {
          const lowestItem = cr.ota_rates?.find((r) => r.is_lowest);
          const lRate = lowestItem ? lowestItem.rate : cr.rate;
          const lOta = lowestItem ? lowestItem.ota_name : (cr.lowest_ota_name || cr.ota_name || 'Booking.com');
          return {
            name: cr.competitor_name,
            rate: lRate,
            isSelf: false,
            ota: lOta,
            source: cr.source || 'GOOGLE_LIVE',
          };
        }),
      ]
    : [];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Users2 className="w-7 h-7 text-indigo-400" />
            Competitor Intelligence & Rate Shopping
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Track custom competitive set positioning, lowest OTA provider prices, and real-time Google search trends.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => {
              setEditingComp(null);
              setFormData({ competitor_name: '', city: selectedHotel?.city || 'Goa', star_rating: 4.0 });
              setShowAddModal(true);
            }}
            className="flex items-center gap-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-white font-medium text-xs rounded-xl border border-slate-700 transition-all"
          >
            <Plus className="w-4 h-4 text-emerald-400" />
            Add Competitor
          </button>

          <button
            onClick={handleFetchGoogleLiveRates}
            disabled={isSyncingGoogle}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 text-white font-medium text-xs rounded-xl shadow-lg transition-all"
          >
            {isSyncingGoogle ? (
              <RefreshCw className="w-4 h-4 animate-spin text-white" />
            ) : (
              <Globe className="w-4 h-4 text-sky-300" />
            )}
            {isSyncingGoogle ? 'Fetching Live Google Rates...' : 'Fetch Live Prices from Google'}
          </button>

          <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 p-2 rounded-xl text-xs">
            <span className="text-slate-400">Stay Date:</span>
            <input
              type="date"
              value={stayDate}
              onChange={(e) => setStayDate(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-white px-2 py-1 rounded"
            />
            <span className="text-slate-400">My Rate (₹):</span>
            <input
              type="number"
              value={myRate}
              onChange={(e) => setMyRate(Number(e.target.value))}
              className="bg-slate-950 border border-slate-800 text-emerald-400 font-bold px-2 py-1 rounded w-24"
            />
          </div>
        </div>
      </div>

      {/* Notification Toast Banner */}
      {syncStatusMsg && (
        <div className="flex items-center gap-2 p-4 bg-indigo-950/80 border border-indigo-700/60 rounded-xl text-indigo-200 text-sm animate-fade-in">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
          <span>{syncStatusMsg}</span>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500"></div>
        </div>
      ) : (
        <>
          {/* Analysis Metrics Cards */}
          {analysis && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="p-5 bg-slate-900/80 border border-slate-800 rounded-2xl">
                <span className="text-xs text-slate-400">Your Current Rate</span>
                <p className="text-2xl font-bold text-emerald-400 mt-2">
                  ₹{(analysis.my_rate || analysis.my_hotel_rate)?.toLocaleString()}
                </p>
                <span className="text-xs text-slate-500">Target stay date rate</span>
              </div>

              <div className="p-5 bg-slate-900/80 border border-slate-800 rounded-2xl">
                <span className="text-xs text-slate-400">Comp Set Median</span>
                <p className="text-2xl font-bold text-cyan-400 mt-2">
                  ₹{(analysis.median_rate || analysis.competitor_median)?.toLocaleString()}
                </p>
                <span className="text-xs text-slate-500">Market middle tier</span>
              </div>

              <div className="p-5 bg-slate-900/80 border border-slate-800 rounded-2xl">
                <span className="text-xs text-slate-400">Market Min - Max Spread</span>
                <p className="text-2xl font-bold text-indigo-400 mt-2">
                  ₹{(analysis.min_rate || analysis.competitor_min)?.toLocaleString()} - ₹
                  {(analysis.max_rate || analysis.competitor_max)?.toLocaleString()}
                </p>
                <span className="text-xs text-slate-500">Full price spread</span>
              </div>

              <div className="p-5 bg-slate-900/80 border border-slate-800 rounded-2xl">
                <span className="text-xs text-slate-400">Price Gap % vs Median</span>
                <p
                  className={`text-2xl font-bold mt-2 ${
                    analysis.price_gap_pct > 0 ? 'text-amber-400' : 'text-emerald-400'
                  }`}
                >
                  {analysis.price_gap_pct > 0 ? `+${analysis.price_gap_pct}%` : `${analysis.price_gap_pct}%`}
                </p>
                <span className="text-xs text-indigo-300 font-semibold">{analysis.positioning}</span>
              </div>
            </div>
          )}

          {/* Recharts Rate Shopping Chart */}
          {chartData.length > 0 && (
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-indigo-400" />
                  Rate Comparison Bar Chart — Stay Date {stayDate}
                </h3>
                <div className="flex items-center gap-2">
                  <span className="flex items-center gap-1.5 px-2.5 py-1 bg-blue-950/80 border border-blue-800/60 rounded-full text-xs text-blue-300 font-medium">
                    <Globe className="w-3.5 h-3.5 text-blue-400" />
                    Google Live Prices & Lowest OTA
                  </span>
                </div>
              </div>

              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="name" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <YAxis
                      stroke="#64748b"
                      label={{ value: 'Rate (₹)', angle: -90, position: 'insideLeft', fill: '#64748b' }}
                    />
                    <Tooltip
                      content={({ active, payload }: any) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload;
                          return (
                            <div className="bg-slate-950/95 border border-slate-700 p-3.5 rounded-xl shadow-2xl space-y-1.5 backdrop-blur-md">
                              <p className="font-bold text-white text-sm flex items-center gap-1.5">
                                <span className={`w-2.5 h-2.5 rounded-full ${data.isSelf ? 'bg-emerald-400' : 'bg-indigo-400'}`} />
                                {data.name}
                              </p>
                              <div className="text-xs space-y-1.5 pt-1.5 border-t border-slate-800">
                                <div className="flex items-center justify-between gap-4">
                                  <span className="text-slate-400">Lowest Price:</span>
                                  <span className="font-extrabold text-emerald-400 text-sm">₹{Number(data.rate).toLocaleString()}</span>
                                </div>
                                {!data.isSelf && (
                                  <div className="flex items-center justify-between gap-4">
                                    <span className="text-slate-400">Lowest OTA Channel:</span>
                                    <span className="font-semibold text-sky-300 bg-sky-950/80 px-2 py-0.5 rounded border border-sky-800/50">
                                      {data.ota}
                                    </span>
                                  </div>
                                )}
                                {data.isSelf && (
                                  <div className="flex items-center justify-between gap-4">
                                    <span className="text-slate-400">Rate Source:</span>
                                    <span className="font-semibold text-emerald-300 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/50">
                                      Our Hotel Rate
                                    </span>
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Bar dataKey="rate" radius={[8, 8, 0, 0]}>
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.isSelf ? '#10b981' : '#6366f1'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Registered Competitors & Lowest OTA Price Section */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Users2 className="w-5 h-5 text-indigo-400" />
                  Primary Competitive Set ({competitors.length} Hotels)
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Showing lowest OTA provider prices and live rates scraped from Google.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {competitors.map((comp) => {
                const compRateObj = analysis?.competitor_rates?.find(
                  (r) => r.competitor_id === comp.competitor_id || r.competitor_name === comp.competitor_name
                );
                const isExpanded = expandedCompId === comp.competitor_id;
                const lowestOtaItem = compRateObj?.ota_rates?.find((r) => r.is_lowest);
                const lowestOtaPrice = lowestOtaItem ? lowestOtaItem.rate : compRateObj?.rate;
                const lowestOtaName = lowestOtaItem
                  ? lowestOtaItem.ota_name
                  : compRateObj?.lowest_ota_name || compRateObj?.ota_name || 'Booking.com';

                return (
                  <div
                    key={comp.competitor_id}
                    className="p-5 bg-slate-950/70 border border-slate-800 rounded-2xl space-y-4 hover:border-indigo-500/50 transition-all shadow-md group"
                  >
                    {/* Header */}
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-bold text-white text-base group-hover:text-indigo-300 transition-colors">
                            {comp.competitor_name}
                          </h4>
                        </div>
                        <span className="text-xs text-slate-400 flex items-center gap-1 mt-1">
                          <MapPin className="w-3.5 h-3.5 text-indigo-400" />
                          {comp.city}
                        </span>
                      </div>

                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={() => openEditModal(comp)}
                          title="Edit Competitor Name & Details"
                          className="p-1.5 text-slate-400 hover:text-white bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg transition-all"
                        >
                          <Pencil className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDeleteCompetitor(comp.competitor_id, comp.competitor_name)}
                          title="Remove Competitor"
                          className="p-1.5 text-slate-400 hover:text-rose-400 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg transition-all"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                        <div className="flex items-center text-amber-400 text-xs font-bold bg-amber-950/40 border border-amber-800/40 px-2 py-1 rounded-full">
                          <Star className="w-3.5 h-3.5 fill-amber-400 mr-1" />
                          {comp.star_rating}★
                        </div>
                      </div>
                    </div>

                    {/* Lowest Price & OTA Provider */}
                    <div className="p-3.5 bg-slate-900/90 border border-slate-800 rounded-xl space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-slate-400 font-medium flex items-center gap-1.5">
                          <Tag className="w-3.5 h-3.5 text-emerald-400" />
                          Lowest OTA Price
                        </span>
                        <span className="px-2 py-0.5 bg-emerald-950/80 border border-emerald-700/60 rounded text-[11px] text-emerald-300 font-semibold flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                          {lowestOtaName}
                        </span>
                      </div>

                      <div className="flex items-baseline justify-between pt-1">
                        <p className="text-2xl font-extrabold text-emerald-400">
                          {lowestOtaPrice ? `₹${lowestOtaPrice.toLocaleString()}` : 'Live Fetch Pending'}
                        </p>
                        <span className="text-xs text-slate-500 font-mono">
                          {compRateObj?.source || 'GOOGLE_LIVE'}
                        </span>
                      </div>
                    </div>

                    {/* Expand Multi-OTA Comparison */}
                    {compRateObj?.ota_rates && compRateObj.ota_rates.length > 0 && (
                      <div className="space-y-2">
                        <button
                          onClick={() => setExpandedCompId(isExpanded ? null : comp.competitor_id)}
                          className="w-full flex items-center justify-between text-xs text-indigo-300 font-medium py-1 px-2 hover:bg-slate-900/50 rounded-lg transition-colors"
                        >
                          <span>View All OTA Channel Rates ({compRateObj.ota_rates.length})</span>
                          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>

                        {isExpanded && (
                          <div className="space-y-1.5 pt-2 border-t border-slate-800 animate-fade-in">
                            {compRateObj.ota_rates.map((otaItem, idx) => (
                              <div
                                key={idx}
                                className={`flex justify-between items-center text-xs p-2 rounded-lg ${
                                  otaItem.is_lowest
                                    ? 'bg-emerald-950/40 border border-emerald-800/60 text-emerald-200'
                                    : 'bg-slate-900/50 text-slate-300'
                                }`}
                              >
                                <span className="flex items-center gap-1.5">
                                  {otaItem.ota_name}
                                  {otaItem.is_lowest && (
                                    <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded font-bold">
                                      LOWEST
                                    </span>
                                  )}
                                </span>
                                <span className="font-bold">₹{otaItem.rate.toLocaleString()}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}

      {/* Add / Edit Competitor Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-5 shadow-2xl animate-fade-in">
            <div className="flex justify-between items-center border-b border-slate-800 pb-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Users2 className="w-5 h-5 text-indigo-400" />
                {editingComp ? 'Customize Competitor Property' : 'Add New Competitor Hotel'}
              </h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveCompetitor} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-400 mb-1">Competitor Hotel Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Taj Exotica Resort Goa"
                  value={formData.competitor_name}
                  onChange={(e) => setFormData({ ...formData, competitor_name: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-400 mb-1">City Location</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Goa"
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-400 mb-1">Star Rating (1.0 to 5.0)</label>
                <input
                  type="number"
                  step="0.5"
                  min="1"
                  max="5"
                  required
                  value={formData.star_rating}
                  onChange={(e) => setFormData({ ...formData, star_rating: parseFloat(e.target.value) })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-medium text-xs rounded-xl shadow-lg transition-all"
                >
                  {editingComp ? 'Save Changes' : 'Add Competitor'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
