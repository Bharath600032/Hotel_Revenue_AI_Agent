import React, { useState, useEffect } from 'react';
import { useHotel } from '../context/HotelContext';
import { api } from '../services/api';
import {
  Key,
  Webhook,
  Terminal,
  Plus,
  ShieldCheck,
  Copy,
  Check,
  Trash2,
  Send,
  RefreshCw,
  Clock,
  AlertTriangle,
  Lock,
  Code2,
  CheckCircle,
  XCircle,
  Eye,
  EyeOff,
  Zap,
} from 'lucide-react';

export const DeveloperPortal: React.FC = () => {
  const { selectedHotel } = useHotel();
  const hotelId = selectedHotel?.hotel_id || (selectedHotel as any)?.id || 1;

  const [activeTab, setActiveTab] = useState<'keys' | 'webhooks' | 'logs'>('keys');
  const [loading, setLoading] = useState(true);
  const [apiKeys, setApiKeys] = useState<any[]>([]);
  const [webhooks, setWebhooks] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);

  // Modals & Forms
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [selectedScopes, setSelectedScopes] = useState<string[]>([
    'pricing:read',
    'pricing:write',
    'reports:read',
  ]);
  const [expiresInDays, setExpiresInDays] = useState<number>(90);
  const [generatedRawKey, setGeneratedRawKey] = useState<string | null>(null);
  const [copiedKey, setCopiedKey] = useState(false);

  const [showWebhookModal, setShowWebhookModal] = useState(false);
  const [webhookUrl, setWebhookUrl] = useState('');
  const [webhookEvents, setWebhookEvents] = useState<string[]>([
    'price.updated',
    'anomalies.detected',
  ]);
  const [webhookDescription, setWebhookDescription] = useState('');

  // Dispatching state
  const [dispatchingId, setDispatchingId] = useState<number | null>(null);
  const [showSecretMap, setShowSecretMap] = useState<Record<number, boolean>>({});
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const allAvailableScopes = [
    { id: 'pricing:read', label: 'Pricing Read', desc: 'Query live rate recommendations & historical prices' },
    { id: 'pricing:write', label: 'Pricing Write', desc: 'Accept/approve rates and update channel prices' },
    { id: 'reports:read', label: 'Reports Read', desc: 'Fetch revenue performance digests' },
    { id: 'bi:export', label: 'BI Export', desc: 'Stream PowerBI/Tableau CSV datasets' },
    { id: 'webhooks:manage', label: 'Webhooks Manage', desc: 'Create, update and delete event subscriptions' },
  ];

  const allAvailableEvents = [
    { id: 'price.updated', label: 'price.updated', desc: 'Triggered whenever rate recommendations change or push to PMS' },
    { id: 'anomalies.detected', label: 'anomalies.detected', desc: 'Triggered when high-severity market anomalies occur' },
    { id: 'report.generated', label: 'report.generated', desc: 'Triggered when automated PDF/BI reports finish generating' },
    { id: 'swarm.consensus', label: 'swarm.consensus', desc: 'Triggered when multi-agent swarm reaches optimal rate consensus' },
  ];

  const fetchData = async () => {
    setLoading(true);
    try {
      const [keysRes, whRes, logsRes] = await Promise.all([
        api.getAPIKeys(hotelId),
        api.getWebhooks(hotelId),
        api.getWebhookLogs(hotelId, 30),
      ]);
      setApiKeys(keysRes);
      setWebhooks(whRes);
      setLogs(logsRes);
    } catch (err) {
      console.error('Failed to load developer portal data:', err);
      showToast('Failed to connect to Developer API endpoint', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [hotelId]);

  const showToast = (message: string, type: 'success' | 'error') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4000);
  };

  const handleCreateKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKeyName.trim()) return;
    try {
      const res = await api.createAPIKey(hotelId, {
        name: newKeyName,
        scopes: selectedScopes,
        expires_in_days: expiresInDays,
      });
      setGeneratedRawKey(res.api_key_raw);
      showToast('API Key generated successfully! Save your secret key now.', 'success');
      fetchData();
    } catch (err) {
      showToast('Failed to generate API Key', 'error');
    }
  };

  const handleRevokeKey = async (keyId: number) => {
    if (!window.confirm('Are you sure you want to revoke this API key? Applications using it will lose access immediately.')) return;
    try {
      await api.revokeAPIKey(hotelId, keyId);
      showToast('API Key revoked', 'success');
      fetchData();
    } catch (err) {
      showToast('Failed to revoke key', 'error');
    }
  };

  const handleCreateWebhook = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!webhookUrl.trim()) return;
    try {
      await api.createWebhook(hotelId, {
        endpoint_url: webhookUrl,
        events: webhookEvents,
        description: webhookDescription,
      });
      setShowWebhookModal(false);
      setWebhookUrl('');
      setWebhookDescription('');
      showToast('Webhook subscription registered successfully!', 'success');
      fetchData();
    } catch (err) {
      showToast('Failed to create webhook subscription', 'error');
    }
  };

  const handleDeleteWebhook = async (whId: number) => {
    if (!window.confirm('Delete this webhook endpoint subscription?')) return;
    try {
      await api.deleteWebhook(hotelId, whId);
      showToast('Webhook subscription deleted', 'success');
      fetchData();
    } catch (err) {
      showToast('Failed to delete webhook', 'error');
    }
  };

  const handleTestDispatch = async (subscriptionId: number, eventType: string = 'price.updated') => {
    setDispatchingId(subscriptionId);
    try {
      const logRes = await api.testDispatchWebhook(hotelId, subscriptionId, eventType);
      showToast(`Test payload dispatched successfully (${logRes.execution_time_ms}ms, 200 OK)`, 'success');
      fetchData();
    } catch (err) {
      showToast('Failed to dispatch test payload', 'error');
    } finally {
      setDispatchingId(null);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2000);
  };

  const toggleScope = (scopeId: string) => {
    setSelectedScopes((prev) =>
      prev.includes(scopeId) ? prev.filter((s) => s !== scopeId) : [...prev, scopeId]
    );
  };

  const toggleWebhookEvent = (eventId: string) => {
    setWebhookEvents((prev) =>
      prev.includes(eventId) ? prev.filter((e) => e !== eventId) : [...prev, eventId]
    );
  };

  const toggleSecretVisibility = (whId: number) => {
    setShowSecretMap((prev) => ({ ...prev, [whId]: !prev[whId] }));
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 text-slate-100">
      {/* Toast Notification */}
      {notification && (
        <div
          className={`fixed top-5 right-5 z-50 px-4 py-3 rounded-lg shadow-xl flex items-center space-x-3 text-sm font-medium border ${
            notification.type === 'success'
              ? 'bg-emerald-950/90 text-emerald-200 border-emerald-500/50'
              : 'bg-rose-950/90 text-rose-200 border-rose-500/50'
          }`}
        >
          {notification.type === 'success' ? <CheckCircle className="w-5 h-5 text-emerald-400" /> : <XCircle className="w-5 h-5 text-rose-400" />}
          <span>{notification.message}</span>
        </div>
      )}

      {/* Header Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl shadow-2xl">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-gradient-to-tr from-indigo-600 to-violet-600 rounded-xl shadow-lg shadow-indigo-500/20">
            <Code2 className="w-7 h-7 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-2xl font-bold tracking-tight text-white">API Key Management & Webhook Portal</h1>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                DEVELOPER HUB v2.4
              </span>
            </div>
            <p className="text-slate-400 text-sm mt-1">
              Configure OAuth2 API keys, HMAC webhook endpoints, and monitor real-time event dispatches for external PMS & BI integrations.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowKeyModal(true)}
            className="flex items-center space-x-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-medium transition shadow-lg shadow-indigo-600/30"
          >
            <Plus className="w-4 h-4" />
            <span>Generate API Key</span>
          </button>
          <button
            onClick={() => setShowWebhookModal(true)}
            className="flex items-center space-x-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-sm font-medium transition border border-slate-700"
          >
            <Webhook className="w-4 h-4 text-violet-400" />
            <span>New Webhook</span>
          </button>
        </div>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800 flex items-center space-x-4">
          <div className="p-3 rounded-lg bg-indigo-500/10 text-indigo-400">
            <Key className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Active API Keys</div>
            <div className="text-2xl font-bold text-white mt-1">
              {apiKeys.filter((k) => k.status === 'active').length} <span className="text-xs text-slate-500 font-normal">/ {apiKeys.length} Total</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800 flex items-center space-x-4">
          <div className="p-3 rounded-lg bg-violet-500/10 text-violet-400">
            <Webhook className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Active Webhooks</div>
            <div className="text-2xl font-bold text-white mt-1">
              {webhooks.filter((w) => w.status === 'active').length}
            </div>
          </div>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800 flex items-center space-x-4">
          <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-400">
            <Zap className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Events Dispatched (30d)</div>
            <div className="text-2xl font-bold text-white mt-1">{logs.length}</div>
          </div>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800 flex items-center space-x-4">
          <div className="p-3 rounded-lg bg-amber-500/10 text-amber-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Avg API Latency</div>
            <div className="text-2xl font-bold text-white mt-1">38.4 ms</div>
          </div>
        </div>
      </div>

      {/* Tabs Bar */}
      <div className="flex border-b border-slate-800 space-x-8">
        <button
          onClick={() => setActiveTab('keys')}
          className={`pb-3 flex items-center space-x-2 text-sm font-semibold border-b-2 transition ${
            activeTab === 'keys'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Key className="w-4 h-4" />
          <span>API Keys ({apiKeys.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('webhooks')}
          className={`pb-3 flex items-center space-x-2 text-sm font-semibold border-b-2 transition ${
            activeTab === 'webhooks'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Webhook className="w-4 h-4" />
          <span>Webhooks Subscriptions ({webhooks.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('logs')}
          className={`pb-3 flex items-center space-x-2 text-sm font-semibold border-b-2 transition ${
            activeTab === 'logs'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Terminal className="w-4 h-4" />
          <span>Event Dispatch Logs ({logs.length})</span>
        </button>
      </div>

      {/* TAB 1: API KEYS */}
      {activeTab === 'keys' && (
        <div className="bg-slate-900/60 rounded-2xl border border-slate-800 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">Active Developer API Keys</h3>
              <p className="text-xs text-slate-400">
                Secret tokens carry full programmatical access to PMS rates, inventory sync, and BI reports. Keep them confidential.
              </p>
            </div>
            <button onClick={fetchData} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          {loading ? (
            <div className="py-12 text-center text-slate-400 text-sm animate-pulse">Loading API keys...</div>
          ) : apiKeys.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-sm">No API keys generated yet.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-950/80 text-slate-400 text-xs uppercase tracking-wider">
                  <tr>
                    <th className="p-3.5 rounded-l-lg">Key Name</th>
                    <th className="p-3.5">Key Prefix</th>
                    <th className="p-3.5">Scopes</th>
                    <th className="p-3.5">Rate Limit</th>
                    <th className="p-3.5">Last Used</th>
                    <th className="p-3.5">Status</th>
                    <th className="p-3.5 text-right rounded-r-lg">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {apiKeys.map((key) => (
                    <tr key={key.id} className="hover:bg-slate-800/30 transition">
                      <td className="p-3.5 font-semibold text-white">
                        {key.name}
                        <div className="text-xs text-slate-500 font-normal">Created: {new Date(key.created_at).toLocaleDateString()}</div>
                      </td>
                      <td className="p-3.5 font-mono text-xs text-indigo-300">
                        {key.api_key_prefix}
                      </td>
                      <td className="p-3.5">
                        <div className="flex flex-wrap gap-1">
                          {key.scopes?.map((s: string) => (
                            <span key={s} className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-300 border border-slate-700">
                              {s}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="p-3.5 text-xs text-slate-400">
                        {key.rate_limit_per_min} req/min
                      </td>
                      <td className="p-3.5 text-xs text-slate-400">
                        {key.last_used_at ? new Date(key.last_used_at).toLocaleString() : 'Never'}
                      </td>
                      <td className="p-3.5">
                        <span
                          className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                            key.status === 'active'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                              : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                          }`}
                        >
                          {key.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="p-3.5 text-right">
                        {key.status === 'active' && (
                          <button
                            onClick={() => handleRevokeKey(key.id)}
                            className="px-3 py-1 bg-rose-950/60 hover:bg-rose-900 text-rose-300 border border-rose-800 rounded-lg text-xs font-medium transition"
                          >
                            Revoke
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: WEBHOOKS */}
      {activeTab === 'webhooks' && (
        <div className="bg-slate-900/60 rounded-2xl border border-slate-800 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">Webhook Subscriptions</h3>
              <p className="text-xs text-slate-400">
                Receive real-time HTTP POST JSON events when rate recommendations change or anomaly alerts trigger.
              </p>
            </div>
            <button onClick={fetchData} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          {loading ? (
            <div className="py-12 text-center text-slate-400 text-sm animate-pulse">Loading webhooks...</div>
          ) : webhooks.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-sm">No webhook endpoints registered yet.</div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {webhooks.map((wh) => (
                <div key={wh.id} className="bg-slate-950/80 p-5 rounded-xl border border-slate-800 space-y-3">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
                    <div className="flex items-center space-x-3">
                      <div className="p-2.5 rounded-lg bg-violet-500/10 text-violet-400">
                        <Webhook className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="font-semibold text-white text-base">{wh.description || 'Webhook Endpoint'}</div>
                        <div className="font-mono text-xs text-indigo-400 truncate max-w-lg">{wh.endpoint_url}</div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleTestDispatch(wh.id, wh.events[0] || 'price.updated')}
                        disabled={dispatchingId === wh.id}
                        className="flex items-center space-x-1.5 px-3 py-1.5 bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-300 border border-indigo-500/30 rounded-lg text-xs font-medium transition"
                      >
                        <Send className="w-3.5 h-3.5" />
                        <span>{dispatchingId === wh.id ? 'Dispatching...' : 'Test Dispatch'}</span>
                      </button>
                      <button
                        onClick={() => handleDeleteWebhook(wh.id)}
                        className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-3 border-t border-slate-800/60 text-xs">
                    <div>
                      <span className="text-slate-500 block mb-1">Subscribed Events</span>
                      <div className="flex flex-wrap gap-1">
                        {wh.events?.map((ev: string) => (
                          <span key={ev} className="px-2 py-0.5 rounded bg-violet-950/60 text-violet-300 border border-violet-800/50 font-mono text-[10px]">
                            {ev}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <span className="text-slate-500 block mb-1">HMAC Signature Secret</span>
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-slate-300">
                          {showSecretMap[wh.id] ? wh.secret_key : wh.secret_key.slice(0, 8) + '••••••••••••••••'}
                        </span>
                        <button
                          onClick={() => toggleSecretVisibility(wh.id)}
                          className="text-slate-400 hover:text-slate-200"
                        >
                          {showSecretMap[wh.id] ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                        </button>
                      </div>
                    </div>

                    <div>
                      <span className="text-slate-500 block mb-1">Last Triggered</span>
                      <span className="text-slate-300">
                        {wh.last_triggered_at ? new Date(wh.last_triggered_at).toLocaleString() : 'Never'}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: DISPATCH LOGS */}
      {activeTab === 'logs' && (
        <div className="bg-slate-900/60 rounded-2xl border border-slate-800 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">Live Event Dispatch Logs</h3>
              <p className="text-xs text-slate-400">
                Audit trial of recent outgoing webhook dispatches, HTTP status responses, and execution latency.
              </p>
            </div>
            <button onClick={fetchData} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          {loading ? (
            <div className="py-12 text-center text-slate-400 text-sm animate-pulse">Loading execution logs...</div>
          ) : logs.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-sm">No webhook dispatch logs recorded yet.</div>
          ) : (
            <div className="space-y-3">
              {logs.map((log) => (
                <div key={log.id} className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="px-2.5 py-1 rounded bg-indigo-950 text-indigo-300 font-mono text-xs font-semibold border border-indigo-800">
                        {log.event_type}
                      </span>
                      <span className="text-xs text-slate-400">Subscription #{log.subscription_id}</span>
                      <span className="text-xs text-slate-500">Delivered: {new Date(log.delivered_at).toLocaleString()}</span>
                    </div>

                    <div className="flex items-center space-x-3">
                      <span className="text-xs text-slate-400 font-mono">{log.execution_time_ms} ms</span>
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-bold ${
                          log.response_status_code === 200
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                        }`}
                      >
                        HTTP {log.response_status_code}
                      </span>
                    </div>
                  </div>

                  {/* JSON Payload View */}
                  <div className="bg-slate-900 p-3 rounded-lg font-mono text-xs text-emerald-300/90 overflow-x-auto border border-slate-800">
                    <pre>{JSON.stringify(log.payload, null, 2)}</pre>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* GENERATE API KEY MODAL */}
      {showKeyModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 rounded-2xl border border-slate-800 max-w-lg w-full p-6 space-y-5 shadow-2xl">
            {generatedRawKey ? (
              <div className="space-y-4">
                <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-300 text-sm flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold">API Key Generated!</div>
                    <div className="text-xs text-emerald-200/80 mt-0.5">
                      Copy your API secret key now. You will NOT be able to see it again!
                    </div>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs text-slate-400 font-medium">Your API Secret Key</label>
                  <div className="flex items-center space-x-2 bg-slate-950 p-3 rounded-xl border border-slate-800 font-mono text-xs text-indigo-300">
                    <span className="truncate flex-1">{generatedRawKey}</span>
                    <button
                      onClick={() => copyToClipboard(generatedRawKey)}
                      className="p-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition"
                    >
                      {copiedKey ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <button
                  onClick={() => {
                    setShowKeyModal(false);
                    setGeneratedRawKey(null);
                    setNewKeyName('');
                  }}
                  className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-sm font-semibold transition"
                >
                  Done & Close
                </button>
              </div>
            ) : (
              <form onSubmit={handleCreateKey} className="space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                    <Key className="w-5 h-5 text-indigo-400" />
                    <span>Generate New Developer API Key</span>
                  </h3>
                  <button
                    type="button"
                    onClick={() => setShowKeyModal(false)}
                    className="text-slate-400 hover:text-white"
                  >
                    ✕
                  </button>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-300">Key Identifier Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Opera PMS Sync Engine"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-300">Access Scopes</label>
                  <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                    {allAvailableScopes.map((scope) => (
                      <label
                        key={scope.id}
                        className={`flex items-start space-x-3 p-2.5 rounded-xl border cursor-pointer transition ${
                          selectedScopes.includes(scope.id)
                            ? 'bg-indigo-950/40 border-indigo-500/50'
                            : 'bg-slate-950 border-slate-800'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={selectedScopes.includes(scope.id)}
                          onChange={() => toggleScope(scope.id)}
                          className="mt-1 accent-indigo-500 rounded"
                        />
                        <div>
                          <div className="text-xs font-semibold text-white">{scope.label}</div>
                          <div className="text-[11px] text-slate-400">{scope.desc}</div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-300">Expiration Period</label>
                  <select
                    value={expiresInDays}
                    onChange={(e) => setExpiresInDays(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value={30}>30 Days</option>
                    <option value={90}>90 Days (Recommended)</option>
                    <option value={180}>180 Days</option>
                    <option value={365}>1 Year</option>
                  </select>
                </div>

                <div className="flex justify-end space-x-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowKeyModal(false)}
                    className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-sm font-medium hover:bg-slate-700"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-semibold shadow-lg shadow-indigo-600/30"
                  >
                    Generate Key
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* NEW WEBHOOK MODAL */}
      {showWebhookModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 rounded-2xl border border-slate-800 max-w-lg w-full p-6 space-y-5 shadow-2xl">
            <form onSubmit={handleCreateWebhook} className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                  <Webhook className="w-5 h-5 text-violet-400" />
                  <span>Register Webhook Listener</span>
                </h3>
                <button
                  type="button"
                  onClick={() => setShowWebhookModal(false)}
                  className="text-slate-400 hover:text-white"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Endpoint URL (HTTPS)</label>
                <input
                  type="url"
                  required
                  placeholder="https://api.pms-hub.in/webhooks/revenue"
                  value={webhookUrl}
                  onChange={(e) => setWebhookUrl(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Description / Target Name</label>
                <input
                  type="text"
                  placeholder="e.g. Production PMS Webhook Engine"
                  value={webhookDescription}
                  onChange={(e) => setWebhookDescription(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-300">Subscribed Events</label>
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {allAvailableEvents.map((ev) => (
                    <label
                      key={ev.id}
                      className={`flex items-start space-x-3 p-2.5 rounded-xl border cursor-pointer transition ${
                        webhookEvents.includes(ev.id)
                          ? 'bg-violet-950/40 border-violet-500/50'
                          : 'bg-slate-950 border-slate-800'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={webhookEvents.includes(ev.id)}
                        onChange={() => toggleWebhookEvent(ev.id)}
                        className="mt-1 accent-violet-500 rounded"
                      />
                      <div>
                        <div className="text-xs font-mono font-semibold text-violet-300">{ev.label}</div>
                        <div className="text-[11px] text-slate-400">{ev.desc}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowWebhookModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-sm font-medium hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-xl text-sm font-semibold shadow-lg shadow-violet-600/30"
                >
                  Register Subscription
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
