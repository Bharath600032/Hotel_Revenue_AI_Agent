import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { PriceRecommendation } from '../types';
import { DollarSign, Sparkles, Layers } from 'lucide-react';
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

  useEffect(() => {
    fetchPricingData();
  }, [hotelId]);

  const fetchPricingData = async () => {
    try {
      setLoading(true);
      const recs = await apiService.getRecommendations(hotelId);
      setRecommendations(recs);
    } catch (err) {
      console.error('Failed to load pricing recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateBatch = async () => {
    try {
      setGenerating(true);
      await apiService.recommendPriceBatch(hotelId, 30);
      await fetchPricingData();
    } catch (err) {
      console.error('Failed to generate batch pricing:', err);
    } finally {
      setGenerating(false);
    }
  };

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
          className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold rounded-2xl shadow-lg shadow-emerald-600/30 transition-all"
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
      <NineStepArchitectureFlow />

      {/* 5-STAGE CONTROLLED AUTONOMOUS PRICING PIPELINE */}
      <FiveStagePricingPipeline hotelId={hotelId} onCycleComplete={fetchPricingData} />

      {/* HUMAN-IN-THE-LOOP APPROVAL QUEUE WIDGET */}
      <ApprovalQueueWidget hotelId={hotelId} onUpdate={fetchPricingData} />


      {/* ALL PERSISTED RECOMMENDATIONS TABLE */}
      <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
          <h3 className="text-base font-extrabold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-indigo-400" />
            Active Rate Recommendations Grid
          </h3>
          <span className="text-xs text-slate-400 font-mono">
            Total Records: <strong className="text-white">{recommendations.length}</strong>
          </span>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-48">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
          </div>
        ) : (
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
                {recommendations.map((rec, i) => (
                  <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono text-white font-bold">{rec.stay_date}</td>
                    <td className="py-3.5 px-4 font-semibold text-indigo-400">Room #{rec.room_type_id}</td>
                    <td className="py-3.5 px-4 text-slate-400">₹{rec.current_rate?.toLocaleString()}</td>
                    <td className="py-3.5 px-4 font-extrabold text-emerald-400">₹{rec.recommended_rate?.toLocaleString()}</td>
                    <td className="py-3.5 px-4 text-cyan-400 font-medium">₹{rec.competitor_median?.toLocaleString()}</td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`px-2.5 py-1 text-[11px] rounded-full font-bold border ${
                          rec.status === 'APPLIED' || rec.status === 'APPROVED'
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                            : rec.status === 'PENDING' || rec.status === 'PENDING_APPROVAL'
                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                            : 'bg-slate-800 text-slate-400 border-slate-700'
                        }`}
                      >
                        {rec.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 max-w-xs truncate" title={rec.price_reason}>
                      {rec.price_reason || rec.status}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

