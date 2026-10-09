import React, { useEffect, useState, useRef } from 'react';
import { apiService } from '../services/api';
import { AuditLogItem } from '../types';
import { History, Shield, Filter, RefreshCw, Eye, X, FileText, RotateCcw, ChevronDown, Check, ChevronLeft, ChevronRight } from 'lucide-react';

export const Audit: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState('');
  const [entityFilter, setEntityFilter] = useState('');
  const [selectedLog, setSelectedLog] = useState<AuditLogItem | null>(null);

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const [showActionDropdown, setShowActionDropdown] = useState(false);
  const [showEntityDropdown, setShowEntityDropdown] = useState(false);

  const actionRef = useRef<HTMLDivElement>(null);
  const entityRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchLogs();
  }, []);

  useEffect(() => {
    setCurrentPage(1);
  }, [actionFilter, entityFilter]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (actionRef.current && !actionRef.current.contains(event.target as Node)) {
        setShowActionDropdown(false);
      }
      if (entityRef.current && !entityRef.current.contains(event.target as Node)) {
        setShowEntityDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await apiService.getAuditLogs(actionFilter || undefined, entityFilter || undefined);
      setLogs(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearFilters = () => {
    setActionFilter('');
    setEntityFilter('');
  };

  // Dynamically extract unique actions and entities from logs + system defaults
  const availableActions = Array.from(
    new Set([
      'APPROVE_AND_PUBLISH_PRICE',
      'MANUAL_RATE_OVERRIDE',
      'AUTOMATED_PRICING_PUBLISH',
      'COMPETITOR_SYNC_GOOGLE',
      'REJECT_RECOMMENDATION',
      'HOTEL_UPDATE',
      ...logs.map((l) => l.action).filter(Boolean),
    ])
  );

  const availableEntities = Array.from(
    new Set([
      'PriceRecommendation',
      'Hotel',
      'CompetitorRates',
      'LOSRules',
      'AncillaryPackage',
      ...logs.map((l) => l.entity_type).filter(Boolean),
    ])
  );

  const filteredLogs = logs.filter((log) => {
    const act = actionFilter.trim().toLowerCase();
    const ent = entityFilter.trim().toLowerCase();

    const logAction = (log.action || '').toLowerCase();
    const logEntity = (log.entity_type || '').toLowerCase();
    const logEntityId = (log.entity_id ? String(log.entity_id) : '').toLowerCase();

    const matchesAction = !act || logAction.includes(act);
    const matchesEntity = !ent || logEntity.includes(ent) || logEntityId.includes(ent);
    return matchesAction && matchesEntity;
  });

  // Pagination Math
  const totalPages = Math.ceil(filteredLogs.length / itemsPerPage) || 1;
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedLogs = filteredLogs.slice(startIndex, startIndex + itemsPerPage);

  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      if (currentPage > 3) pages.push('...');
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);
      for (let i = start; i <= end; i++) pages.push(i);
      if (currentPage < totalPages - 2) pages.push('...');
      pages.push(totalPages);
    }
    return pages;
  };

  const formatLogValue = (val: any): string => {
    if (val === null || val === undefined || val === '') return '-';
    if (typeof val === 'object') {
      try {
        return JSON.stringify(val);
      } catch {
        return '[Object]';
      }
    }
    return String(val);
  };

  const formatPrettyJson = (val: any): string => {
    if (val === null || val === undefined || val === '') return 'N/A';
    if (typeof val === 'object') {
      try {
        return JSON.stringify(val, null, 2);
      } catch {
        return String(val);
      }
    }
    try {
      const parsed = JSON.parse(val);
      return JSON.stringify(parsed, null, 2);
    } catch {
      return String(val);
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
        <div className="flex flex-wrap items-center gap-3 bg-slate-900 border border-slate-800 p-2 rounded-xl text-xs relative">
          
          {/* Action Filter Dropdown */}
          <div ref={actionRef} className="relative">
            <div className="flex items-center bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 focus-within:border-indigo-500">
              <button
                onClick={() => setShowActionDropdown(!showActionDropdown)}
                className="p-1 text-indigo-400 hover:text-indigo-300 transition-colors flex items-center gap-1"
                title="Click to select Action from dropdown"
              >
                <Filter className="w-4 h-4" />
              </button>
              <input
                type="text"
                placeholder="Filter Action..."
                value={actionFilter}
                onChange={(e) => setActionFilter(e.target.value)}
                onFocus={() => setShowActionDropdown(true)}
                className="bg-transparent text-white px-2 py-0.5 rounded w-36 focus:outline-none text-xs"
              />
              <button
                onClick={() => setShowActionDropdown(!showActionDropdown)}
                className="text-slate-500 hover:text-slate-300"
              >
                <ChevronDown className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Action Dropdown Menu */}
            {showActionDropdown && (
              <div className="absolute left-0 top-full mt-1.5 w-64 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl z-40 py-1 max-h-60 overflow-y-auto divide-y divide-slate-800/50">
                <div className="px-3 py-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider bg-slate-950/80">
                  Select Action Filter
                </div>
                <button
                  onClick={() => {
                    setActionFilter('');
                    setShowActionDropdown(false);
                  }}
                  className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between hover:bg-indigo-600/20 hover:text-indigo-300 transition-colors ${
                    actionFilter === '' ? 'text-indigo-400 font-bold bg-indigo-500/10' : 'text-slate-300'
                  }`}
                >
                  <span>All Actions</span>
                  {actionFilter === '' && <Check className="w-3.5 h-3.5 text-indigo-400" />}
                </button>
                {availableActions.map((act) => (
                  <button
                    key={act}
                    onClick={() => {
                      setActionFilter(act);
                      setShowActionDropdown(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between hover:bg-indigo-600/20 hover:text-indigo-300 transition-colors font-mono ${
                      actionFilter === act ? 'text-indigo-400 font-bold bg-indigo-500/10' : 'text-slate-300'
                    }`}
                  >
                    <span className="truncate">{act}</span>
                    {actionFilter === act && <Check className="w-3.5 h-3.5 text-indigo-400 shrink-0" />}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Entity Filter Dropdown */}
          <div ref={entityRef} className="relative">
            <div className="flex items-center bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 focus-within:border-indigo-500">
              <button
                onClick={() => setShowEntityDropdown(!showEntityDropdown)}
                className="p-1 text-emerald-400 hover:text-emerald-300 transition-colors flex items-center gap-1"
                title="Click to select Entity Type from dropdown"
              >
                <Shield className="w-4 h-4" />
              </button>
              <input
                type="text"
                placeholder="Filter Entity..."
                value={entityFilter}
                onChange={(e) => setEntityFilter(e.target.value)}
                onFocus={() => setShowEntityDropdown(true)}
                className="bg-transparent text-white px-2 py-0.5 rounded w-36 focus:outline-none text-xs"
              />
              <button
                onClick={() => setShowEntityDropdown(!showEntityDropdown)}
                className="text-slate-500 hover:text-slate-300"
              >
                <ChevronDown className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Entity Dropdown Menu */}
            {showEntityDropdown && (
              <div className="absolute left-0 top-full mt-1.5 w-60 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl z-40 py-1 max-h-60 overflow-y-auto divide-y divide-slate-800/50">
                <div className="px-3 py-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider bg-slate-950/80">
                  Select Entity Type
                </div>
                <button
                  onClick={() => {
                    setEntityFilter('');
                    setShowEntityDropdown(false);
                  }}
                  className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between hover:bg-emerald-600/20 hover:text-emerald-300 transition-colors ${
                    entityFilter === '' ? 'text-emerald-400 font-bold bg-emerald-500/10' : 'text-slate-300'
                  }`}
                >
                  <span>All Entity Types</span>
                  {entityFilter === '' && <Check className="w-3.5 h-3.5 text-emerald-400" />}
                </button>
                {availableEntities.map((ent) => (
                  <button
                    key={ent}
                    onClick={() => {
                      setEntityFilter(ent);
                      setShowEntityDropdown(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between hover:bg-emerald-600/20 hover:text-emerald-300 transition-colors ${
                      entityFilter === ent ? 'text-emerald-400 font-bold bg-emerald-500/10' : 'text-slate-300'
                    }`}
                  >
                    <span className="truncate">{ent}</span>
                    {entityFilter === ent && <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />}
                  </button>
                ))}
              </div>
            )}
          </div>

          {(actionFilter || entityFilter) && (
            <button
              onClick={handleClearFilters}
              className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors flex items-center gap-1 text-[11px]"
              title="Clear Filters"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Clear
            </button>
          )}
          <button
            onClick={fetchLogs}
            className="p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors flex items-center gap-1 font-semibold"
            title="Refresh Audit Logs"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </button>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        {loading ? (
          <div className="flex justify-center items-center h-48">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
          </div>
        ) : filteredLogs.length > 0 ? (
          <>
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
                    <th className="pb-3 px-3 text-right">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {paginatedLogs.map((log) => {
                    const oldStr = formatLogValue(log.old_value);
                    const newStr = formatLogValue(log.new_value);
                    return (
                      <tr key={log.audit_id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-3 px-3 font-mono text-xs text-slate-400 whitespace-nowrap">
                          {log.created_at ? new Date(log.created_at).toLocaleString() : '-'}
                        </td>
                        <td className="py-3 px-3 font-bold text-indigo-400">{formatLogValue(log.action)}</td>
                        <td className="py-3 px-3 text-slate-300">{formatLogValue(log.entity_type)}</td>
                        <td className="py-3 px-3 font-mono text-xs text-slate-400">#{formatLogValue(log.entity_id)}</td>
                        <td className="py-3 px-3 text-xs text-rose-400 font-mono truncate max-w-xs" title={oldStr}>
                          {oldStr}
                        </td>
                        <td className="py-3 px-3 text-xs text-emerald-400 font-mono truncate max-w-xs" title={newStr}>
                          {newStr}
                        </td>
                        <td className="py-3 px-3 text-xs font-mono text-slate-500">{formatLogValue(log.ip_address) || '127.0.0.1'}</td>
                        <td className="py-3 px-3 text-right">
                          <button
                            onClick={() => setSelectedLog(log)}
                            className="p-1.5 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
                            title="View Log Details"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800 text-xs">
              <div className="text-slate-400">
                Showing <span className="font-semibold text-slate-200">{startIndex + 1}</span> to{' '}
                <span className="font-semibold text-slate-200">{Math.min(startIndex + itemsPerPage, filteredLogs.length)}</span> of{' '}
                <span className="font-semibold text-slate-200">{filteredLogs.length}</span> entries
              </div>

              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800 text-slate-200 rounded-lg transition-colors flex items-center gap-1 font-medium"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  Previous
                </button>

                {getPageNumbers().map((pageNum, idx) => (
                  <React.Fragment key={idx}>
                    {typeof pageNum === 'number' ? (
                      <button
                        onClick={() => setCurrentPage(pageNum)}
                        className={`w-7 h-7 rounded-lg transition-all font-semibold ${
                          currentPage === pageNum
                            ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                            : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                        }`}
                      >
                        {pageNum}
                      </button>
                    ) : (
                      <span className="px-1 text-slate-500">...</span>
                    )}
                  </React.Fragment>
                ))}

                <button
                  onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800 text-slate-200 rounded-lg transition-colors flex items-center gap-1 font-medium"
                >
                  Next
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-12 text-slate-500 text-xs flex flex-col items-center gap-2">
            <div>No audit log records found for action "{actionFilter}" and entity "{entityFilter}".</div>
            {(actionFilter || entityFilter) && (
              <button
                onClick={handleClearFilters}
                className="mt-2 px-3 py-1.5 bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600/30 border border-indigo-500/30 rounded-lg text-xs transition-colors"
              >
                Clear Search Filters
              </button>
            )}
          </div>
        )}
      </div>

      {/* Detail JSON Modal */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-indigo-400" />
                <h3 className="text-base font-bold text-white">
                  Audit Log #{selectedLog.audit_id} - Details
                </h3>
              </div>
              <button
                onClick={() => setSelectedLog(null)}
                className="p-1 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-4 bg-slate-950 p-4 rounded-xl border border-slate-800">
                <div>
                  <span className="text-slate-400 block text-[11px]">Action</span>
                  <span className="font-bold text-indigo-400 text-sm">{formatLogValue(selectedLog.action)}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Entity Type</span>
                  <span className="font-semibold text-slate-200">{formatLogValue(selectedLog.entity_type)}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Entity ID</span>
                  <span className="font-mono text-slate-300">#{formatLogValue(selectedLog.entity_id)}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Timestamp</span>
                  <span className="font-mono text-slate-300">{selectedLog.created_at ? new Date(selectedLog.created_at).toLocaleString() : '-'}</span>
                </div>
              </div>

              <div>
                <h4 className="text-rose-400 font-semibold mb-1">Old State Payload</h4>
                <pre className="bg-slate-950 border border-slate-800 p-3 rounded-xl font-mono text-rose-300 overflow-x-auto text-[11px]">
                  {formatPrettyJson(selectedLog.old_value)}
                </pre>
              </div>

              <div>
                <h4 className="text-emerald-400 font-semibold mb-1">New State Payload</h4>
                <pre className="bg-slate-950 border border-slate-800 p-3 rounded-xl font-mono text-emerald-300 overflow-x-auto text-[11px]">
                  {formatPrettyJson(selectedLog.new_value)}
                </pre>
              </div>
            </div>

            <div className="p-4 border-t border-slate-800 flex justify-end bg-slate-950">
              <button
                onClick={() => setSelectedLog(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white font-medium rounded-xl text-xs transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
