import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { PriceRecommendation } from '../types';
import { DollarSign, Sparkles, Layers, Clock, CheckCircle2, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';
import { ApprovalQueueWidget } from '../components/ApprovalQueueWidget';
import { FiveStagePricingPipeline } from '../components/FiveStagePricingPipeline';
import { NineStepArchitectureFlow } from '../components/NineStepArchitectureFlow';

import { useHotel } from '../context/HotelContext';

export const Pricing: React.FC = () => {
  const { selectedHotel } = useHotel();
  const hotelId = selectedHotel?.hotel_id || 1;
  const [recommendations, setRecommendations] = useState<PriceRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  // Tab State: Default set to 'PENDING'
  const [recTab, setRecTab] = useState<'PENDING' | 'PUBLISHED'>('PENDING');

  // Pagination / Slide state: 5 records max per slide
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 5;

  useEffect(() => {
    fetchPricingData();
  }, [hotelId]);

  const fetchPricingData = async () => {
    try {
      if (recommendations.length === 0) {
        setLoading(true);
      }
      const recs = await apiService.getRecommendations(hotelId);
      setRecommendations(recs);
    } catch (err) {
      console.error('Failed to load pricing recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGlobalRefresh = async () => {
    await fetchPricingData();
    setRefreshKey((prev) => prev + 1);
  };

  const handleTabClick = (tab: 'PENDING' | 'PUBLISHED') => {
    setRecTab(tab);
    setCurrentPage(1);
  };

  const handleGenerateBatch = async () => {
    try {
      setGenerating(true);
      await apiService.recommendPriceBatch(hotelId, 30);
      await handleGlobalRefresh();
    } catch (err) {
      console.error('Failed to generate batch pricing:', err);
    } finally {
      setGenerating(false);
    }
  };

  const pendingRecs = recommendations.filter((r) => {
    const st = (r.status || '').toUpperCase();
    return st === 'PENDING' || st === 'PENDING_APPROVAL' || st.includes('PENDING');
  });

  const publishedRecs = recommendations.filter((r) => {
    const st = (r.status || '').toUpperCase();
    return st === 'PUBLISHED' || st === 'APPLIED' || st === 'APPROVED' || (!st.includes('PENDING') && st.length > 0);
  });

  const displayedRecs = recTab === 'PENDING' ? pendingRecs : publishedRecs;

  const totalItems = displayedRecs.length;
  const totalPages = Math.ceil(totalItems / pageSize) || 1;
  const safeCurrentPage = Math.min(currentPage, totalPages);
  const startIndex = (safeCurrentPage - 1) * pageSize;
  const paginatedRecs = displayedRecs.slice(startIndex, startIndex + pageSize);

  return (
    <div className="space-y-8 font-sans">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2.5 tracking-tight">
            <div className="p-2 bg-gradient-to-tr from-emerald-600 to-emerald-500 rounded-2xl shadow-lg shadow-emerald-600/30">
              <DollarSign className="w-5 h-5 text-white" />
            </div>
            Dynamic Pricing Engine & Rate Approvals
          </h1>
          <p className="text-slate-400 text-xs mt-1">
            Controlled autonomous rate optimization combining pickup pace, competitor positioning, and deterministic guardrail checks.
          </p>
        </div>

        <button
          onClick={handleGenerateBatch}
          disabled={generating}
          className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold rounded-2xl shadow-lg shadow-emerald-600/30 transition-all cursor-pointer"
        >
          {generating ? (
            <>
              <div className="animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-white"></div>
              Calculating 30-Day Rates...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Run 30-Day Price Optimization
            </>
          )}
        </button>
      </div>

      {/* 9-STEP AI REVENUE PIPELINE ARCHITECTURE */}
      <NineStepArchitectureFlow
        hotelId={hotelId}
        refreshKey={refreshKey}
        onRefresh={handleGlobalRefresh}
      />

      {/* 5-STAGE CONTROLLED AUTONOMOUS PRICING PIPELINE */}
      <FiveStagePricingPipeline
        hotelId={hotelId}
        refreshKey={refreshKey}
        onCycleComplete={handleGlobalRefresh}
      />

      {/* HUMAN-IN-THE-LOOP APPROVAL QUEUE WIDGET */}
      <ApprovalQueueWidget
        hotelId={hotelId}
        refreshKey={refreshKey}
        onUpdate={handleGlobalRefresh}
      />

      {/* SPLIT RECOMMENDATIONS GRID: PENDING vs PUBLISHED */}
      <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-500/10 rounded-xl border border-indigo-500/20 text-indigo-400">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-extrabold text-white flex items-center gap-2">
                Active Rate Recommendations Grid
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Showing {recTab === 'PENDING' ? 'pending recommendations awaiting approval' : 'published & applied active rate plans'} (Max 5 per slide)
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Split Tabs: Pending vs Published */}
            <div className="flex items-center gap-1.5 p-1 bg-slate-950 border border-slate-800 rounded-2xl">
              <button
                onClick={() => handleTabClick('PENDING')}
                className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all flex items-center gap-2 cursor-pointer ${
                  recTab === 'PENDING'
                    ? 'bg-gradient-to-r from-amber-600 to-amber-500 text-white shadow-lg shadow-amber-500/20 border border-amber-400/40'
                    : 'text-slate-400 hover:text-white hover:bg-slate-900'
                }`}
              >
                <Clock className="w-3.5 h-3.5 text-amber-300" />
                <span>Pending</span>
                <span className="px-2 py-0.5 text-[10px] font-mono font-extrabold bg-amber-500/20 text-amber-300 rounded-full border border-amber-500/30">
                  {pendingRecs.length}
                </span>
              </button>

              <button
                onClick={() => handleTabClick('PUBLISHED')}
                className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all flex items-center gap-2 cursor-pointer ${
                  recTab === 'PUBLISHED'
                    ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-lg shadow-emerald-500/20 border border-emerald-400/40'
                    : 'text-slate-400 hover:text-white hover:bg-slate-900'
                }`}
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-300" />
                <span>Published</span>
                <span className="px-2 py-0.5 text-[10px] font-mono font-extrabold bg-emerald-500/20 text-emerald-300 rounded-full border border-emerald-500/30">
                  {publishedRecs.length}
                </span>
              </button>
            </div>

            <button
              onClick={fetchPricingData}
              className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-xl border border-slate-700 transition-all cursor-pointer"
              title="Refresh Data"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-48">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
          </div>
        ) : displayedRecs.length === 0 ? (
          <div className="p-12 text-center bg-slate-950/40 rounded-2xl border border-slate-800/60 space-y-2">
            {recTab === 'PENDING' ? (
              <>
                <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
                <h4 className="text-sm font-bold text-white">No Pending Recommendations</h4>
                <p className="text-xs text-slate-400">All price recommendations have been reviewed and published!</p>
              </>
            ) : (
              <>
                <Clock className="w-10 h-10 text-amber-400 mx-auto" />
                <h4 className="text-sm font-bold text-white">No Published Rates Found</h4>
                <p className="text-xs text-slate-400">Published recommendations will appear here once approved.</p>
              </>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-bold">
                    <th className="pb-3 px-4">Stay Date</th>
                    <th className="pb-3 px-4">Room Type</th>
                    <th className="pb-3 px-4">Current Rate</th>
                    <th className="pb-3 px-4">Recommended</th>
                    <th className="pb-3 px-4">Comp Median</th>
                    <th className="pb-3 px-4">Status</th>
                    <th className="pb-3 px-4">Optimization Rationale</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {paginatedRecs.map((rec, i) => {
                    const isRecPending = (rec.status || '').toUpperCase().includes('PENDING');
                    return (
                      <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-3.5 px-4 font-mono text-white font-bold">{rec.stay_date}</td>
                        <td className="py-3.5 px-4 font-semibold text-indigo-400">Room #{rec.room_type_id}</td>
                        <td className="py-3.5 px-4 text-slate-400">₹{rec.current_rate?.toLocaleString()}</td>
                        <td className="py-3.5 px-4 font-extrabold text-emerald-400">₹{rec.recommended_rate?.toLocaleString()}</td>
                        <td className="py-3.5 px-4 text-cyan-400 font-medium">₹{rec.competitor_median?.toLocaleString()}</td>
                        <td className="py-3.5 px-4">
                          <span
                            className={`px-2.5 py-1 text-[11px] rounded-full font-bold border ${
                              isRecPending
                                ? 'bg-amber-500/10 text-amber-400 border-amber-500/30 font-mono'
                                : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 font-mono'
                            }`}
                          >
                            {rec.status || (isRecPending ? 'PENDING' : 'PUBLISHED')}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-slate-400 max-w-xs truncate" title={rec.price_reason}>
                          {rec.price_reason || rec.status}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination / Slide Navigation Controls */}
            {totalItems > 0 && (
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800 text-xs">
                <div className="text-slate-400 font-mono">
                  Showing <span className="font-bold text-white">{startIndex + 1}</span> to{' '}
                  <span className="font-bold text-white">{Math.min(startIndex + pageSize, totalItems)}</span> of{' '}
                  <span className={`font-bold font-mono ${recTab === 'PENDING' ? 'text-amber-400' : 'text-emerald-400'}`}>{totalItems}</span> records (Slide {safeCurrentPage} of {totalPages})
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                    disabled={safeCurrentPage === 1}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 hover:text-white rounded-xl border border-slate-700 transition-all flex items-center gap-1 font-bold cursor-pointer"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    <span>Prev Slide</span>
                  </button>

                  {/* Page Numbers */}
                  <div className="flex items-center gap-1">
                    {Array.from({ length: totalPages }, (_, idx) => idx + 1)
                      .slice(Math.max(0, safeCurrentPage - 3), Math.min(totalPages, safeCurrentPage + 2))
                      .map((pNum) => (
                        <button
                          key={pNum}
                          onClick={() => setCurrentPage(pNum)}
                          className={`w-8 h-8 rounded-xl font-bold font-mono text-xs transition-all cursor-pointer ${
                            safeCurrentPage === pNum
                              ? recTab === 'PENDING'
                                ? 'bg-amber-500 text-white shadow-md shadow-amber-500/30'
                                : 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
                              : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
                          }`}
                        >
                          {pNum}
                        </button>
                      ))}
                  </div>

                  <button
                    onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                    disabled={safeCurrentPage === totalPages}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 hover:text-white rounded-xl border border-slate-700 transition-all flex items-center gap-1 font-bold cursor-pointer"
                  >
                    <span>Next Slide</span>
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

