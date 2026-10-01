import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { AgentChatResponse, PriceRecommendation } from '../types';
import { Bot, Send, User as UserIcon, CheckCircle2, XCircle, Edit3, Sparkles, ShieldAlert, Cpu, Zap, PlusCircle, MessageSquare, Trash2 } from 'lucide-react';
import { useHotel } from '../context/HotelContext';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  recommendation?: PriceRecommendation;
  factors?: string[];
  tools_used?: { tool_name: string; execution_time_ms: number }[];
  requires_approval?: boolean;
}

interface ChatSession {
  id: string;
  title: string;
  createdAt: string;
  messages: ChatMessage[];
}

export const Assistant: React.FC = () => {
  const { selectedHotel } = useHotel();
  const activeHotelId = selectedHotel?.hotel_id || 1;

  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>('');
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const defaultGreeting: ChatMessage = {
    id: `init_${Date.now()}`,
    sender: 'assistant',
    content: `Hello! I am KESH, your Dedicated Revenue AI Agent for ${selectedHotel?.hotel_name || 'your property'}. I monitor live demand signals, competitor rate parity, and occupancy forecasts. Ask me for rate recommendations, room categories, total rooms count, or revenue analysis!`,
  };

  // Restore sessions per hotel from localStorage
  useEffect(() => {
    const storageKey = `hotel_chat_sessions_v2_${activeHotelId}`;
    const saved = localStorage.getItem(storageKey);
    let loadedSessions: ChatSession[] = [];

    if (saved) {
      try {
        loadedSessions = JSON.parse(saved);
      } catch (e) {
        console.error('Failed to parse saved chat sessions:', e);
      }
    }

    if (!Array.isArray(loadedSessions) || loadedSessions.length === 0) {
      const initId = `sess_${Date.now()}`;
      loadedSessions = [
        {
          id: initId,
          title: 'Current Conversation',
          createdAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          messages: [defaultGreeting],
        },
      ];
    }

    setSessions(loadedSessions);
    setActiveSessionId(loadedSessions[0].id);
  }, [activeHotelId, selectedHotel?.hotel_name]);

  // Persist sessions per hotel whenever updated
  useEffect(() => {
    if (activeHotelId && sessions.length > 0) {
      const storageKey = `hotel_chat_sessions_v2_${activeHotelId}`;
      localStorage.setItem(storageKey, JSON.stringify(sessions));
    }
  }, [sessions, activeHotelId]);

  const activeSession = sessions.find((s) => s.id === activeSessionId) || sessions[0];
  const messages = activeSession ? activeSession.messages : [defaultGreeting];

  const handleNewChat = () => {
    const newId = `sess_${Date.now()}`;
    const newSession: ChatSession = {
      id: newId,
      title: `Chat ${sessions.length + 1}`,
      createdAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      messages: [
        {
          id: `init_${Date.now()}`,
          sender: 'assistant',
          content: `Hello! I am KESH, your Dedicated Revenue AI Agent for ${selectedHotel?.hotel_name || 'your property'}. Ready for a new conversation!`,
        },
      ],
    };

    setSessions((prev) => [newSession, ...prev]);
    setActiveSessionId(newId);
  };

  const handleDeleteSession = (sessionId: string) => {
    if (sessions.length <= 1) {
      handleNewChat();
      return;
    }
    const filtered = sessions.filter((s) => s.id !== sessionId);
    setSessions(filtered);
    if (activeSessionId === sessionId && filtered.length > 0) {
      setActiveSessionId(filtered[0].id);
    }
  };

  const samplePrompts = [
    'Total rooms in this hotel',
    'Recommend rate for Deluxe Ocean View on Oct 20',
    'List out room names and baseline rates',
    'Analyze competitor price gap for Goa property',
    'Show 30-day demand forecast & occupancy pace',
  ];

  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || inputMessage.trim();
    if (!query || loading || !activeSessionId) return;

    setInputMessage('');
    const userMsgId = `user_${Date.now()}`;
    const newMsg: ChatMessage = { id: userMsgId, sender: 'user', content: query };

    setSessions((prev) =>
      prev.map((s) => {
        if (s.id === activeSessionId) {
          const updatedMsgs = [...s.messages, newMsg];
          const newTitle = s.messages.length <= 1 ? (query.length > 25 ? query.substring(0, 25) + '...' : query) : s.title;
          return { ...s, title: newTitle, messages: updatedMsgs };
        }
        return s;
      })
    );

    setLoading(true);

    try {
      const res: AgentChatResponse = await apiService.sendAgentChat(activeHotelId, query);
      const assistantMsgId = `asst_${Date.now()}`;
      const asstMsg: ChatMessage = {
        id: assistantMsgId,
        sender: 'assistant',
        content: res.answer,
        recommendation: res.recommendation ? (res.recommendation as PriceRecommendation) : undefined,
        factors: res.factors,
        tools_used: res.tools_used,
        requires_approval: res.requires_approval,
      };

      setSessions((prev) =>
        prev.map((s) => (s.id === activeSessionId ? { ...s, messages: [...s.messages, asstMsg] } : s))
      );
    } catch (err: any) {
      const errMsg: ChatMessage = {
        id: `err_${Date.now()}`,
        sender: 'assistant',
        content: 'An error occurred while communicating with KESH. Please verify backend server state.',
      };
      setSessions((prev) =>
        prev.map((s) => (s.id === activeSessionId ? { ...s, messages: [...s.messages, errMsg] } : s))
      );
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="h-[calc(100vh-7.5rem)] flex flex-col bg-slate-900/80 backdrop-blur border border-slate-800 rounded-3xl overflow-hidden shadow-2xl font-sans">
      {/* Header Bar */}
      <div className="p-4 bg-slate-950/90 border-b border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-gradient-to-tr from-indigo-600 to-indigo-500 rounded-2xl shadow-lg shadow-indigo-600/30">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-extrabold text-white flex items-center gap-2">
              KESH — Autonomous Revenue AI Assistant
              <span className="px-2 py-0.5 bg-indigo-500/20 text-indigo-300 text-[10px] font-bold rounded-full border border-indigo-500/30">
                AI Agent: KESH
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">Dedicated AI Agent for {selectedHotel?.hotel_name || 'Cute Orange Hotel'}</p>
          </div>
        </div>

        {/* Multi-Session Selector & New Chat Button */}
        <div className="flex items-center space-x-2">
          {/* Chat Sessions Selector */}
          <div className="relative flex items-center">
            <MessageSquare className="w-3.5 h-3.5 text-indigo-400 absolute left-3 pointer-events-none" />
            <select
              value={activeSessionId}
              onChange={(e) => setActiveSessionId(e.target.value)}
              className="bg-slate-900 border border-slate-800 text-xs text-slate-200 font-medium rounded-xl pl-8 pr-3 py-1.5 focus:border-indigo-500 outline-none max-w-[180px] truncate"
            >
              {sessions.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.title} ({s.createdAt})
                </option>
              ))}
            </select>
          </div>

          {/* New Chat Button */}
          <button
            onClick={handleNewChat}
            className="px-3.5 py-1.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-xs rounded-xl flex items-center space-x-1.5 transition-all shadow-md shadow-indigo-600/30 hover:scale-[1.02]"
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Chat</span>
          </button>

          {/* Delete Active Session */}
          {activeSessionId && (
            <button
              onClick={() => handleDeleteSession(activeSessionId)}
              title="Delete current conversation thread"
              className="p-1.5 bg-slate-900 hover:bg-rose-900/40 text-slate-400 hover:text-rose-400 border border-slate-800 rounded-xl transition-all"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}

          <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-bold rounded-full border border-emerald-500/20 hidden lg:flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5" />
            22 Tools Ready
          </span>
        </div>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 p-6 overflow-y-auto space-y-6">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start space-x-3 ${msg.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}
          >
            <div
              className={`p-2.5 rounded-2xl flex-shrink-0 shadow-md ${
                msg.sender === 'user'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-800 text-indigo-400 border border-slate-700/80'
              }`}
            >
              {msg.sender === 'user' ? <UserIcon className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div className={`max-w-2xl space-y-3 ${msg.sender === 'user' ? 'items-end' : ''}`}>
              <div
                className={`p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-indigo-600 text-white rounded-tr-none shadow-lg'
                    : 'bg-slate-950/90 border border-slate-800 text-slate-200 rounded-tl-none shadow-md'
                }`}
              >
                <div className="whitespace-pre-wrap font-medium">{msg.content}</div>
              </div>

              {/* Structured Recommendation Card */}
              {msg.recommendation && (
                <div className="bg-slate-950 border border-indigo-500/30 rounded-3xl p-5 space-y-4 shadow-2xl">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
                    <div className="flex items-center space-x-2">
                      <Sparkles className="w-4 h-4 text-amber-400" />
                      <span className="text-xs font-bold text-white uppercase tracking-wider">
                        Rate Recommendation: {msg.recommendation.stay_date}
                      </span>
                    </div>
                    {msg.requires_approval && (
                      <span className="px-2.5 py-0.5 bg-amber-500/10 text-amber-400 text-xs font-bold rounded-full border border-amber-500/20 flex items-center space-x-1">
                        <ShieldAlert className="w-3 h-3" />
                        <span>Approval Required</span>
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="p-3 bg-slate-900/90 rounded-2xl border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase font-bold">Recommended Rate</span>
                      <p className="text-lg font-extrabold text-emerald-400">₹{msg.recommendation.recommended_rate?.toLocaleString()}</p>
                    </div>
                    <div className="p-3 bg-slate-900/90 rounded-2xl border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase font-bold">Current Base</span>
                      <p className="text-lg font-extrabold text-slate-300">₹{msg.recommendation.current_rate?.toLocaleString()}</p>
                    </div>
                    <div className="p-3 bg-slate-900/90 rounded-2xl border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase font-bold">Competitor Median</span>
                      <p className="text-lg font-extrabold text-indigo-400">₹{msg.recommendation.competitor_median?.toLocaleString()}</p>
                    </div>
                    <div className="p-3 bg-slate-900/90 rounded-2xl border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase font-bold">Confidence</span>
                      <p className="text-lg font-extrabold text-cyan-400">{Math.round((msg.recommendation.confidence_score || 0.88) * 100)}%</p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-2 pt-1">
                    <button className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl flex items-center space-x-1.5 transition-all shadow-md shadow-emerald-600/20">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Approve Rate</span>
                    </button>
                    <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs rounded-xl flex items-center space-x-1.5 transition-all border border-slate-700">
                      <Edit3 className="w-4 h-4" />
                      <span>Modify</span>
                    </button>
                    <button className="px-4 py-2 bg-slate-800 hover:bg-rose-900/40 text-rose-400 font-bold text-xs rounded-xl flex items-center space-x-1.5 transition-all border border-slate-700">
                      <XCircle className="w-4 h-4" />
                      <span>Reject</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Tools Executed Drawer */}
              {msg.tools_used && msg.tools_used.length > 0 && (
                <div className="text-[10px] text-slate-400 flex items-center space-x-2 font-mono pt-1">
                  <Cpu className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Tools Executed:</span>
                  {msg.tools_used.map((t, idx) => (
                    <span key={idx} className="px-2 py-0.5 bg-slate-950 text-indigo-300 rounded-lg border border-slate-800">
                      {t.tool_name} ({t.execution_time_ms}ms)
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-3 text-slate-400 text-xs font-mono">
            <Bot className="w-4 h-4 animate-spin text-indigo-400" />
            <span>KESH is analyzing demand signals, forecasts, and competitor rates...</span>
          </div>
        )}

      </div>

      {/* Quick Prompt Suggestions */}
      <div className="px-6 py-2 bg-slate-950/60 border-t border-slate-800/60 flex items-center gap-2 overflow-x-auto">
        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider flex-shrink-0">Suggestions:</span>
        {samplePrompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => handleSendMessage(p)}
            className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 text-slate-300 text-[11px] font-semibold rounded-full border border-slate-800 transition-colors whitespace-nowrap flex-shrink-0"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }} className="p-4 bg-slate-950 border-t border-slate-800/80 flex space-x-3">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSendMessage();
            }
          }}
          placeholder="Ask KESH e.g. 'Total rooms in this hotel' or 'Recommend rate for Deluxe Room'..."
          className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl px-4 py-3 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
        />
        <button
          type="submit"
          disabled={loading || !inputMessage.trim()}
          className="px-5 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-2xl flex items-center space-x-2 transition-all disabled:opacity-50 shadow-lg shadow-indigo-600/30"
        >
          <span className="text-xs">Send</span>
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};


