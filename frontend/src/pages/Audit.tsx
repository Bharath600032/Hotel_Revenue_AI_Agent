import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { AuditLogItem } from '../types';
import { History, Shield, Filter, RefreshCw } from 'lucide-react';

export const Audit: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState('');
  const [entityFilter, setEntityFilter] = useState('');

  useEffect(() => {
    fetchLogs();
  }, [actionFilter, entityFilter]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await apiService.getAuditLogs(actionFilter || undefined, entityFilter || undefined);
      setLogs(data);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <History className="w-7 h-7 text-indigo-400" />
            Immutable System Audit Trail
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Complete compliance timeline of automated price updates, human approvals, overrides, and model runs.
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 p-2 rounded-xl text-xs">
          <Filter className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Filter Action..."
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-white px-2 py-1 rounded w-32"
          />
          <input
            type="text"
            placeholder="Filter Entity..."
            value={entityFilter}
            onChange={(e) => setEntityFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-white px-2 py-1 rounded w-32"
          />
          <button
            onClick={fetchLogs}
            className="p-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
        {loading ? (
          <div className="flex justify-center items-center h-48">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
          </div>
        ) : logs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider">
                  <th className="pb-3 px-3">Timestamp</th>
                  <th className="pb-3 px-3">Action</th>
                  <th className="pb-3 px-3">Entity Type</th>
                  <th className="pb-3 px-3">Entity ID</th>
                  <th className="pb-3 px-3">Old State</th>
                  <th className="pb-3 px-3">New State</th>
                  <th className="pb-3 px-3">IP Address</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {logs.map((log) => (
                  <tr key={log.audit_id} className="hover:bg-slate-800/30">
                    <td className="py-3 px-3 font-mono text-xs text-slate-400">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-3 font-bold text-indigo-400">{log.action}</td>
                    <td className="py-3 px-3 text-slate-300">{log.entity_type}</td>
                    <td className="py-3 px-3 font-mono text-xs text-slate-400">#{log.entity_id || '-'}</td>
                    <td className="py-3 px-3 text-xs text-rose-400 font-mono truncate max-w-xs">{log.old_value || '-'}</td>
                    <td className="py-3 px-3 text-xs text-emerald-400 font-mono truncate max-w-xs">{log.new_value || '-'}</td>
                    <td className="py-3 px-3 text-xs font-mono text-slate-500">{log.ip_address || '127.0.0.1'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12 text-slate-500 text-xs">
            No audit log records found for the given filter criteria.
          </div>
        )}
      </div>
    </div>
  );
};
