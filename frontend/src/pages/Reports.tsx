import React, { useState } from 'react';
import { apiService } from '../services/api';
import { FileSpreadsheet, Download, Calendar, CheckCircle } from 'lucide-react';

export const Reports: React.FC = () => {
  const [hotelId] = useState(1);
  const [startDate, setStartDate] = useState('2026-09-01');
  const [endDate, setEndDate] = useState('2026-12-31');
  const [downloading, setDownloading] = useState(false);
  const [successMsg, setSuccessMsg] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    setSuccessMsg(false);
    try {
      const url = apiService.getReportDownloadUrl(hotelId, startDate, endDate);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Pricing_Report_Hotel_${hotelId}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setSuccessMsg(true);
    } catch (err) {
      console.error('Failed to download report:', err);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <FileSpreadsheet className="w-7 h-7 text-emerald-400" />
          Executive Reports & Excel Export Generator
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Export formatted 365-day pricing recommendations, occupancy projections, and competitor medians.
        </p>
      </div>

      {/* Report Generator Card */}
      <div className="p-8 bg-slate-900 border border-slate-800 rounded-2xl space-y-6">
        <h3 className="text-lg font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-4">
          <Calendar className="w-5 h-5 text-indigo-400" />
          Configure Excel Report Horizon
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-xs text-slate-300 font-medium">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 text-white text-sm p-3 rounded-xl"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs text-slate-300 font-medium">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 text-white text-sm p-3 rounded-xl"
            />
          </div>
        </div>

        <div className="pt-4 flex items-center justify-between border-t border-slate-800">
          <div className="text-xs text-slate-400">
            Includes: <span className="text-slate-200 font-semibold">Recommended Rates, Current Rates, Demand Index, Competitor Medians</span>
          </div>

          <button
            onClick={handleDownload}
            disabled={downloading}
            className="flex items-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-bold rounded-xl shadow-lg shadow-emerald-600/30 transition-all"
          >
            {downloading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Generating Excel Sheet...
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                Download Formatted .XLSX
              </>
            )}
          </button>
        </div>

        {successMsg && (
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 text-xs flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            Excel report generated and downloaded successfully!
          </div>
        )}
      </div>
    </div>
  );
};
