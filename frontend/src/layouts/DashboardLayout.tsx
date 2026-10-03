import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useHotel } from '../context/HotelContext';
import {
  LayoutDashboard,
  Building2,
  TrendingUp,
  LineChart,
  DollarSign,
  Users2,
  Calendar,
  Bot,
  FileSpreadsheet,
  BookOpen,
  History,
  Settings,
  LogOut,
  Sparkles,
  Search,
  Bell,
  PanelLeftClose,
  PanelLeftOpen,
  ChevronRight,
  User as UserIcon,
  CheckCircle2,
  Command,
  Sun,
  Moon,
  ChevronDown,
} from 'lucide-react';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const { hotels, selectedHotel, setSelectedHotel } = useHotel();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showHotelDropdown, setShowHotelDropdown] = useState(false);

  const notificationRef = React.useRef<HTMLDivElement>(null);
  const userMenuRef = React.useRef<HTMLDivElement>(null);
  const hotelDropdownRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
      if (hotelDropdownRef.current && !hotelDropdownRef.current.contains(event.target as Node)) {
        setShowHotelDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const navCategories = [
    {
      title: 'OVERVIEW',
      items: [
        { label: 'Dashboard', icon: LayoutDashboard, path: '/' },
        { label: 'Hotels & Inventory', icon: Building2, path: '/hotels' },
      ],
    },
    {
      title: 'REVENUE & PRICING',
      items: [
        { label: 'Revenue Analytics', icon: TrendingUp, path: '/revenue' },
        { label: 'Demand Forecasting', icon: LineChart, path: '/forecasting' },
        { label: 'Pricing Engine', icon: DollarSign, path: '/pricing', badge: '5' },
        { label: 'Competitor Intelligence', icon: Users2, path: '/competitors' },
        { label: 'Events & Holidays', icon: Calendar, path: '/events' },
      ],
    },
    {
      title: 'INTELLIGENCE & AI',
      items: [
        { label: 'AI Revenue Assistant', icon: Bot, path: '/assistant', badge: 'AI' },
        { label: 'RAG Knowledge Base', icon: BookOpen, path: '/rag' },
      ],
    },
    {
      title: 'SYSTEM & LOGS',
      items: [
        { label: 'User & Role Access', icon: UserIcon, path: '/users', badge: 'ADMIN' },
        { label: 'Reports & Exports', icon: FileSpreadsheet, path: '/reports' },
        { label: 'Audit Compliance', icon: History, path: '/audit' },
        { label: 'Settings', icon: Settings, path: '/settings' },
      ],
    },
  ];

  // Helper to construct dynamic breadcrumb path
  const getBreadcrumbTitle = (path: string) => {
    switch (path) {
      case '/': return 'Overview';
      case '/hotels': return 'Hotels & Inventory';
      case '/revenue': return 'Revenue Analytics';
      case '/forecasting': return 'Demand Forecasting';
      case '/pricing': return 'Pricing Engine & Approvals';
      case '/competitors': return 'Competitor Intelligence';
      case '/events': return 'Events & Holidays';
      case '/assistant': return 'AI Revenue Assistant';
      case '/reports': return 'Reports & Exports';
      case '/rag': return 'RAG Knowledge Base';
      case '/audit': return 'Audit Logs';
      case '/users': return 'User & Role Access Control';
      case '/settings': return 'Settings';
      default: return 'Dashboard';
    }
  };

  return (
    <div className="min-h-screen flex bg-slate-950 text-slate-100 font-sans antialiased selection:bg-indigo-500 selection:text-white">
      {/* Sidebar Navigation */}
      <aside
        className={`${
          collapsed ? 'w-20' : 'w-64'
        } bg-slate-900/95 backdrop-blur-xl border-r border-slate-800/80 flex flex-col justify-between p-3 sticky top-0 h-screen transition-all duration-300 z-30 shadow-2xl`}
      >
        <div className="space-y-6">
          {/* Brand Logo */}
          <div className="flex items-center justify-between px-2 pt-1">
            <Link to="/" className="flex items-center space-x-3 group">
              <div className="p-2 bg-gradient-to-tr from-indigo-600 to-indigo-500 rounded-xl shadow-lg shadow-indigo-600/30 group-hover:scale-105 transition-all">
                <Sparkles className="w-5 h-5 text-white animate-pulse-subtle" />
              </div>
              {!collapsed && (
                <div>
                  <h1 className="text-sm font-bold tracking-tight text-white leading-none group-hover:text-indigo-400 transition-colors">
                    Revenue AI
                  </h1>
                  <span className="text-[10px] text-indigo-400 font-semibold uppercase tracking-wider">Autonomous Agent</span>
                </div>
              )}
            </Link>
          </div>

          {/* Navigation Categories */}
          <nav className="space-y-5 overflow-y-auto max-h-[calc(100vh-180px)] pr-1">
            {navCategories.map((cat, idx) => (
              <div key={idx} className="space-y-1">
                {!collapsed && (
                  <p className="px-3 text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1.5">
                    {cat.title}
                  </p>
                )}
                {cat.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      title={collapsed ? item.label : undefined}
                      className={`flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition-all group ${
                        isActive
                          ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/25 border border-indigo-500/50'
                          : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60 border border-transparent'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <Icon className={`w-4 h-4 transition-transform group-hover:scale-110 ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-indigo-400'}`} />
                        {!collapsed && <span>{item.label}</span>}
                      </div>

                      {!collapsed && item.badge && (
                        <span
                          className={`px-1.5 py-0.5 rounded-full text-[10px] font-extrabold ${
                            item.badge === 'AI'
                              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                              : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          }`}
                        >
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  );
                })}
              </div>
            ))}
          </nav>
        </div>

        {/* User Profile Card & Logout */}
        <div className="pt-3 border-t border-slate-800/80">
          <div className="flex items-center justify-between p-2 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <div className="flex items-center space-x-2.5 min-w-0">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 text-white flex items-center justify-center font-bold text-xs shadow-md">
                {user?.full_name ? user.full_name.charAt(0) : 'A'}
              </div>
              {!collapsed && (
                <div className="truncate">
                  <p className="text-xs font-bold text-white truncate">{user?.full_name || 'Administrator'}</p>
                  <p className="text-[10px] text-indigo-400 font-medium truncate">{user?.role || 'Chief Revenue Officer'}</p>
                </div>
              )}
            </div>
            {!collapsed && (
              <button
                onClick={logout}
                className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                title="Sign Out"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      </aside>

      {/* Main Page Area */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Next-Shadcn Dashboard Header Bar */}
        <header className="h-14 bg-slate-900/80 backdrop-blur-md border-b border-slate-800/80 px-6 flex items-center justify-between sticky top-0 z-20 shadow-sm">
          {/* Left Controls: Sidebar Toggle + Breadcrumb + Hotel Selector */}
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              title="Toggle Sidebar"
            >
              {collapsed ? <PanelLeftOpen className="w-4 h-4" /> : <PanelLeftClose className="w-4 h-4" />}
            </button>

            <div className="h-4 w-px bg-slate-800" />

            {/* Breadcrumb Path */}
            <div className="flex items-center space-x-2 text-xs text-slate-400 font-medium">
              <span>Dashboard</span>
              <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
              <span className="text-white font-bold">{getBreadcrumbTitle(location.pathname)}</span>
            </div>

            {/* Active Property Selector Dropdown */}
            <div className="relative hidden md:block" ref={hotelDropdownRef}>
              <button
                onClick={() => setShowHotelDropdown(!showHotelDropdown)}
                className="flex items-center space-x-2 px-3 py-1.5 bg-slate-950/80 hover:bg-slate-800/80 border border-slate-700/80 rounded-xl text-xs font-bold text-white transition-all shadow-md"
              >
                <div className="p-1 bg-indigo-500/20 rounded-lg text-indigo-400 border border-indigo-500/30">
                  <Building2 className="w-3.5 h-3.5" />
                </div>
                <div className="text-left">
                  <div className="flex items-center gap-1.5">
                    <span className="text-indigo-300 font-mono text-[10px] bg-indigo-500/20 px-1 rounded border border-indigo-500/30">
                      {selectedHotel?.hotel_code || 'HTL'}
                    </span>
                    <span className="truncate max-w-[160px]">{selectedHotel?.hotel_name || 'Select Hotel'}</span>
                  </div>
                </div>
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse ml-1" />
                <ChevronDown className="w-3.5 h-3.5 text-slate-400 ml-1" />
              </button>

              {showHotelDropdown && (
                <div className="absolute left-0 mt-2 w-72 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-2 z-50 space-y-1 animate-fadeIn">
                  <div className="px-3 py-2 border-b border-slate-800 flex items-center justify-between">
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Active Hotel Scope</span>
                    <span className="text-[10px] text-emerald-400 font-mono bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                      {hotels.length} Properties
                    </span>
                  </div>
                  <div className="max-h-60 overflow-y-auto space-y-1">
                    {hotels.map((h) => {
                      const isCurrent = selectedHotel?.hotel_id === h.hotel_id;
                      return (
                        <button
                          key={h.hotel_id}
                          onClick={() => {
                            setSelectedHotel(h);
                            setShowHotelDropdown(false);
                          }}
                          className={`w-full text-left px-3 py-2.5 rounded-xl text-xs font-semibold flex items-center justify-between transition-colors ${
                            isCurrent
                              ? 'bg-indigo-600 text-white font-bold shadow-lg shadow-indigo-600/30'
                              : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                          }`}
                        >
                          <div>
                            <div className="flex items-center gap-1.5">
                              <span className={`text-[10px] font-mono px-1 rounded ${isCurrent ? 'bg-indigo-700 text-white' : 'bg-slate-800 text-indigo-400'}`}>
                                {h.hotel_code}
                              </span>
                              <span>{h.hotel_name}</span>
                              {h.status !== 'ACTIVE' && (
                                <span className="text-[9px] font-extrabold bg-amber-500/20 text-amber-300 border border-amber-500/40 px-1 py-0.2 rounded">
                                  INACTIVE
                                </span>
                              )}
                            </div>
                            <p className={`text-[10px] mt-0.5 ${isCurrent ? 'text-indigo-200' : 'text-slate-400'}`}>
                              📍 {h.city}, {h.country} ({h.total_rooms} Rooms)
                            </p>
                          </div>
                          {isCurrent && <CheckCircle2 className="w-4 h-4 text-white shrink-0" />}
                        </button>
                      );
                    })}
                  </div>
                  <div className="border-t border-slate-800 pt-1">
                    <Link
                      to="/hotels"
                      onClick={() => setShowHotelDropdown(false)}
                      className="block text-center px-2 py-1.5 text-[11px] font-bold text-indigo-400 hover:bg-indigo-500/10 rounded-lg transition-colors"
                    >
                      + Manage Properties & AI Agents
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Controls: Global Search + Notifications + Theme Indicator + Avatar Dropdown */}
          <div className="flex items-center space-x-3">
            {/* Command Search Bar Trigger */}
            <div className="relative hidden lg:block">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search metrics, rates, AI..."
                className="w-64 bg-slate-950/80 border border-slate-800 rounded-xl pl-9 pr-12 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all"
              />
              <div className="absolute right-2 top-1/2 -translate-y-1/2 px-1.5 py-0.5 bg-slate-800 rounded border border-slate-700 text-[10px] text-slate-400 font-mono flex items-center gap-0.5">
                <Command className="w-2.5 h-2.5" /> K
              </div>
            </div>

            {/* Notifications Popover Toggle */}
            <div className="relative" ref={notificationRef}>
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition-colors relative"
                title="Notifications"
              >
                <Bell className="w-4 h-4" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-indigo-500" />
              </button>

              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-4 space-y-3 z-50">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <h4 className="text-xs font-bold text-white">System Notifications</h4>
                    <span className="text-[10px] bg-indigo-500/20 text-indigo-400 px-2 py-0.5 rounded-full font-bold">
                      3 New
                    </span>
                  </div>
                  <div className="space-y-2 text-xs">
                    <div className="p-2 bg-slate-950/60 rounded-xl border border-slate-800">
                      <p className="font-semibold text-emerald-400">Demand Surge Detected</p>
                      <p className="text-[11px] text-slate-400">Sunburn Festival Goa caused +22% pickup increase.</p>
                    </div>
                    <div className="p-2 bg-slate-950/60 rounded-xl border border-slate-800">
                      <p className="font-semibold text-amber-400">Approval Required</p>
                      <p className="text-[11px] text-slate-400">5 price recommendations exceed ±10% threshold.</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* User Profile Avatar Dropdown */}
            <div className="relative" ref={userMenuRef}>
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 p-1 pl-2 hover:bg-slate-800/80 rounded-xl transition-colors border border-slate-800/60"
              >
                <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-indigo-500 to-indigo-600 text-white font-bold text-xs flex items-center justify-center shadow">
                  {user?.full_name ? user.full_name.charAt(0) : 'A'}
                </div>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </button>

              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-56 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-3 space-y-2 z-50">
                  <div className="px-2 py-1.5 border-b border-slate-800">
                    <p className="text-xs font-bold text-white">{user?.full_name || 'Admin User'}</p>
                    <p className="text-[10px] text-slate-400">{user?.email || 'admin@revenueagent.ai'}</p>
                  </div>
                  <div className="space-y-1 text-xs text-slate-300">
                    <Link
                      to="/settings"
                      onClick={() => setShowUserMenu(false)}
                      className="block px-2 py-1.5 hover:bg-slate-800 rounded-lg transition-colors"
                    >
                      Account Settings
                    </Link>
                    <Link
                      to="/audit"
                      onClick={() => setShowUserMenu(false)}
                      className="block px-2 py-1.5 hover:bg-slate-800 rounded-lg transition-colors"
                    >
                      Audit Trail
                    </Link>
                  </div>
                  <div className="border-t border-slate-800 pt-1">
                    <button
                      onClick={logout}
                      className="w-full text-left px-2 py-1.5 text-xs text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors font-semibold"
                    >
                      Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page Content Body */}
        <div className="p-6 md:p-8 space-y-8 flex-1 overflow-y-auto">{children}</div>
      </main>
    </div>
  );
};

