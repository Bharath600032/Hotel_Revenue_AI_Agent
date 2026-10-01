import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { PriceRecommendation } from '../types';
import { ShieldAlert, CheckCircle2, Edit3, XCircle, RefreshCw, AlertCircle } from 'lucide-react';

interface ApprovalQueueWidgetProps {
  hotelId?: number;
  onUpdate?: () => void;
}

export const ApprovalQueueWidget: React.FC<ApprovalQueueWidgetProps> = ({ hotelId = 1, onUpdate }) => {
  const [pendingItems, setPendingItems] = useState<PriceRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // Modal State for Override / Reject
  const [overrideModalRec, setOverrideModalRec] = useState<PriceRecommendation | null>(null);
  const [overrideRateInput, setOverrideRateInput] = useState<number>(0);
  const [overrideReasonInput, setOverrideReasonInput] = useState<string>('');

  const [rejectModalRec, setRejectModalRec] = useState<PriceRecommendation | null>(null);
  const [rejectReasonInput, setRejectReasonInput] = useState<string>('');

  useEffect(() => {
    fetchPendingQueue();
  }, [hotelId]);

  const fetchPendingQueue = async () => {
    try {
      setLoading(true);
      const data = await apiService.getPendingApprovals(hotelId);
      setPendingItems(data);
    } catch (err) {
      console.error('Failed to load pending approvals:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (rec: PriceRecommendation) => {
    if (!rec.recommendation_id) return;
    try {
      await apiService.approveRecommendation(hotelId, rec.recommendation_id);
      setActionSuccess(`Approved rate ₹${rec.recommended_rate.toLocaleString()} for ${rec.stay_date}`);
      await fetchPendingQueue();
      if (onUpdate) onUpdate();
    } catch (err) {
      console.error('Failed to approve recommendation:', err);
    }
  };

  const handleSubmitOverride = async () => {
    if (!overrideModalRec?.recommendation_id) return;
    try {
      await apiService.overrideRecommendation(
        hotelId,
        overrideModalRec.recommendation_id,
        overrideRateInput,
        overrideReasonInput || 'Manager custom rate override'
      );
      setActionSuccess(`Overrode rate to ₹${overrideRateInput.toLocaleString()} for ${overrideModalRec.stay_date}`);
      setOverrideModalRec(null);
      await fetchPendingQueue();
      if (onUpdate) onUpdate();
    } catch (err) {
      console.error('Failed to override rate:', err);
    }
  };

  const handleSubmitReject = async () => {
    if (!rejectModalRec?.recommendation_id) return;
    try {
      await apiService.rejectRecommendation(
        hotelId,
        rejectModalRec.recommendation_id,
        rejectReasonInput || 'Rejected by revenue manager'
      );
      setActionSuccess(`Rejected recommendation for ${rejectModalRec.stay_date}`);
      setRejectModalRec(null);
      await fetchPendingQueue();
      if (onUpdate) onUpdate();
    } catch (err) {
      console.error('Failed to reject rate:', err);
    }
  };

  return (
    <div className="p-6 bg-slate-900/80 backdrop-blur border border-amber-500/30 rounded-3xl space-y-4 shadow-xl">
      {/* Widget Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-amber-500/10 rounded-2xl border border-amber-500/20">
            <ShieldAlert className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <h3 className="text-base font-extrabold text-white flex items-center gap-2">
              Human Approval Queue
              <span className="px-2.5 py-0.5 bg-amber-500/20 text-amber-400 text-xs font-bold rounded-full border border-amber-500/30">
                {pendingItems.length} Pending
              </span>
            </h3>
            <p className="text-xs text-slate-400">High-impact price recommendations exceeding automatic guardrail limit (±10%)</p>
          </div>
        </div>

        <button
          onClick={fetchPendingQueue}
          className="px-3 py-1.5 text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-xl transition-all text-xs font-semibold flex items-center gap-1.5 border border-slate-700/60"
          title="Refresh Queue"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {actionSuccess && (
        <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl text-emerald-400 text-xs font-semibold flex items-center justify-between">
          <span className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            {actionSuccess}
          </span>
          <button onClick={() => setActionSuccess(null)} className="text-slate-400 hover:text-white text-xs">
            ✕
          </button>
        </div>
      )}

      {/* Pending Items List */}
      {loading ? (
        <div className="flex justify-center items-center h-32">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-amber-500"></div>
        </div>
      ) : pendingItems.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {pendingItems.map((rec) => {
            const shiftPct = rec.current_rate
              ? (((rec.recommended_rate - rec.current_rate) / rec.current_rate) * 100).toFixed(1)
              : '0.0';
            return (
              <div
                key={rec.recommendation_id}
                className="p-4 bg-slate-950/80 border border-slate-800/80 hover:border-indigo-500/40 rounded-2xl space-y-3 transition-all shadow-md"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-xs font-mono font-bold text-indigo-400">{rec.stay_date}</span>
                    <h4 className="text-sm font-bold text-white mt-0.5">Room Type #{rec.room_type_id}</h4>
                  </div>
                  <span className="px-2 py-0.5 bg-amber-500/10 text-amber-400 text-[10px] font-bold rounded-full border border-amber-500/20">
                    &gt;10% SHIFT
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-2 bg-slate-900/80 p-2.5 rounded-xl text-center text-xs border border-slate-800/60">
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase">Current</span>
                    <p className="font-extrabold text-slate-300">₹{rec.current_rate?.toLocaleString()}</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase">AI Proposed</span>
                    <p className="font-extrabold text-emerald-400">₹{rec.recommended_rate?.toLocaleString()}</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase">Variation</span>
                    <p className={`font-extrabold ${Number(shiftPct) > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {Number(shiftPct) > 0 ? `+${shiftPct}%` : `${shiftPct}%`}
                    </p>
                  </div>
                </div>

                <p className="text-xs text-slate-400 italic bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/50">
                  "{rec.price_reason || rec.status || 'High demand forecast requires rate adjustment'}"
                </p>

                {/* Actions */}
                <div className="flex items-center gap-2 pt-1">
                  <button
                    onClick={() => handleApprove(rec)}
                    className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition-all shadow-md shadow-emerald-600/20"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Approve
                  </button>

                  <button
                    onClick={() => {
                      setOverrideModalRec(rec);
                      setOverrideRateInput(rec.recommended_rate);
                    }}
                    className="flex-1 py-2 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition-all shadow-md shadow-indigo-600/20"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                    Override
                  </button>

                  <button
                    onClick={() => setRejectModalRec(rec)}
                    className="py-2 px-3 bg-slate-800 hover:bg-rose-600 text-slate-300 hover:text-white text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition-all"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    Reject
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-6 text-slate-400 text-xs font-medium">
          🎉 All price recommendations are verified or operating within automated guardrail limits!
        </div>
      )}

      {/* OVERRIDE MODAL */}
      {overrideModalRec && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl max-w-md w-full space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Override AI Recommendation Rate</h3>
            <p className="text-xs text-slate-400">
              Stay Date: <strong className="text-white font-mono">{overrideModalRec.stay_date}</strong> | Room Type #{overrideModalRec.room_type_id}
            </p>

            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-bold">Custom Override Rate (₹)</label>
              <input
                type="number"
                value={overrideRateInput}
                onChange={(e) => setOverrideRateInput(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 text-emerald-400 font-bold p-3 rounded-2xl text-lg font-mono focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-bold">Reason / Note for Immutable Audit Log</label>
              <textarea
                value={overrideReasonInput}
                onChange={(e) => setOverrideReasonInput(e.target.value)}
                placeholder="e.g., Match local competitor surge promotion..."
                className="w-full bg-slate-950 border border-slate-800 text-white text-xs p-3 rounded-2xl h-20 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="flex gap-2 pt-2">
              <button
                onClick={() => setOverrideModalRec(null)}
                className="flex-1 py-2.5 bg-slate-800 text-slate-300 text-xs font-bold rounded-2xl hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmitOverride}
                className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-2xl shadow-lg shadow-indigo-600/30"
              >
                Submit Override Rate
              </button>
            </div>
          </div>
        </div>
      )}

      {/* REJECT MODAL */}
      {rejectModalRec && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl max-w-md w-full space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Reject Recommendation</h3>
            <p className="text-xs text-slate-400">
              Stay Date: <strong className="text-white font-mono">{rejectModalRec.stay_date}</strong>
            </p>

            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-bold">Rejection Reason</label>
              <textarea
                value={rejectReasonInput}
                onChange={(e) => setRejectReasonInput(e.target.value)}
                placeholder="e.g. Demand expectations lower than model forecast..."
                className="w-full bg-slate-950 border border-slate-800 text-white text-xs p-3 rounded-2xl h-24 focus:outline-none focus:border-rose-500"
              />
            </div>

            <div className="flex gap-2 pt-2">
              <button
                onClick={() => setRejectModalRec(null)}
                className="flex-1 py-2.5 bg-slate-800 text-slate-300 text-xs font-bold rounded-2xl hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmitReject}
                className="flex-1 py-2.5 bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold rounded-2xl shadow-lg shadow-rose-600/30"
              >
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

