import React, { useState, useEffect } from 'react';
import {
  Bell,
  ShieldAlert,
  Send,
  CheckCircle2,
  AlertTriangle,
  Info,
  Clock,
  Mail,
  MessageSquare,
  Slack,
  Smartphone,
  RefreshCw,
  Sliders,
  Play,
  UserCheck,
  Zap,
  Filter,
  Layers,
  ChevronRight,
  Sparkles,
  ExternalLink,
} from 'lucide-react';
import { apiService } from '../services/api';

interface AlertLog {
  log_id: number;
  hotel_id: number;
  rule_id?: number;
  alert_type: string;
  severity: string;
  title: string;
  message: string;
  channel: string;
  status: string;
  recipient?: string;
  metadata_json?: Record<string, any>;
  created_at: string;
  acknowledged_at?: string;
  acknowledged_by?: string;
}

interface AlertRule {
  rule_id: number;
  hotel_id: number;
  alert_type: string;
  rule_name: string;
  description?: string;
  threshold_value: number;
  severity: string;
  is_enabled: boolean;
  notify_email: boolean;
  notify_whatsapp: boolean;
  notify_slack: boolean;
  notify_in_app: boolean;
  recipients?: string;
  slack_webhook_url?: string;
  created_at: string;
  updated_at: string;
}

export const AlertsNotifications: React.FC = () => {
  const [hotelId] = useState<number>(1);
  const [activeTab, setActiveTab] = useState<'feed' | 'rules' | 'simulator'>('feed');

  // Data states
  const [alerts, setAlerts] = useState<AlertLog[]>([]);
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [channelFilter, setChannelFilter] = useState<string>('ALL');
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');

  // Simulator states
  const [simChannel, setSimChannel] = useState<string>('SLACK');
  const [simTarget, setSimTarget] = useState<string>('https://hooks.slack.com/services/T00/B00/XXXX');
  const [simType, setSimType] = useState<string>('COMPETITOR_UNDERCUT');
  const [simResult, setSimResult] = useState<any>(null);
  const [simulating, setSimulating] = useState<boolean>(false);

  // Editing Rule state
  const [editingRule, setEditingRule] = useState<AlertRule | null>(null);
  const [editThreshold, setEditThreshold] = useState<number>(10);

  useEffect(() => {
    fetchAlertsData();
  }, [hotelId, statusFilter, channelFilter, severityFilter]);

  const fetchAlertsData = async () => {
    try {
      setLoading(true);
      const [alertLogs, alertRules] = await Promise.all([
        apiService.getAlerts(hotelId, statusFilter, channelFilter, severityFilter),
        apiService.getAlertRules(hotelId),
      ]);
      setAlerts(alertLogs);
      setRules(alertRules);
    } catch (err) {
      console.error('Failed to fetch alerts data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = async (logId: number) => {
    try {
      await apiService.acknowledgeAlert(hotelId, logId, 'Senior Revenue Manager');
      fetchAlertsData();
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  const handleToggleRuleChannel = async (rule: AlertRule, field: string, currentValue: boolean) => {
    try {
      const updateData = { [field]: !currentValue };
      await apiService.updateAlertRule(hotelId, rule.rule_id, updateData);
      fetchAlertsData();
    } catch (err) {
      console.error('Failed to update rule toggle:', err);
    }
  };

  const handleSaveThreshold = async () => {
    if (!editingRule) return;
    try {
      await apiService.updateAlertRule(hotelId, editingRule.rule_id, { threshold_value: editThreshold });
      setEditingRule(null);
      fetchAlertsData();
    } catch (err) {
      console.error('Failed to save threshold:', err);
    }
  };

  const handleRunSimulator = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSimulating(true);
      const res = await apiService.testChannelDispatch(hotelId, {
        channel: simChannel,
        target_destination: simTarget,
        sample_type: simType,
      });
      setSimResult(res);
      fetchAlertsData();
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setSimulating(false);
    }
  };

  // Metrics
  const criticalCount = alerts.filter((a) => a.severity === 'CRITICAL').length;
  const unreadCount = alerts.filter((a) => a.status === 'DISPATCHED').length;
  const activeRulesCount = rules.filter((r) => r.is_enabled).length;

  const getSeverityBadge = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
            CRITICAL
          </span>
        );
      case 'WARNING':
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            WARNING
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30 flex items-center gap-1.5">
            <Info className="w-3.5 h-3.5 text-blue-400" />
            INFO
          </span>
        );
    }
  };

  const getChannelIcons = (channelStr: string) => {
    const cUpper = channelStr.toUpperCase();
    return (
      <div className="flex items-center gap-1.5 text-slate-400">
        {(cUpper.includes('EMAIL') || cUpper.includes('MULTI')) && (
          <span title="Email Alert" className="p-1 rounded bg-slate-800 text-slate-300">
            <Mail className="w-3.5 h-3.5" />
          </span>
        )}
        {(cUpper.includes('WHATSAPP') || cUpper.includes('MULTI')) && (
          <span title="WhatsApp / SMS Alert" className="p-1 rounded bg-emerald-900/50 text-emerald-400">
            <MessageSquare className="w-3.5 h-3.5" />
          </span>
        )}
        {(cUpper.includes('SLACK') || cUpper.includes('MULTI')) && (
          <span title="Slack / Teams Webhook" className="p-1 rounded bg-purple-900/50 text-purple-300">
            <Slack className="w-3.5 h-3.5" />
          </span>
        )}
        {(cUpper.includes('IN_APP') || cUpper.includes('MULTI')) && (
          <span title="In-App Push" className="p-1 rounded bg-blue-900/50 text-blue-400">
            <Smartphone className="w-3.5 h-3.5" />
          </span>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6 font-sans">
      {/* Page Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-2 border-b border-slate-800/60">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-3 tracking-tight">
            <Bell className="w-7 h-7 text-indigo-400 flex-shrink-0 animate-pulse-subtle" />
            <span>Automated Multi-Channel Alerts & Notifications</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Real-time anomaly monitoring, automated competitor rate drops & displacement alerts across WhatsApp, Email, Slack, and In-App channels.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-1.5 rounded-xl flex-shrink-0">
          <button
            onClick={() => setActiveTab('feed')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'feed'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Anomaly Feed ({alerts.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('rules')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'rules'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            <Sliders className="w-4 h-4" />
            <span>Channel Rules Matrix</span>
          </button>
          <button
            onClick={() => setActiveTab('simulator')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'simulator'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            <Send className="w-4 h-4" />
            <span>Dispatch Simulator</span>
          </button>
          <button
            onClick={fetchAlertsData}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors ml-1"
            title="Refresh Alert Logs"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Top Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-xs font-medium">Total Alerts Dispatched</p>
            <p className="text-2xl font-extrabold text-white mt-1">{alerts.length}</p>
            <span className="text-[11px] text-emerald-400 flex items-center gap-1 mt-1">
              <CheckCircle2 className="w-3 h-3" /> Multi-channel broadcast active
            </span>
          </div>
          <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl text-indigo-400">
            <Bell className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-xs font-medium">Critical Rate Breaches</p>
            <p className="text-2xl font-extrabold text-rose-400 mt-1">{criticalCount}</p>
            <span className="text-[11px] text-rose-400/80 flex items-center gap-1 mt-1">
              <ShieldAlert className="w-3 h-3" /> Requires immediate review
            </span>
          </div>
          <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400">
            <ShieldAlert className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-xs font-medium">Pending Unread Alerts</p>
            <p className="text-2xl font-extrabold text-amber-300 mt-1">{unreadCount}</p>
            <span className="text-[11px] text-amber-400/80 flex items-center gap-1 mt-1">
              <Clock className="w-3 h-3" /> Awaiting response
            </span>
          </div>
          <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-400">
            <AlertTriangle className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-xs font-medium">Active Rule Triggers</p>
            <p className="text-2xl font-extrabold text-emerald-400 mt-1">{activeRulesCount} / {rules.length}</p>
            <span className="text-[11px] text-emerald-400 flex items-center gap-1 mt-1">
              <Zap className="w-3 h-3" /> 100% Delivery SLA
            </span>
          </div>
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400">
            <Sliders className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* TAB 1: ANOMALY FEED & ALERT HISTORY */}
      {activeTab === 'feed' && (
        <div className="space-y-4">
          {/* Filters Bar */}
          <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <Filter className="w-4 h-4 text-indigo-400" />
              <span className="font-semibold text-white">Filters:</span>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              {/* Channel Filter */}
              <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-xl text-xs">
                <span className="text-slate-400">Channel:</span>
                <select
                  value={channelFilter}
                  onChange={(e) => setChannelFilter(e.target.value)}
                  className="bg-transparent text-white font-medium focus:outline-none cursor-pointer"
                >
                  <option value="ALL" className="bg-slate-900">All Channels</option>
                  <option value="EMAIL" className="bg-slate-900">Email</option>
                  <option value="WHATSAPP" className="bg-slate-900">WhatsApp / SMS</option>
                  <option value="SLACK" className="bg-slate-900">Slack / Teams</option>
                  <option value="IN_APP" className="bg-slate-900">In-App</option>
                </select>
              </div>

              {/* Severity Filter */}
              <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-xl text-xs">
                <span className="text-slate-400">Severity:</span>
                <select
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value)}
                  className="bg-transparent text-white font-medium focus:outline-none cursor-pointer"
                >
                  <option value="ALL" className="bg-slate-900">All Severities</option>
                  <option value="CRITICAL" className="bg-slate-900">Critical</option>
                  <option value="WARNING" className="bg-slate-900">Warning</option>
                  <option value="INFO" className="bg-slate-900">Info</option>
                </select>
              </div>

              {/* Status Filter */}
              <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-xl text-xs">
                <span className="text-slate-400">Status:</span>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="bg-transparent text-white font-medium focus:outline-none cursor-pointer"
                >
                  <option value="ALL" className="bg-slate-900">All Statuses</option>
                  <option value="DISPATCHED" className="bg-slate-900">Dispatched (Unread)</option>
                  <option value="ACKNOWLEDGED" className="bg-slate-900">Acknowledged</option>
                </select>
              </div>
            </div>
          </div>

          {/* Alerts Feed Cards */}
          {loading ? (
            <div className="p-12 text-center text-slate-400 bg-slate-900/50 border border-slate-800 rounded-2xl">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto text-indigo-400 mb-2" />
              <p className="text-sm">Fetching real-time multi-channel alerts...</p>
            </div>
          ) : alerts.length === 0 ? (
            <div className="p-12 text-center text-slate-400 bg-slate-900/50 border border-slate-800 rounded-2xl">
              <CheckCircle2 className="w-8 h-8 mx-auto text-emerald-400 mb-2" />
              <p className="text-sm font-semibold text-white">No active alert breaches found</p>
              <p className="text-xs text-slate-500 mt-1">All revenue parameters are currently within guardrail safety limits.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {alerts.map((alert) => (
                <div
                  key={alert.log_id}
                  className={`p-5 rounded-2xl border transition-all ${
                    alert.status === 'ACKNOWLEDGED'
                      ? 'bg-slate-900/40 border-slate-800/80 opacity-85'
                      : alert.severity === 'CRITICAL'
                      ? 'bg-rose-950/20 border-rose-500/40 shadow-lg shadow-rose-950/30'
                      : alert.severity === 'WARNING'
                      ? 'bg-amber-950/20 border-amber-500/40 shadow-lg shadow-amber-950/20'
                      : 'bg-slate-900/90 border-slate-800'
                  }`}
                >
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    {/* Main Alert Info */}
                    <div className="space-y-2 flex-grow">
                      <div className="flex flex-wrap items-center gap-2">
                        {getSeverityBadge(alert.severity)}
                        {getChannelIcons(alert.channel)}
                        <span className="text-xs text-slate-500 font-mono">
                          {new Date(alert.created_at).toLocaleString()}
                        </span>
                        {alert.status === 'ACKNOWLEDGED' && (
                          <span className="px-2 py-0.5 rounded text-[11px] bg-slate-800 text-slate-400 flex items-center gap-1">
                            <UserCheck className="w-3 h-3 text-emerald-400" />
                            Ack by {alert.acknowledged_by}
                          </span>
                        )}
                      </div>

                      <h3 className="text-base font-bold text-white tracking-tight">{alert.title}</h3>
                      <p className="text-sm text-slate-300 leading-relaxed">{alert.message}</p>

                      {/* Context Metadata Pills */}
                      {alert.metadata_json && Object.keys(alert.metadata_json).length > 0 && (
                        <div className="flex flex-wrap items-center gap-2 pt-1">
                          {Object.entries(alert.metadata_json).map(([k, v]) => (
                            <span
                              key={k}
                              className="px-2 py-0.5 bg-slate-950 border border-slate-800/80 rounded text-[11px] text-indigo-300 font-mono"
                            >
                              <strong className="text-slate-400 font-semibold">{k.replace('_', ' ')}:</strong>{' '}
                              {typeof v === 'number' && (k.includes('rate') || k.includes('impact') || k.includes('revpor'))
                                ? `₹${v.toLocaleString('en-IN')}`
                                : String(v)}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center gap-2 flex-shrink-0 lg:flex-col lg:items-end">
                      {alert.status === 'DISPATCHED' ? (
                        <button
                          onClick={() => handleAcknowledge(alert.log_id)}
                          className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-1.5 cursor-pointer whitespace-nowrap"
                        >
                          <CheckCircle2 className="w-4 h-4" />
                          <span>Acknowledge Alert</span>
                        </button>
                      ) : (
                        <span className="text-xs text-emerald-400 flex items-center gap-1 font-medium bg-emerald-950/40 border border-emerald-500/30 px-3 py-1.5 rounded-xl">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Acknowledged</span>
                        </span>
                      )}

                      <span className="text-[11px] text-slate-500">
                        Recipient: <strong className="text-slate-400">{alert.recipient || 'Multi-Channel'}</strong>
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: AUTOMATED RULES CONFIG MATRIX */}
      {activeTab === 'rules' && (
        <div className="space-y-4">
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <Sliders className="w-5 h-5 text-indigo-400" />
                  Automated Multi-Channel Notification Rules Matrix
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Configure anomaly detection thresholds and toggle dispatch channels (Email, WhatsApp, Slack, In-App).
                </p>
              </div>
            </div>

            {/* Rules Table */}
            <div className="overflow-x-auto mt-4">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider bg-slate-950/50">
                    <th className="p-3">Rule Name & Trigger</th>
                    <th className="p-3">Severity</th>
                    <th className="p-3">Threshold</th>
                    <th className="p-3 text-center">Email</th>
                    <th className="p-3 text-center">WhatsApp</th>
                    <th className="p-3 text-center">Slack</th>
                    <th className="p-3 text-center">In-App</th>
                    <th className="p-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-xs">
                  {rules.map((rule) => (
                    <tr key={rule.rule_id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="p-3">
                        <p className="font-bold text-white text-sm">{rule.rule_name}</p>
                        <p className="text-slate-400 text-xs mt-0.5">{rule.description}</p>
                      </td>
                      <td className="p-3">{getSeverityBadge(rule.severity)}</td>
                      <td className="p-3 font-mono text-indigo-300 font-semibold">
                        {rule.alert_type === 'DISPLACEMENT_THRESHOLD'
                          ? `₹${rule.threshold_value.toLocaleString('en-IN')}`
                          : rule.alert_type === 'HIGH_DEMAND_EVENT'
                          ? `Level ${rule.threshold_value}`
                          : `${rule.threshold_value}%`}
                      </td>

                      {/* Email Toggle */}
                      <td className="p-3 text-center">
                        <input
                          type="checkbox"
                          checked={rule.notify_email}
                          onChange={() => handleToggleRuleChannel(rule, 'notify_email', rule.notify_email)}
                          className="w-4 h-4 accent-indigo-500 cursor-pointer rounded"
                        />
                      </td>

                      {/* WhatsApp Toggle */}
                      <td className="p-3 text-center">
                        <input
                          type="checkbox"
                          checked={rule.notify_whatsapp}
                          onChange={() => handleToggleRuleChannel(rule, 'notify_whatsapp', rule.notify_whatsapp)}
                          className="w-4 h-4 accent-emerald-500 cursor-pointer rounded"
                        />
                      </td>

                      {/* Slack Toggle */}
                      <td className="p-3 text-center">
                        <input
                          type="checkbox"
                          checked={rule.notify_slack}
                          onChange={() => handleToggleRuleChannel(rule, 'notify_slack', rule.notify_slack)}
                          className="w-4 h-4 accent-purple-500 cursor-pointer rounded"
                        />
                      </td>

                      {/* In-App Toggle */}
                      <td className="p-3 text-center">
                        <input
                          type="checkbox"
                          checked={rule.notify_in_app}
                          onChange={() => handleToggleRuleChannel(rule, 'notify_in_app', rule.notify_in_app)}
                          className="w-4 h-4 accent-blue-500 cursor-pointer rounded"
                        />
                      </td>

                      {/* Edit Button */}
                      <td className="p-3 text-right">
                        <button
                          onClick={() => {
                            setEditingRule(rule);
                            setEditThreshold(rule.threshold_value);
                          }}
                          className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs transition-colors"
                        >
                          Edit Limit
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: DISPATCH SIMULATOR */}
      {activeTab === 'simulator' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Simulator Form */}
          <div className="lg:col-span-5 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Send className="w-5 h-5 text-indigo-400" />
              Multi-Channel Delivery Simulator
            </h2>
            <p className="text-xs text-slate-400">
              Simulate live dispatch payloads to verify channel format rendering across Slack, WhatsApp, Email, and In-App.
            </p>

            <form onSubmit={handleRunSimulator} className="space-y-4 pt-2">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Select Channel</label>
                <select
                  value={simChannel}
                  onChange={(e) => setSimChannel(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
                >
                  <option value="SLACK">Slack / Teams Webhook (Block Kit)</option>
                  <option value="WHATSAPP">WhatsApp / SMS (Twilio Text)</option>
                  <option value="EMAIL">Email (HTML Digest)</option>
                  <option value="IN_APP">In-App Banner Push</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Target Destination</label>
                <input
                  type="text"
                  value={simTarget}
                  onChange={(e) => setSimTarget(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white focus:border-indigo-500 focus:outline-none font-mono"
                  placeholder="e.g. https://hooks.slack.com/services/..."
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Alert Anomaly Scenario</label>
                <select
                  value={simType}
                  onChange={(e) => setSimType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
                >
                  <option value="COMPETITOR_UNDERCUT">Competitor Undercut (&gt; 10% Rate Drop)</option>
                  <option value="PACE_SURGE">Unusual Booking Pace Spike (+32 Rooms)</option>
                  <option value="DISPLACEMENT_THRESHOLD">Group Displacement Net Loss Breach (₹74,500)</option>
                  <option value="TREVPAR_BREACH">Non-Room TRevPAR Deficit (18.2% Below Target)</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={simulating}
                className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center gap-2 cursor-pointer"
              >
                {simulating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-white" />}
                <span>Dispatch Test Payload</span>
              </button>
            </form>
          </div>

          {/* Payload Preview Render */}
          <div className="lg:col-span-7 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-emerald-400" />
                  Live Channel Formatted Payload Output
                </h3>
                {simResult && (
                  <span className="text-[11px] text-emerald-400 bg-emerald-950/40 border border-emerald-500/30 px-2.5 py-0.5 rounded-full font-mono">
                    200 OK • Dispatched
                  </span>
                )}
              </div>

              <div className="mt-4">
                {simResult ? (
                  <div className="bg-slate-950 border border-slate-800/80 rounded-xl p-4 font-mono text-xs text-emerald-300 leading-relaxed whitespace-pre-wrap overflow-x-auto max-h-[380px]">
                    {simResult.formatted_payload}
                  </div>
                ) : (
                  <div className="p-12 text-center text-slate-500 bg-slate-950/40 border border-slate-800/60 rounded-xl">
                    <Send className="w-8 h-8 mx-auto text-slate-600 mb-2" />
                    <p className="text-xs">Click "Dispatch Test Payload" to render live formatted message payload.</p>
                  </div>
                )}
              </div>
            </div>

            {simResult && (
              <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
                <span>
                  Target: <strong className="text-white">{simResult.recipient}</strong>
                </span>
                <span className="font-mono text-[11px]">
                  Timestamp: {new Date(simResult.dispatched_at).toLocaleTimeString()}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Edit Threshold Modal */}
      {editingRule && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Edit Rule Limit Threshold</h3>
            <p className="text-xs text-slate-400">{editingRule.rule_name}</p>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Threshold Limit Value ({editingRule.alert_type === 'DISPLACEMENT_THRESHOLD' ? '₹ INR' : '%'})
              </label>
              <input
                type="number"
                value={editThreshold}
                onChange={(e) => setEditThreshold(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-sm text-white focus:border-indigo-500 focus:outline-none font-mono"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setEditingRule(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveThreshold}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/30"
              >
                Save Threshold
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
