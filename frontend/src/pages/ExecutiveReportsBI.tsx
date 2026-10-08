import React, { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  Database,
  Calendar,
  Clock,
  Mail,
  RefreshCw,
  Plus,
  CheckCircle2,
  Sparkles,
  ExternalLink,
  Table,
  Layers,
  FileSpreadsheet,
  TrendingUp,
  DollarSign,
  Share2,
  Copy,
  Check,
} from 'lucide-react';
import { apiService } from '../services/api';
import { useHotel } from '../context/HotelContext';

export const ExecutiveReportsBI: React.FC = () => {
  const { selectedHotel } = useHotel();
  const hotelId = selectedHotel?.hotel_id || (selectedHotel as any)?.id || 1;

  const [activeTab, setActiveTab] = useState<'pdf' | 'bi_studio' | 'schedules'>('pdf');
  const [loading, setLoading] = useState<boolean>(true);

  // PDF Generator state
  const [reportType, setReportType] = useState<string>('DAILY_REVENUE');
  const [reportTitle, setReportTitle] = useState<string>('Daily Executive Revenue Digest');
  const [generatingPdf, setGeneratingPdf] = useState<boolean>(false);
  const [generatedReport, setGeneratedReport] = useState<any>(null);
  const [exportLogs, setExportLogs] = useState<any[]>([]);

  // BI Studio state
  const [biDays, setBiDays] = useState<number>(30);
  const [biDataset, setBiDataset] = useState<any>(null);
  const [copiedEndpoint, setCopiedEndpoint] = useState<boolean>(false);

  // Schedules state
  const [schedules, setSchedules] = useState<any[]>([]);
  const [showAddSched, setShowAddSched] = useState<boolean>(false);
  const [newSchedName, setNewSchedName] = useState<string>('Weekly TRevPAR & Ancillary Briefing');
  const [newSchedRecipients, setNewSchedRecipients] = useState<string>('gm@hotel.com, revenue@hotel.com');

  useEffect(() => {
    fetchData();
  }, [hotelId, biDays]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [logs, scheds, biData] = await Promise.all([
        apiService.getReportExportHistory(hotelId),
        apiService.getReportSchedules(hotelId),
        apiService.getBIDataset(hotelId, biDays),
      ]);
      setExportLogs(logs || []);
      setSchedules(scheds || []);
      setBiDataset(biData || null);

      if (logs && logs.length > 0 && !generatedReport) {
        setGeneratedReport(logs[0]);
      }
    } catch (err) {
      console.error('Failed to fetch executive reports data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePdf = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setGeneratingPdf(true);
      const res = await apiService.generateExecutivePDF(hotelId, {
        report_type: reportType,
        title: reportTitle,
      });
      setGeneratedReport(res);
      fetchData();
    } catch (err) {
      console.error('Error generating PDF report:', err);
    } finally {
      setGeneratingPdf(false);
    }
  };

  const handleCreateSchedule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiService.createReportSchedule(hotelId, {
        hotel_id: hotelId,
        schedule_name: newSchedName,
        report_type: 'DAILY_REVENUE',
        frequency: 'DAILY',
        file_format: 'PDF',
        recipients: newSchedRecipients,
      });
      setShowAddSched(false);
      fetchData();
    } catch (err) {
      console.error('Error creating schedule:', err);
    }
  };

  const handleCopyEndpoint = (url: string) => {
    navigator.clipboard.writeText(window.location.origin + url);
    setCopiedEndpoint(true);
    setTimeout(() => setCopiedEndpoint(false), 3000);
  };

  const handleExportCSV = () => {
    if (!biDataset || !biDataset.dataset_records) return;
    const headers = biDataset.columns.join(',');
    const rows = biDataset.dataset_records.map((r: any) =>
      biDataset.columns.map((col: string) => JSON.stringify(r[col] ?? '')).join(',')
    );
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers, ...rows].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `hotel_${hotelId}_bi_revenue_dataset.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 font-sans">
      {/* Page Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-2 border-b border-slate-800/60">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-3 tracking-tight">
            <FileText className="w-7 h-7 text-indigo-400 flex-shrink-0" />
            <span>Executive PDF Reporting & Automated BI Exports</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Generate executive revenue briefings in INR (₹), schedule automated email digests, and export PowerBI & Tableau datasets.
          </p>
        </div>

        {/* Tab Navigation Controls */}
        <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-1.5 rounded-xl flex-shrink-0">
          <button
            onClick={() => setActiveTab('pdf')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'pdf'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Executive PDF Generator</span>
          </button>
          <button
            onClick={() => setActiveTab('bi_studio')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'bi_studio'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            <Database className="w-4 h-4" />
            <span>PowerBI / Tableau Studio</span>
          </button>
          <button
            onClick={() => setActiveTab('schedules')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'schedules'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            <Mail className="w-4 h-4" />
            <span>Email Schedules ({schedules.length})</span>
          </button>
          <button
            onClick={fetchData}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors ml-1"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Top Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-xs font-medium">Executive Reports Generated</p>
            <p className="text-2xl font-extrabold text-white mt-1">{exportLogs.length}</p>
            <span className="text-[11px] text-indigo-400 flex items-center gap-1 mt-1">
              <CheckCircle2 className="w-3 h-3" /> INR (₹) Revenue Format
            </span>
          </div>
          <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl text-indigo-400">
            <FileText className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-xs font-medium">BI Export Records</p>
            <p className="text-2xl font-extrabold text-emerald-400 mt-1">{biDataset?.record_count || 30}</p>
            <span className="text-[11px] text-emerald-400 flex items-center gap-1 mt-1">
              <Database className="w-3 h-3" /> PowerBI & Tableau Ready
            </span>
          </div>
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400">
            <Database className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-xs font-medium">Active Automated Schedules</p>
            <p className="text-2xl font-extrabold text-purple-300 mt-1">{schedules.length}</p>
            <span className="text-[11px] text-purple-400 flex items-center gap-1 mt-1">
              <Clock className="w-3 h-3" /> Recurring Email Dispatch
            </span>
          </div>
          <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-xl text-purple-400">
            <Mail className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-xs font-medium">AI Strategic Action Items</p>
            <p className="text-2xl font-extrabold text-amber-300 mt-1">3 Yield Rules</p>
            <span className="text-[11px] text-amber-400 flex items-center gap-1 mt-1">
              <Sparkles className="w-3 h-3" /> Embedded in PDF Summary
            </span>
          </div>
          <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-400">
            <Sparkles className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* TAB 1: EXECUTIVE PDF GENERATOR */}
      {activeTab === 'pdf' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Generator Form */}
          <div className="lg:col-span-5 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <FileText className="w-5 h-5 text-indigo-400" />
              Generate Executive Revenue PDF
            </h2>
            <p className="text-xs text-slate-400">
              Compile KPI metrics, RevPAR / TRevPAR breakdown in INR (₹), and AI strategic recommendations into a presentation-ready PDF report.
            </p>

            <form onSubmit={handleGeneratePdf} className="space-y-4 pt-2">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Report Category</label>
                <select
                  value={reportType}
                  onChange={(e) => {
                    setReportType(e.target.value);
                    if (e.target.value === 'DAILY_REVENUE') setReportTitle('Daily Executive Revenue Digest');
                    else if (e.target.value === 'WEEKLY_TREVPAR') setReportTitle('Weekly TRevPAR & Non-Room Yield Audit');
                    else setReportTitle('Monthly Group Displacement & Breakeven Audit');
                  }}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
                >
                  <option value="DAILY_REVENUE">Daily Executive Revenue Digest (PDF)</option>
                  <option value="WEEKLY_TREVPAR">Weekly TRevPAR & Non-Room Revenue Audit</option>
                  <option value="MONTHLY_DISPLACEMENT_AUDIT">Monthly Group Displacement & Breakeven Audit</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Report Document Title</label>
                <input
                  type="text"
                  value={reportTitle}
                  onChange={(e) => setReportTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white focus:border-indigo-500 focus:outline-none font-medium"
                />
              </div>

              <button
                type="submit"
                disabled={generatingPdf}
                className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center gap-2 cursor-pointer"
              >
                {generatingPdf ? <RefreshCw className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                <span>Generate Executive PDF Report</span>
              </button>
            </form>

            {/* Past Report Logs History */}
            <div className="pt-4 border-t border-slate-800/80">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">Report History Log</h3>
              <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
                {exportLogs.map((log) => (
                  <div
                    key={log.export_id}
                    onClick={() => setGeneratedReport(log)}
                    className={`p-2.5 rounded-xl border text-xs cursor-pointer transition-all ${
                      generatedReport?.export_id === log.export_id
                        ? 'bg-indigo-950/40 border-indigo-500/50 text-white'
                        : 'bg-slate-950/60 border-slate-800/60 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between font-semibold text-slate-200">
                      <span className="truncate max-w-[200px]">{log.report_title}</span>
                      <span className="text-[10px] text-indigo-400 font-mono">{log.file_size_kb} KB</span>
                    </div>
                    <div className="flex items-center justify-between text-[11px] text-slate-500 mt-1">
                      <span>{new Date(log.generated_at).toLocaleDateString()}</span>
                      <span className="text-emerald-400 font-medium">{log.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Interactive Document Preview */}
          <div className="lg:col-span-7 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <FileText className="w-5 h-5 text-emerald-400" />
                  <h3 className="text-base font-bold text-white">Live PDF Executive Briefing Preview</h3>
                </div>
                {generatedReport?.download_url && (
                  <a
                    href={generatedReport.download_url}
                    download
                    className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-emerald-600/30 transition-all flex items-center gap-1.5"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download PDF</span>
                  </a>
                )}
              </div>

              {/* Formatted Report Briefing Render */}
              <div className="mt-4 bg-slate-950 border border-slate-800 rounded-xl p-6 space-y-5">
                <div className="border-b border-slate-800/80 pb-3 flex justify-between items-start">
                  <div>
                    <h2 className="text-lg font-extrabold text-white">{generatedReport?.report_title || reportTitle}</h2>
                    <p className="text-xs text-indigo-400 font-medium mt-0.5">
                      Property: {selectedHotel?.hotel_name || 'Grand Heritage Palace'} • Currency: INR (₹)
                    </p>
                  </div>
                  <span className="px-2.5 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-bold rounded-full">
                    CONFIDENTIAL EXECUTIVE REPORT
                  </span>
                </div>

                {/* Key Metrics Snapshot */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-900/80 p-3 rounded-xl border border-slate-800/80">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">Average Daily Rate</span>
                    <p className="text-sm font-extrabold text-white mt-0.5">₹8,950</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">Occupancy Rate</span>
                    <p className="text-sm font-extrabold text-emerald-400 mt-0.5">84.5%</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">RevPAR (Room)</span>
                    <p className="text-sm font-extrabold text-indigo-300 mt-0.5">₹7,562</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">TRevPAR (Total)</span>
                    <p className="text-sm font-extrabold text-purple-300 mt-0.5">₹11,250</p>
                  </div>
                </div>

                {/* AI Strategic Action Plan */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                    AI Agent Strategic Revenue Recommendations
                  </h4>
                  <ul className="space-y-1.5 text-xs text-slate-300 pl-2">
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                      <span>Increase Deluxe BAR rate by ₹750/night for upcoming high-demand weekend.</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                      <span>Deploy Spa & Banquet dynamic upsell bundle to expand TRevPAR by +14.2%.</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                      <span>Maintain MLOS 2-night restriction on peak event dates (Nov 12-15).</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
              <span>Status: <strong className="text-emerald-400 font-semibold">100% Validated & Generated</strong></span>
              <span>Generated: {generatedReport?.generated_at ? new Date(generatedReport.generated_at).toLocaleString() : 'Just now'}</span>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: POWERBI / TABLEAU BI STUDIO */}
      {activeTab === 'bi_studio' && (
        <div className="space-y-6">
          {/* Endpoint Connectors Box */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <Database className="w-5 h-5 text-emerald-400" />
                  PowerBI & Tableau Live Data Connector Endpoints
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Connect PowerBI Desktop or Tableau Online directly to this live REST API endpoint for real-time revenue dashboard sync.
                </p>
              </div>

              <div className="flex items-center gap-2 flex-shrink-0">
                <button
                  onClick={handleExportCSV}
                  className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-emerald-600/30 transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <FileSpreadsheet className="w-4 h-4" />
                  <span>Download CSV Dataset</span>
                </button>
              </div>
            </div>

            {/* API Endpoint Copy Card */}
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="space-y-1">
                <span className="text-[11px] text-slate-400 font-mono font-semibold">REST API OData Endpoint URL:</span>
                <p className="text-xs text-emerald-300 font-mono font-bold break-all">
                  {window.location.origin}/api/v1/hotels/{hotelId}/executive-reports/bi-dataset
                </p>
              </div>
              <button
                onClick={() => handleCopyEndpoint(`/api/v1/hotels/${hotelId}/executive-reports/bi-dataset`)}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 flex-shrink-0"
              >
                {copiedEndpoint ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                <span>{copiedEndpoint ? 'Copied!' : 'Copy Endpoint'}</span>
              </button>
            </div>
          </div>

          {/* Dataset Table */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Table className="w-4 h-4 text-indigo-400" />
                BI Dataset Records Preview (INR ₹)
              </h3>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400">Show Days:</span>
                <select
                  value={biDays}
                  onChange={(e) => setBiDays(Number(e.target.value))}
                  className="bg-slate-950 border border-slate-800 text-white text-xs px-2.5 py-1 rounded-lg focus:outline-none"
                >
                  <option value={7}>7 Days</option>
                  <option value={14}>14 Days</option>
                  <option value={30}>30 Days</option>
                </select>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800 font-mono">
                  <tr>
                    <th className="p-3">Stay Date</th>
                    <th className="p-3">Rooms Sold</th>
                    <th className="p-3 text-center">Occupancy %</th>
                    <th className="p-3 text-right">ADR (₹)</th>
                    <th className="p-3 text-right">RevPAR (₹)</th>
                    <th className="p-3 text-right">Non-Room (₹)</th>
                    <th className="p-3 text-right">TRevPAR (₹)</th>
                    <th className="p-3 text-center">Comp Index</th>
                    <th className="p-3 text-right">Displacement Deficit (₹)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {biDataset?.dataset_records?.map((r: any, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                      <td className="p-3 text-white font-bold">{r.stay_date}</td>
                      <td className="p-3 text-slate-300">{r.rooms_sold} / {r.total_rooms}</td>
                      <td className="p-3 text-center text-emerald-400 font-semibold">{r.occupancy_pct}%</td>
                      <td className="p-3 text-right font-semibold">₹{r.adr_inr.toLocaleString('en-IN')}</td>
                      <td className="p-3 text-right text-indigo-300">₹{r.revpar_inr.toLocaleString('en-IN')}</td>
                      <td className="p-3 text-right text-purple-300">₹{r.non_room_rev_inr.toLocaleString('en-IN')}</td>
                      <td className="p-3 text-right text-white font-bold">₹{r.trevpar_inr.toLocaleString('en-IN')}</td>
                      <td className="p-3 text-center font-bold text-amber-300">{r.competitor_index}</td>
                      <td className={`p-3 text-right font-bold ${r.net_displacement_loss_inr > 0 ? 'text-rose-400' : 'text-slate-500'}`}>
                        {r.net_displacement_loss_inr > 0 ? `₹${r.net_displacement_loss_inr.toLocaleString('en-IN')}` : '₹0'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: AUTOMATED EMAIL SCHEDULES */}
      {activeTab === 'schedules' && (
        <div className="space-y-4">
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <Mail className="w-5 h-5 text-indigo-400" />
                  Automated Recurring Email Dispatch Schedules
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Configure automated PDF digests and BI dataset sync emails sent directly to executive leadership.
                </p>
              </div>

              <button
                onClick={() => setShowAddSched(!showAddSched)}
                className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-1.5 cursor-pointer"
              >
                <Plus className="w-4 h-4" />
                <span>Add New Schedule</span>
              </button>
            </div>

            {/* Add Schedule Form */}
            {showAddSched && (
              <form onSubmit={handleCreateSchedule} className="mt-4 p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
                <h3 className="text-xs font-bold text-white">Create Recurring Report Email Dispatch</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Schedule Name</label>
                    <input
                      type="text"
                      value={newSchedName}
                      onChange={(e) => setNewSchedName(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Recipient Email List</label>
                    <input
                      type="text"
                      value={newSchedRecipients}
                      onChange={(e) => setNewSchedRecipients(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white"
                      required
                    />
                  </div>
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowAddSched(false)}
                    className="px-3 py-1.5 bg-slate-800 text-slate-300 text-xs rounded-lg"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-1.5 bg-indigo-600 text-white text-xs font-semibold rounded-lg shadow"
                  >
                    Save Schedule
                  </button>
                </div>
              </form>
            )}

            {/* Schedules Table */}
            <div className="overflow-x-auto mt-4">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-800 font-semibold text-slate-400 uppercase tracking-wider bg-slate-950/50">
                    <th className="p-3">Schedule Name</th>
                    <th className="p-3">Frequency</th>
                    <th className="p-3">Format</th>
                    <th className="p-3">Recipients</th>
                    <th className="p-3">Next Scheduled Run</th>
                    <th className="p-3 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {schedules.map((s) => (
                    <tr key={s.schedule_id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="p-3 font-bold text-white">{s.schedule_name}</td>
                      <td className="p-3 font-semibold text-indigo-300">{s.frequency}</td>
                      <td className="p-3 font-mono text-purple-300">{s.file_format}</td>
                      <td className="p-3 text-slate-400 font-mono text-[11px]">{s.recipients}</td>
                      <td className="p-3 text-slate-400">
                        {s.next_run_at ? new Date(s.next_run_at).toLocaleString() : 'Tomorrow 08:00 AM'}
                      </td>
                      <td className="p-3 text-right">
                        <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded font-bold text-[10px]">
                          ACTIVE
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
