import React, { useState, useEffect } from 'react';
import { useHotel } from '../context/HotelContext';
import { apiService } from '../services/api';
import {
  Globe,
  RefreshCw,
  Send,
  CheckCircle2,
  AlertCircle,
  Database,
  ShieldCheck,
  Zap,
  DollarSign,
  ArrowDownLeft,
  ArrowUpRight,
  Clock,
  Layers,
  Settings2,
  TrendingUp,
  Server,
  Activity,
  Plus,
  Edit2,
  Trash2,
  X,
  Check,
} from 'lucide-react';

export const OTAChannelManager: React.FC = () => {
  const { selectedHotel } = useHotel();
  const hotelId = selectedHotel?.hotel_id || (selectedHotel as any)?.id || 1;

  const [activeTab, setActiveTab] = useState<'channels' | 'push' | 'logs'>('channels');
  const [loading, setLoading] = useState<boolean>(true);
  const [pmsConnector, setPmsConnector] = useState<any>(null);
  const [otaChannels, setOtaChannels] = useState<any[]>([]);
  const [syncLogs, setSyncLogs] = useState<any[]>([]);

  // Push form state
  const [selectedRoomType, setSelectedRoomType] = useState<string>('Deluxe Ocean Suite');
  const [pushRateINR, setPushRateINR] = useState<number>(9800);
  const [pushReason, setPushReason] = useState<string>('AI Dynamic Weekend Demand Surge');
  const [isPushing, setIsPushing] = useState<boolean>(false);

  // Pull state
  const [isPulling, setIsPulling] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  // Add Channel Modal state
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [addChannelName, setAddChannelName] = useState<string>('');
  const [addChannelCode, setAddChannelCode] = useState<string>('');
  const [addCommissionPct, setAddCommissionPct] = useState<number>(15.0);

  // Edit Channel Modal state
  const [editingChannel, setEditingChannel] = useState<any | null>(null);
  const [editChannelName, setEditChannelName] = useState<string>('');
  const [editCommissionPct, setEditCommissionPct] = useState<number>(18.0);
  const [editStatus, setEditStatus] = useState<string>('ACTIVE');
  const [editParity, setEditParity] = useState<string>('PARITY_OK');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [pmsRes, otaRes, logsRes] = await Promise.all([
        apiService.getPMSConnector(hotelId),
        apiService.getOTAChannels(hotelId),
        apiService.getSyncLogs(hotelId, 30),
      ]);
      setPmsConnector(pmsRes);
      setOtaChannels(otaRes || []);
      setSyncLogs(logsRes || []);
    } catch (err) {
      console.error('Failed to load OTA & PMS connector data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [hotelId]);

  const showNotification = (text: string, type: 'success' | 'error') => {
    setToastMessage({ text, type });
    setTimeout(() => setToastMessage(null), 4000);
  };

  const handlePushRates = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pushRateINR <= 0) return;
    setIsPushing(true);
    try {
      const res = await apiService.pushTwoWayRates(hotelId, {
        room_type: selectedRoomType,
        recommended_rate_inr: pushRateINR,
        override_reason: pushReason,
      });
      showNotification(`Successfully pushed ₹${pushRateINR.toLocaleString('en-IN')} to PMS & ${res.target_channels.length} OTAs (${res.execution_time_ms}ms)`, 'success');
      fetchData();
    } catch (err) {
      showNotification('Failed to push rates to channels', 'error');
    } finally {
      setIsPushing(false);
    }
  };

  const handlePullReservations = async () => {
    setIsPulling(true);
    try {
      const res = await apiService.pullPMSReservations(hotelId);
      showNotification(`Pulled ${res.new_reservations_count} new reservations from Opera Cloud PMS (Revenue: ₹${res.total_revenue_inr.toLocaleString('en-IN')})`, 'success');
      fetchData();
    } catch (err) {
      showNotification('Failed to pull reservations from PMS', 'error');
    } finally {
      setIsPulling(false);
    }
  };

  const handleCreateChannel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!addChannelName.trim() || !addChannelCode.trim()) return;
    try {
      await apiService.createOTAChannel(hotelId, {
        channel_name: addChannelName,
        channel_code: addChannelCode.toUpperCase(),
        commission_pct: addCommissionPct,
      });
      showNotification(`Added new OTA channel: ${addChannelName}`, 'success');
      setShowAddModal(false);
      setAddChannelName('');
      setAddChannelCode('');
      setAddCommissionPct(15.0);
      fetchData();
    } catch (err) {
      showNotification('Failed to create OTA channel', 'error');
    }
  };

  const openEditModal = (ch: any) => {
    setEditingChannel(ch);
    setEditChannelName(ch.channel_name);
    setEditCommissionPct(ch.commission_pct);
    setEditStatus(ch.connection_status);
    setEditParity(ch.rate_parity_status);
  };

  const handleUpdateChannel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingChannel) return;
    try {
      await apiService.updateOTAChannel(hotelId, editingChannel.id, {
        channel_name: editChannelName,
        commission_pct: editCommissionPct,
        connection_status: editStatus,
        rate_parity_status: editParity,
      });
      showNotification(`Updated ${editChannelName} (Commission set to ${editCommissionPct}%)`, 'success');
      setEditingChannel(null);
      fetchData();
    } catch (err) {
      showNotification('Failed to update OTA channel', 'error');
    }
  };

  const handleDeleteChannel = async (ch: any) => {
    if (!window.confirm(`Are you sure you want to disconnect & delete channel "${ch.channel_name}"?`)) return;
    try {
      await apiService.deleteOTAChannel(hotelId, ch.id);
      showNotification(`Deleted channel ${ch.channel_name}`, 'success');
      fetchData();
    } catch (err) {
      showNotification('Failed to delete channel', 'error');
    }
  };

  const uniqueChannels = Array.from(new Map(otaChannels.map((c) => [c.channel_code, c])).values());

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 text-slate-100">
      {/* Toast alert */}
      {toastMessage && (
        <div
          className={`fixed top-5 right-5 z-50 px-4 py-3 rounded-xl shadow-xl flex items-center space-x-3 text-sm font-medium border ${
            toastMessage.type === 'success'
              ? 'bg-emerald-950/90 text-emerald-200 border-emerald-500/50'
              : 'bg-rose-950/90 text-rose-200 border-rose-500/50'
          }`}
        >
          {toastMessage.type === 'success' ? <CheckCircle2 className="w-5 h-5 text-emerald-400" /> : <AlertCircle className="w-5 h-5 text-rose-400" />}
          <span>{toastMessage.text}</span>
        </div>
      )}

      {/* Header title */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl shadow-2xl">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-gradient-to-tr from-sky-600 to-indigo-600 rounded-xl shadow-lg shadow-sky-500/20 shrink-0">
            <Globe className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">OTA Channel Manager & PMS 2-Way Sync</h1>
            <p className="text-slate-400 text-sm mt-1">
              Synchronize live rate recommendations directly to Opera Cloud PMS, STAAH, Booking.com, MakeMyTrip, and Expedia.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 shrink-0">
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center justify-center space-x-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition shadow-lg shadow-emerald-600/20 whitespace-nowrap"
          >
            <Plus className="w-4 h-4 shrink-0" />
            <span>Add OTA Channel</span>
          </button>

          <button
            onClick={handlePullReservations}
            disabled={isPulling}
            className="flex items-center justify-center space-x-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-bold transition border border-slate-700 whitespace-nowrap"
          >
            <ArrowDownLeft className={`w-4 h-4 text-emerald-400 shrink-0 ${isPulling ? 'animate-spin' : ''}`} />
            <span>{isPulling ? 'Pulling Bookings...' : 'Pull PMS Bookings'}</span>
          </button>

          <button
            onClick={() => setActiveTab('push')}
            className="flex items-center justify-center space-x-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition shadow-lg shadow-indigo-600/30 whitespace-nowrap"
          >
            <ArrowUpRight className="w-4 h-4 shrink-0" />
            <span>2-Way Rate Push</span>
          </button>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800 flex items-center space-x-4">
          <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-400">
            <Server className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">PMS Connector Link</div>
            <div className="text-lg font-bold text-white mt-0.5">
              {pmsConnector?.pms_provider || 'OPERA CLOUD'}
            </div>
            <div className="text-[11px] text-emerald-400 font-semibold mt-0.5">● Connected (5 min auto-sync)</div>
          </div>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800 flex items-center space-x-4">
          <div className="p-3 rounded-lg bg-sky-500/10 text-sky-400">
            <Globe className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Connected OTA Channels</div>
            <div className="text-2xl font-bold text-white mt-0.5">{uniqueChannels.length} Channels</div>
            <div className="text-[11px] text-slate-400 mt-0.5">MMT, Booking.com, Agoda, Expedia, etc.</div>
          </div>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800 flex items-center space-x-4">
          <div className="p-3 rounded-lg bg-violet-500/10 text-violet-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Rate Parity Status</div>
            <div className="text-2xl font-bold text-emerald-400 mt-0.5">100% Compliant</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Zero parity breaches detected</div>
          </div>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800 flex items-center space-x-4">
          <div className="p-3 rounded-lg bg-amber-500/10 text-amber-400">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">2-Way Sync Latency</div>
            <div className="text-2xl font-bold text-white mt-0.5">58.4 ms</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Real-time WebSocket/REST push</div>
          </div>
        </div>
      </div>

      {/* Tabs Header */}
      <div className="flex border-b border-slate-800 space-x-8">
        <button
          onClick={() => setActiveTab('channels')}
          className={`pb-3 flex items-center space-x-2 text-sm font-semibold border-b-2 transition ${
            activeTab === 'channels'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Globe className="w-4 h-4" />
          <span>OTA Channel Matrix ({uniqueChannels.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('push')}
          className={`pb-3 flex items-center space-x-2 text-sm font-semibold border-b-2 transition ${
            activeTab === 'push'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Send className="w-4 h-4" />
          <span>2-Way Rate Push Simulator</span>
        </button>

        <button
          onClick={() => setActiveTab('logs')}
          className={`pb-3 flex items-center space-x-2 text-sm font-semibold border-b-2 transition ${
            activeTab === 'logs'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Clock className="w-4 h-4" />
          <span>Sync Audit Logs ({syncLogs.length})</span>
        </button>
      </div>

      {/* TAB 1: OTA CHANNELS */}
      {activeTab === 'channels' && (
        <div className="bg-slate-900/60 rounded-2xl border border-slate-800 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">Live Channel Mapping & Parity Matrix</h3>
              <p className="text-xs text-slate-400">
                Connected OTA distribution channels with real-time rate parity checks and editable commission structures.
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowAddModal(true)}
                className="flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 rounded-lg text-xs font-semibold transition"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Channel</span>
              </button>
              <button onClick={fetchData} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition">
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>

          {loading ? (
            <div className="py-12 text-center text-slate-400 text-sm animate-pulse">Loading channel mappings...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {uniqueChannels.map((ch) => (
                <div key={ch.channel_code} className="bg-slate-950/80 p-5 rounded-xl border border-slate-800 space-y-3 relative group">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="px-2.5 py-1 bg-indigo-950 text-indigo-300 font-mono text-xs font-bold rounded border border-indigo-800">
                        {ch.channel_code}
                      </div>
                      <div>
                        <div className="font-semibold text-white text-sm">{ch.channel_name}</div>
                        <div className="text-xs text-emerald-400 font-medium">{ch.commission_pct}% Commission</div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-1">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                        ch.connection_status === 'ACTIVE'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                      }`}>
                        {ch.connection_status}
                      </span>
                      <button
                        onClick={() => openEditModal(ch)}
                        title="Edit Commission & Details"
                        className="p-1 text-slate-400 hover:text-indigo-300 hover:bg-slate-800 rounded transition"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDeleteChannel(ch)}
                        title="Delete Channel"
                        className="p-1 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded transition"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-800/60 space-y-2 text-xs">
                    <div className="flex justify-between items-center text-slate-300">
                      <span className="text-slate-400">Last Pushed Rate (₹):</span>
                      <span className="font-semibold text-emerald-400 font-mono text-sm">
                        ₹{ch.last_pushed_rate_inr?.toLocaleString('en-IN')}
                      </span>
                    </div>

                    <div className="flex justify-between items-center text-slate-300">
                      <span className="text-slate-400">Rate Parity Status:</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-800">
                        {ch.rate_parity_status}
                      </span>
                    </div>

                    <div className="flex justify-between items-center text-slate-400 pt-1 text-[11px]">
                      <span>Mapped Room Types:</span>
                      <span>{ch.mapped_room_count} Room Categories</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: 2-WAY RATE PUSH */}
      {activeTab === 'push' && (
        <div className="bg-slate-900/60 rounded-2xl border border-slate-800 p-6 space-y-5">
          <div>
            <h3 className="text-lg font-semibold text-white">2-Way Rate Dispatch & Push Engine</h3>
            <p className="text-xs text-slate-400">
              Transmit AI-calculated rate recommendations to Opera Cloud PMS and push synchronized ARI (Availability, Rates & Inventory) to all OTAs.
            </p>
          </div>

          <form onSubmit={handlePushRates} className="max-w-2xl space-y-4 bg-slate-950/80 p-5 rounded-xl border border-slate-800">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Target Room Type</label>
              <select
                value={selectedRoomType}
                onChange={(e) => setSelectedRoomType(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
              >
                <option value="Deluxe Ocean Suite">Deluxe Ocean Suite</option>
                <option value="Executive Suite">Executive Suite</option>
                <option value="Superior King Room">Superior King Room</option>
                <option value="Standard Twin Room">Standard Twin Room</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Recommended Room Rate (₹ INR)</label>
              <div className="relative">
                <span className="absolute left-3 top-2.5 text-slate-400 text-sm font-semibold">₹</span>
                <input
                  type="number"
                  required
                  min={1000}
                  step={100}
                  value={pushRateINR}
                  onChange={(e) => setPushRateINR(Number(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 pl-8 text-sm text-white font-mono font-semibold focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Override / Push Strategy Notes</label>
              <input
                type="text"
                value={pushReason}
                onChange={(e) => setPushReason(e.target.value)}
                placeholder="e.g. AI Dynamic Weekend Surge"
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={isPushing}
                className="flex items-center justify-center space-x-2 w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-semibold transition shadow-lg shadow-indigo-600/30"
              >
                <Send className={`w-4 h-4 ${isPushing ? 'animate-bounce' : ''}`} />
                <span>{isPushing ? 'Transmitting to PMS & OTAs...' : 'Transmit 2-Way Rate Update'}</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* TAB 3: AUDIT LOGS */}
      {activeTab === 'logs' && (
        <div className="bg-slate-900/60 rounded-2xl border border-slate-800 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">2-Way Synchronization Audit Logs</h3>
              <p className="text-xs text-slate-400">
                Log history of outgoing rate updates and incoming PMS reservation pulls.
              </p>
            </div>
            <button onClick={fetchData} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          {loading ? (
            <div className="py-12 text-center text-slate-400 text-sm animate-pulse">Loading sync logs...</div>
          ) : syncLogs.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-sm">No 2-way sync logs recorded yet.</div>
          ) : (
            <div className="space-y-3">
              {syncLogs.map((log) => (
                <div key={log.id} className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-3">
                    <span className="px-2.5 py-1 bg-sky-950 text-sky-300 font-mono font-semibold rounded border border-sky-800">
                      {log.sync_type}
                    </span>
                    <div>
                      <div className="font-semibold text-white text-sm">{log.target_channel}</div>
                      <div className="text-slate-400 text-[11px]">
                        Processed: {log.records_processed} items • Latency: {log.execution_time_ms} ms
                      </div>
                    </div>
                  </div>

                  <div className="text-right space-y-1">
                    <span className="px-2.5 py-0.5 rounded-full font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                      {log.status}
                    </span>
                    <div className="text-slate-500 text-[11px]">
                      {new Date(log.synced_at).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ADD CHANNEL MODAL */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 rounded-2xl border border-slate-800 max-w-md w-full p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                <Globe className="w-5 h-5 text-emerald-400" />
                <span>Add OTA Distribution Channel</span>
              </h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateChannel} className="space-y-4 text-sm">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">OTA Channel Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. TripAdvisor, Hostelworld, EaseMyTrip"
                  value={addChannelName}
                  onChange={(e) => setAddChannelName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Channel Code (2-4 Uppercase Chars)</label>
                <input
                  type="text"
                  required
                  maxLength={5}
                  placeholder="e.g. TA, HW, EMT"
                  value={addChannelCode}
                  onChange={(e) => setAddChannelCode(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white font-mono uppercase focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Commission Percentage (%)</label>
                <input
                  type="number"
                  required
                  step={0.5}
                  min={0}
                  max={50}
                  value={addCommissionPct}
                  onChange={(e) => setAddCommissionPct(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white font-mono focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-xs font-medium hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold transition"
                >
                  Save New Channel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* EDIT CHANNEL MODAL */}
      {editingChannel && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 rounded-2xl border border-slate-800 max-w-md w-full p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                <Edit2 className="w-5 h-5 text-indigo-400" />
                <span>Edit OTA Channel & Commission</span>
              </h3>
              <button onClick={() => setEditingChannel(null)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpdateChannel} className="space-y-4 text-sm">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Channel Name</label>
                <input
                  type="text"
                  required
                  value={editChannelName}
                  onChange={(e) => setEditChannelName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Commission Percentage (%)</label>
                <input
                  type="number"
                  required
                  step={0.1}
                  min={0}
                  max={50}
                  value={editCommissionPct}
                  onChange={(e) => setEditCommissionPct(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white font-mono font-bold text-indigo-300 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Connection Status</label>
                <select
                  value={editStatus}
                  onChange={(e) => setEditStatus(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="PAUSED">PAUSED</option>
                  <option value="ERROR">ERROR</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Rate Parity State</label>
                <select
                  value={editParity}
                  onChange={(e) => setEditParity(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="PARITY_OK">PARITY_OK</option>
                  <option value="UNDERCUT_DETECTED">UNDERCUT_DETECTED</option>
                  <option value="BREACH_WARNING">BREACH_WARNING</option>
                </select>
              </div>

              <div className="flex justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setEditingChannel(null)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-xs font-medium hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition shadow-lg shadow-indigo-600/30"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
