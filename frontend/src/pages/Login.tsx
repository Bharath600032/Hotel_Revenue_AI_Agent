import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { Sparkles, ArrowRight, Lock, Mail, ShieldCheck, UserCheck, LogOut } from 'lucide-react';

export const Login: React.FC = () => {
  const { login, logout, user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('admin@revenueagent.ai');
  const [password, setPassword] = useState('Admin123!Pass');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeRole, setActiveRole] = useState<'admin' | 'manager' | 'analyst'>('admin');

  useEffect(() => {
    if (location.search.includes('expired=true')) {
      setError('Your security session expired. Please log in again to continue.');
    }
  }, [location]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/', { replace: true });
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Authentication failed. Please verify backend connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectRole = (role: 'admin' | 'manager' | 'analyst', roleEmail: string, rolePass: string) => {
    setActiveRole(role);
    setEmail(roleEmail);
    setPassword(rolePass);
    setError('');
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 relative overflow-hidden font-sans">
      {/* Background Radial Glow & Mesh Gradients */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-600/20 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute bottom-10 right-10 w-96 h-96 bg-emerald-600/15 rounded-full blur-[120px] pointer-events-none" />

      {/* Main Glass Card Container */}
      <div className="w-full max-w-md bg-slate-900/90 backdrop-blur-2xl border border-slate-800 rounded-3xl p-8 shadow-2xl shadow-slate-950 space-y-6 relative z-10">
        
        {/* Brand Header */}
        <div className="text-center space-y-3">
          <div className="inline-flex p-3.5 bg-gradient-to-tr from-indigo-600 to-indigo-500 border border-indigo-400/30 rounded-2xl shadow-xl shadow-indigo-600/30 mb-1">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <div className="space-y-1">
            <h1 className="text-2xl font-extrabold text-white tracking-tight">Hotel Autonomous Revenue AI</h1>
            <p className="text-xs text-slate-400 font-medium">Enterprise Autonomous Revenue & Rate Management Platform</p>
          </div>
          <div className="pt-1">
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-full text-[11px] font-bold">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Guardrails & Live Rate Automation</span>
            </span>
          </div>
        </div>

        {/* If Already Authenticated Banner */}
        {isAuthenticated ? (
          <div className="p-5 bg-indigo-950/60 border border-indigo-500/30 rounded-2xl space-y-3">
            <div className="flex items-center space-x-2 text-emerald-400 text-xs font-bold">
              <UserCheck className="w-4 h-4" />
              <span>Session Active: Logged in as {user?.full_name || 'Admin'}</span>
            </div>
            <p className="text-xs text-slate-300">
              Account: <strong className="text-white font-mono">{user?.email || 'admin@revenueagent.ai'}</strong> ({user?.role || 'Administrator'})
            </p>
            <div className="flex gap-2 pt-2">
              <button
                onClick={() => navigate('/')}
                className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-1.5 transition-all"
              >
                <span>Go to Dashboard</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={logout}
                className="py-2.5 px-3 bg-slate-800 hover:bg-rose-600 text-slate-300 hover:text-white font-bold text-xs rounded-xl flex items-center justify-center gap-1.5 transition-all border border-slate-700"
                title="Sign Out to switch accounts"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Sign Out</span>
              </button>
            </div>
          </div>
        ) : (
          <>
            {error && (
              <div className="p-3.5 bg-rose-500/10 border border-rose-500/30 rounded-2xl text-rose-400 text-xs font-semibold flex items-start gap-2">
                <span>⚠️</span>
                <span>{error}</span>
              </div>
            )}

            {/* Credentials Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="block text-[11px] font-bold text-slate-300 uppercase tracking-wider">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-mono"
                    placeholder="admin@revenueagent.ai"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="block text-[11px] font-bold text-slate-300 uppercase tracking-wider">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-mono"
                    placeholder="••••••••••••"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-bold py-3 px-4 rounded-xl shadow-xl shadow-indigo-600/30 flex items-center justify-center space-x-2 transition-all disabled:opacity-50 mt-4 group"
              >
                <span className="text-xs">{loading ? 'Authenticating Credentials...' : 'Sign In to Dashboard'}</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
              </button>
            </form>

            {/* Demo Credentials Quick-Select Section */}
            <div className="pt-4 border-t border-slate-800/80 text-center space-y-3">
              <p className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider">
                One-Click Demo Account Quick Select:
              </p>
              <div className="grid grid-cols-4 gap-1.5">
                <button
                  type="button"
                  onClick={() => handleSelectRole('admin', 'superadmin@cuteorange.in', 'SuperAdmin123!')}
                  className={`px-2 py-2 rounded-xl text-xs font-semibold flex flex-col items-center justify-center space-y-1 transition-all border ${
                    email === 'superadmin@cuteorange.in'
                      ? 'bg-purple-600/20 border-purple-500 text-purple-300 shadow-md shadow-purple-600/20'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <span>Super Admin</span>
                  <span className="text-[9px] font-mono text-purple-400">Global</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleSelectRole('admin', 'admin@revenueagent.ai', 'Admin123!Pass')}
                  className={`px-2 py-2 rounded-xl text-xs font-semibold flex flex-col items-center justify-center space-y-1 transition-all border ${
                    activeRole === 'admin' && email !== 'superadmin@cuteorange.in'
                      ? 'bg-indigo-600/20 border-indigo-500 text-indigo-300 shadow-md shadow-indigo-600/20'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <span>Admin</span>
                  <span className="text-[9px] font-mono text-slate-500">Full Access</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleSelectRole('manager', 'manager@revenueagent.ai', 'Manager123!Pass')}
                  className={`px-2 py-2 rounded-xl text-xs font-semibold flex flex-col items-center justify-center space-y-1 transition-all border ${
                    activeRole === 'manager'
                      ? 'bg-emerald-600/20 border-emerald-500 text-emerald-300 shadow-md shadow-emerald-600/20'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <span>Manager</span>
                  <span className="text-[9px] font-mono text-slate-500">Approvals</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleSelectRole('analyst', 'analyst@revenueagent.ai', 'Analyst123!Pass')}
                  className={`px-2 py-2 rounded-xl text-xs font-semibold flex flex-col items-center justify-center space-y-1 transition-all border ${
                    activeRole === 'analyst'
                      ? 'bg-cyan-600/20 border-cyan-500 text-cyan-300 shadow-md shadow-cyan-600/20'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <span>Analyst</span>
                  <span className="text-[9px] font-mono text-slate-500">Read-Only</span>
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Footer System Status Badge */}
      <div className="mt-8 text-center text-xs text-slate-500 font-mono">
        Autonomous Revenue AI Platform &bull; Status: <span className="text-emerald-400 font-bold">Online</span>
      </div>
    </div>
  );
};



