import React, { useState, useEffect } from 'react';
import {
  Users,
  Bot,
  Zap,
  CheckCircle2,
  AlertTriangle,
  Play,
  RefreshCw,
  Sparkles,
  TrendingUp,
  DollarSign,
  ShieldAlert,
  Utensils,
  Layers,
  History,
  Cpu,
  GitMerge,
  Award,
} from 'lucide-react';
import { apiService } from '../services/api';
import { useHotel } from '../context/HotelContext';

export const AgentSwarmArchitecture: React.FC = () => {
  const { selectedHotel } = useHotel();
  const hotelId = selectedHotel?.hotel_id || (selectedHotel as any)?.id || 1;

  const [activeTab, setActiveTab] = useState<'live_eval' | 'history' | 'members'>('live_eval');
  const [loading, setLoading] = useState<boolean>(true);

  // Swarm states
  const [members, setMembers] = useState<any[]>([]);
  const [sessions, setSessions] = useState<any[]>([]);
  const [evaluating, setEvaluating] = useState<boolean>(false);
  const [activeSession, setActiveSession] = useState<any>(null);

  // Form states
  const [topicInput, setTopicInput] = useState<string>('Weekend Dynamic BAR Pricing & MLOS Restriction Alignment');

  useEffect(() => {
    fetchSwarmData();
  }, [hotelId]);

  const fetchSwarmData = async () => {
    try {
      setLoading(true);
      const [membersData, sessionsData] = await Promise.all([
        apiService.getSwarmMembers(hotelId),
        apiService.getSwarmSessions(hotelId),
      ]);
      setMembers(membersData || []);
      setSessions(sessionsData || []);

      if (sessionsData && sessionsData.length > 0 && !activeSession) {
        setActiveSession(sessionsData[0]);
      }
    } catch (err) {
      console.error('Failed to fetch swarm data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunSwarmEval = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setEvaluating(true);
      const res = await apiService.evaluateSwarmConsensus(hotelId, {
        hotel_id: hotelId,
        topic: topicInput,
      });
      setActiveSession(res);
      fetchSwarmData();
    } catch (err) {
      console.error('Error running swarm evaluation:', err);
    } finally {
      setEvaluating(false);
    }
  };

  const getAgentIcon = (code: string) => {
    switch (code) {
      case 'PRICING_AGENT':
        return <DollarSign className="w-5 h-5 text-indigo-400" />;
      case 'DEMAND_AGENT':
        return <TrendingUp className="w-5 h-5 text-emerald-400" />;
      case 'COMPETE_AGENT':
        return <ShieldAlert className="w-5 h-5 text-amber-400" />;
      case 'DISPLACEMENT_AGENT':
        return <Users className="w-5 h-5 text-rose-400" />;
      default:
        return <Utensils className="w-5 h-5 text-purple-400" />;
    }
  };

  return (
    <div className="space-y-6 font-sans">
      {/* Page Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-2 border-b border-slate-800/60">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-3 tracking-tight">
            <Cpu className="w-7 h-7 text-purple-400 flex-shrink-0 animate-pulse-subtle" />
            <span>Multi-Agent Collaborative Swarm Architecture</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            5 specialized AI sub-agents working in a synchronized consensus swarm to optimize pricing, forecast demand, and resolve strategy conflicts.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-1.5 rounded-xl flex-shrink-0">
          <button
            onClick={() => setActiveTab('live_eval')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'live_eval'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            <GitMerge className="w-4 h-4" />
            <span>Live Swarm Consensus</span>
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'history'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            <History className="w-4 h-4" />
            <span>Consensus History ({sessions.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('members')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'members'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            <Bot className="w-4 h-4" />
            <span>Swarm Sub-Agents ({members.length})</span>
          </button>
          <button
            onClick={fetchSwarmData}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors ml-1"
            title="Refresh Swarm Data"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Top Swarm KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-xs font-medium">Active Sub-Agent Swarm</p>
            <p className="text-2xl font-extrabold text-white mt-1">{members.length} AI Agents</p>
            <span className="text-[11px] text-emerald-400 flex items-center gap-1 mt-1">
              <CheckCircle2 className="w-3 h-3" /> 100% Synchronized
            </span>
          </div>
          <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-xl text-purple-400">
            <Bot className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-xs font-medium">Swarm Consensus Accuracy</p>
            <p className="text-2xl font-extrabold text-emerald-400 mt-1">95.8%</p>
            <span className="text-[11px] text-emerald-400 flex items-center gap-1 mt-1">
              <Award className="w-3 h-3" /> High-Confidence Voting
            </span>
          </div>
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400">
            <Award className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-xs font-medium">Conflict Resolution Rate</p>
            <p className="text-2xl font-extrabold text-indigo-300 mt-1">100%</p>
            <span className="text-[11px] text-indigo-400 flex items-center gap-1 mt-1">
              <GitMerge className="w-3 h-3" /> Weighted Voting Synthesis
            </span>
          </div>
          <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl text-indigo-400">
            <GitMerge className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-xs font-medium">Consensus Evaluations Run</p>
            <p className="text-2xl font-extrabold text-amber-300 mt-1">{sessions.length}</p>
            <span className="text-[11px] text-amber-400 flex items-center gap-1 mt-1">
              <Zap className="w-3 h-3" /> Auto-Executed Strategy
            </span>
          </div>
          <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-400">
            <Zap className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* 5 SUB-AGENTS QUICK GRID */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {members.map((m) => (
          <div key={m.agent_id} className="bg-slate-900/90 border border-slate-800/80 rounded-2xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <div className="p-2 bg-slate-950 border border-slate-800 rounded-xl">
                {getAgentIcon(m.agent_code)}
              </div>
              <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-bold rounded-full">
                {m.status}
              </span>
            </div>
            <div>
              <h4 className="text-xs font-bold text-white leading-tight">{m.agent_name}</h4>
              <p className="text-[11px] text-slate-400 mt-0.5">{m.specialization}</p>
            </div>
            <div className="flex items-center justify-between text-[11px] text-slate-500 border-t border-slate-800/60 pt-2 font-mono">
              <span>Accuracy: <strong className="text-emerald-400">{m.accuracy_rating_pct}%</strong></span>
              <span>Weight: <strong className="text-purple-300">{m.voting_weight}x</strong></span>
            </div>
          </div>
        ))}
      </div>

      {/* TAB 1: LIVE SWARM CONSENSUS ENGINE */}
      {activeTab === 'live_eval' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Form Trigger */}
          <div className="lg:col-span-5 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <GitMerge className="w-5 h-5 text-purple-400" />
              Trigger Swarm Consensus Session
            </h2>
            <p className="text-xs text-slate-400">
              Run a joint multi-agent evaluation across Pricing, Demand, Compete, Displacement, and TRevPAR sub-agents to synthesize an optimal revenue decision.
            </p>

            <form onSubmit={handleRunSwarmEval} className="space-y-4 pt-2">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Target Evaluation Topic</label>
                <textarea
                  value={topicInput}
                  onChange={(e) => setTopicInput(e.target.value)}
                  rows={3}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white focus:border-purple-500 focus:outline-none leading-relaxed"
                  placeholder="e.g. Evaluate rate increase to ₹8,950 for upcoming weekend..."
                />
              </div>

              <button
                type="submit"
                disabled={evaluating}
                className="w-full py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-purple-600/30 transition-all flex items-center justify-center gap-2 cursor-pointer"
              >
                {evaluating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-white" />}
                <span>Run 5-Agent Collaborative Evaluation</span>
              </button>
            </form>
          </div>

          {/* Live Swarm Consensus Output Render */}
          <div className="lg:col-span-7 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-purple-400" />
                  <h3 className="text-sm font-bold text-white">Synthesized Swarm Decision</h3>
                </div>
                {activeSession && (
                  <span className="px-3 py-1 bg-purple-500/20 text-purple-300 border border-purple-500/30 text-xs font-extrabold rounded-full font-mono">
                    {activeSession.overall_confidence_pct}% Confidence Score
                  </span>
                )}
              </div>

              {/* Sub-Agent Individual Votes Grid */}
              <div className="mt-4 space-y-3">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Individual Sub-Agent Votes & Rationales</h4>

                <div className="space-y-2.5 max-h-[320px] overflow-y-auto pr-1">
                  {activeSession?.agent_votes_json?.map((vote: any, idx: number) => (
                    <div key={idx} className="bg-slate-950 border border-slate-800/80 rounded-xl p-3 space-y-1.5 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-white flex items-center gap-2">
                          <Bot className="w-3.5 h-3.5 text-purple-400" />
                          {vote.agent_name}
                        </span>
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-0.5 rounded font-extrabold text-[10px] ${
                              vote.vote_decision === 'APPROVE'
                                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                                : vote.vote_decision === 'COUNTER_PROPOSE'
                                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                                : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                            }`}
                          >
                            {vote.vote_decision}
                          </span>
                          <span className="text-[11px] text-slate-400 font-mono">{vote.confidence_pct}%</span>
                        </div>
                      </div>
                      <p className="text-slate-300 leading-relaxed text-[11px]">{vote.reasoning}</p>
                      <span className="text-[10px] text-indigo-300 font-mono">
                        Proposal: <strong>{vote.proposed_value}</strong>
                      </span>
                    </div>
                  ))}
                </div>

                {/* Synthesis Rationale Card */}
                {activeSession?.synthesis_rationale && (
                  <div className="p-3 bg-purple-950/30 border border-purple-500/30 rounded-xl text-xs text-purple-200 leading-relaxed">
                    <strong className="text-white block mb-1">Final Swarm Orchestrator Consensus:</strong>
                    {activeSession.synthesis_rationale}
                  </div>
                )}
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
              <span>Status: <strong className="text-emerald-400 font-semibold">{activeSession?.status || 'EXECUTED'}</strong></span>
              <span>Evaluated: {activeSession?.created_at ? new Date(activeSession.created_at).toLocaleString() : 'Just now'}</span>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: CONSENSUS SESSION HISTORY */}
      {activeTab === 'history' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <History className="w-4 h-4 text-purple-400" />
              Multi-Agent Swarm Decision History Audit Log
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
                <tr>
                  <th className="p-3">Evaluation Topic</th>
                  <th className="p-3">Proposed Action</th>
                  <th className="p-3 text-center">Confidence Score</th>
                  <th className="p-3 text-center">Conflict Status</th>
                  <th className="p-3 text-right">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {sessions.map((s) => (
                  <tr
                    key={s.session_id}
                    onClick={() => {
                      setActiveSession(s);
                      setActiveTab('live_eval');
                    }}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="p-3 text-white font-bold max-w-[280px] truncate">{s.consensus_topic}</td>
                    <td className="p-3 font-mono text-indigo-300">{s.proposed_action}</td>
                    <td className="p-3 text-center font-extrabold text-purple-300 font-mono">{s.overall_confidence_pct}%</td>
                    <td className="p-3 text-center">
                      {s.conflict_detected ? (
                        <span className="px-2 py-0.5 bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded text-[10px] font-bold">
                          RESOLVED CONFLICT
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded text-[10px] font-bold">
                          UNANIMOUS
                        </span>
                      )}
                    </td>
                    <td className="p-3 text-right text-slate-400 font-mono text-[11px]">
                      {new Date(s.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: SUB-AGENTS DETAILS */}
      {activeTab === 'members' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {members.map((m) => (
            <div key={m.agent_id} className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-2 bg-slate-950 border border-slate-800 rounded-xl">
                    {getAgentIcon(m.agent_code)}
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">{m.agent_name}</h3>
                    <p className="text-xs text-indigo-400 font-medium">{m.specialization}</p>
                  </div>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">{m.role_description}</p>

              <div className="grid grid-cols-3 gap-2 bg-slate-950 p-2.5 rounded-xl border border-slate-800/80 text-center text-xs font-mono">
                <div>
                  <span className="text-[10px] text-slate-500 block">Voting Weight</span>
                  <strong className="text-purple-300">{m.voting_weight}x</strong>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 block">Accuracy Rating</span>
                  <strong className="text-emerald-400">{m.accuracy_rating_pct}%</strong>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 block">Proposals</span>
                  <strong className="text-white">{m.total_proposals}</strong>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
