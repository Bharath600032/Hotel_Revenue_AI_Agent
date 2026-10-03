import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { EventItem, HolidayItem, CalendarImpact, WeatherForecastResponse } from '../types';
import {
  Calendar,
  Flame,
  PartyPopper,
  Plus,
  FileSpreadsheet,
  UploadCloud,
  X,
  CheckCircle2,
  Trash2,
  Building,
  Sparkles,
  Archive,
  Clock,
  Sun,
  CloudSun,
  CloudRain,
  CloudLightning,
  Thermometer,
  Droplets,
  Wind,
} from 'lucide-react';
import { useHotel } from '../context/HotelContext';

const getTodayDateString = () => new Date().toISOString().split('T')[0];

export const Events: React.FC = () => {
  const { selectedHotel } = useHotel();
  const activeCity = selectedHotel?.city || 'Goa';
  const hotelId = selectedHotel?.hotel_id || 1;

  const [stayDate, setStayDate] = useState(getTodayDateString());

  const [events, setEvents] = useState<EventItem[]>([]);
  const [holidays, setHolidays] = useState<HolidayItem[]>([]);
  const [impact, setImpact] = useState<CalendarImpact | null>(null);
  const [weatherForecast, setWeatherForecast] = useState<WeatherForecastResponse | null>(null);
  const [weatherHorizon, setWeatherHorizon] = useState<number>(14);
  const [loading, setLoading] = useState(true);
  const [successMsg, setSuccessMsg] = useState('');

  // Tabs and Filters State
  const [activeTab, setActiveTab] = useState<'LIVE' | 'ARCHIVED'>('LIVE');
  const [liveFilter, setLiveFilter] = useState<'ALL' | 'ACTIVE' | 'UPCOMING'>('ALL');

  // Modals state
  const [showAddModal, setShowAddModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);

  // Manual Event Form State
  const [eventName, setEventName] = useState('');
  const [eventCity, setEventCity] = useState(activeCity);
  const [eventType, setEventType] = useState('CONFERENCE');
  const [startDate, setStartDate] = useState(getTodayDateString());
  const [endDate, setEndDate] = useState(getTodayDateString());
  const [attendance, setAttendance] = useState<number | ''>(5000);
  const [venue, setVenue] = useState('');
  const [importance, setImportance] = useState(3);
  const [submitting, setSubmitting] = useState(false);

  // Upload Excel File State
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    setEventCity(activeCity);
  }, [activeCity]);

  useEffect(() => {
    fetchEventData();
  }, [stayDate, activeCity, hotelId, weatherHorizon]);

  const fetchEventData = async () => {
    try {
      setLoading(true);
      const [evtData, holData, impData, wData] = await Promise.all([
        apiService.getEvents(activeCity),
        apiService.getHolidays('India'),
        apiService.getCalendarImpact(hotelId, stayDate),
        apiService.getWeatherForecast(hotelId, weatherHorizon).catch(() => null),
      ]);
      setEvents(evtData);
      setHolidays(holData);
      setImpact(impData);
      if (wData) setWeatherForecast(wData);
    } catch (err) {
      console.error('Failed to load event data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await apiService.createEvent({
        event_name: eventName.trim(),
        city: eventCity.trim() || activeCity,
        event_type: eventType,
        start_date: startDate,
        end_date: endDate || startDate,
        expected_attendance: attendance ? Number(attendance) : undefined,
        venue: venue.trim() || undefined,
        importance: Number(importance),
      });

      setSuccessMsg(`Event '${eventName}' created successfully!`);
      setShowAddModal(false);
      setEventName('');
      setStartDate(stayDate);
      setEndDate(stayDate);
      setVenue('');
      await fetchEventData();
    } catch (err: any) {
      console.error('Failed to create event:', err);
      alert(err?.response?.data?.detail || 'Failed to create event.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUploadExcel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;
    try {
      setUploading(true);
      const res = await apiService.uploadEventsExcel(uploadFile);
      setSuccessMsg(res.message || `Successfully imported events from '${uploadFile.name}'!`);
      setShowUploadModal(false);
      setUploadFile(null);
      await fetchEventData();
    } catch (err: any) {
      console.error('Failed to upload events Excel file:', err);
      alert(err?.response?.data?.detail || 'Failed to upload Excel file. Check column headers.');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteEvent = async (eventId: number, name: string) => {
    if (!window.confirm(`Are you sure you want to delete event '${name}'?`)) return;
    try {
      await apiService.deleteEvent(eventId);
      setSuccessMsg(`Event '${name}' deleted.`);
      await fetchEventData();
    } catch (err) {
      console.error('Failed to delete event:', err);
    }
  };

  const getEventStatus = (sDateStr: string, eDateStr?: string, refDateStr: string = stayDate): 'ACTIVE' | 'UPCOMING' | 'COMPLETED' => {
    const eDate = eDateStr || sDateStr;
    if (refDateStr >= sDateStr && refDateStr <= eDate) {
      return 'ACTIVE';
    } else if (refDateStr < sDateStr) {
      return 'UPCOMING';
    } else {
      return 'COMPLETED';
    }
  };

  const getHolidayStatus = (holidayDateStr: string, refDateStr: string = stayDate): 'ACTIVE' | 'UPCOMING' | 'COMPLETED' => {
    if (refDateStr === holidayDateStr) {
      return 'ACTIVE';
    } else if (refDateStr < holidayDateStr) {
      return 'UPCOMING';
    } else {
      return 'COMPLETED';
    }
  };

  const eventTypesList = [
    'HOLIDAY',
    'CONFERENCE',
    'FESTIVAL',
    'CONCERT',
    'SPORTS',
    'EXHIBITION',
    'CULTURAL',
    'OTHER',
  ];

  // Classification of Regional City Events vs Holiday Category Events vs Official Holidays
  const regionalCityEvents = events.filter((e) => e.event_type !== 'HOLIDAY');
  const holidayCategoryEvents = events.filter((e) => e.event_type === 'HOLIDAY');

  const liveRegionalCityEvents = regionalCityEvents.filter((e) => {
    const st = getEventStatus(e.start_date, e.end_date, stayDate);
    if (st === 'COMPLETED') return false;
    if (liveFilter === 'ACTIVE') return st === 'ACTIVE';
    if (liveFilter === 'UPCOMING') return st === 'UPCOMING';
    return true;
  });
  const archivedRegionalCityEvents = regionalCityEvents.filter(
    (e) => getEventStatus(e.start_date, e.end_date, stayDate) === 'COMPLETED'
  );

  const liveHolidayCategoryEvents = holidayCategoryEvents.filter((e) => {
    const st = getEventStatus(e.start_date, e.end_date, stayDate);
    if (st === 'COMPLETED') return false;
    if (liveFilter === 'ACTIVE') return st === 'ACTIVE';
    if (liveFilter === 'UPCOMING') return st === 'UPCOMING';
    return true;
  });
  const archivedHolidayCategoryEvents = holidayCategoryEvents.filter(
    (e) => getEventStatus(e.start_date, e.end_date, stayDate) === 'COMPLETED'
  );

  const liveHolidays = holidays.filter((h) => {
    const st = getHolidayStatus(h.holiday_date, stayDate);
    if (st === 'COMPLETED') return false;
    if (liveFilter === 'ACTIVE') return st === 'ACTIVE';
    if (liveFilter === 'UPCOMING') return st === 'UPCOMING';
    return true;
  });
  const archivedHolidays = holidays.filter(
    (h) => getHolidayStatus(h.holiday_date, stayDate) === 'COMPLETED'
  );

  // Aggregated Counts for Badges
  const totalLiveCount =
    regionalCityEvents.filter((e) => getEventStatus(e.start_date, e.end_date, stayDate) !== 'COMPLETED').length +
    holidayCategoryEvents.filter((e) => getEventStatus(e.start_date, e.end_date, stayDate) !== 'COMPLETED').length +
    holidays.filter((h) => getHolidayStatus(h.holiday_date, stayDate) !== 'COMPLETED').length;

  const totalActiveCount =
    regionalCityEvents.filter((e) => getEventStatus(e.start_date, e.end_date, stayDate) === 'ACTIVE').length +
    holidayCategoryEvents.filter((e) => getEventStatus(e.start_date, e.end_date, stayDate) === 'ACTIVE').length +
    holidays.filter((h) => getHolidayStatus(h.holiday_date, stayDate) === 'ACTIVE').length;

  const totalUpcomingCount =
    regionalCityEvents.filter((e) => getEventStatus(e.start_date, e.end_date, stayDate) === 'UPCOMING').length +
    holidayCategoryEvents.filter((e) => getEventStatus(e.start_date, e.end_date, stayDate) === 'UPCOMING').length +
    holidays.filter((h) => getHolidayStatus(h.holiday_date, stayDate) === 'UPCOMING').length;

  const totalArchivedCount =
    archivedRegionalCityEvents.length + archivedHolidayCategoryEvents.length + archivedHolidays.length;

  return (
    <div className="space-y-6 font-sans">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-3">
            <div className="p-2.5 bg-gradient-to-tr from-amber-500 to-indigo-600 rounded-2xl shadow-lg shadow-amber-500/20">
              <Calendar className="w-6 h-6 text-white" />
            </div>
            Events & Holidays Calendar Impact
          </h1>
          <p className="text-slate-400 text-xs mt-1">
            Evaluate high-demand regional events, festival long weekends, and automated yield demand multipliers for{' '}
            <strong className="text-amber-300">{selectedHotel?.hotel_name || 'Selected Property'}</strong> ({activeCity}).
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => {
              setEventName('');
              setStartDate(stayDate);
              setEndDate(stayDate);
              setVenue('');
              setShowAddModal(true);
            }}
            className="px-4 py-2.5 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-white text-xs font-bold rounded-2xl shadow-lg shadow-amber-600/30 flex items-center gap-2 transition-all hover:scale-[1.02] cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            Add Event Manually
          </button>

          <button
            onClick={() => setShowUploadModal(true)}
            className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white text-xs font-bold rounded-2xl border border-slate-700 flex items-center gap-2 transition-all cursor-pointer"
          >
            <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
            Upload Excel / CSV
          </button>

          <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 p-2 rounded-2xl text-xs">
            <span className="text-slate-400 font-bold">Stay Date:</span>
            <input
              type="date"
              value={stayDate}
              onChange={(e) => setStayDate(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-white px-2.5 py-1 rounded-xl font-mono"
            />
          </div>
        </div>
      </div>

      {successMsg && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl text-emerald-400 text-xs font-bold flex items-center justify-between shadow-lg">
          <span className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            {successMsg}
          </span>
          <button onClick={() => setSuccessMsg('')} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-amber-500"></div>
        </div>
      ) : (
        <>
          {/* Calendar Impact Summary Card */}
          {impact && (
            <div className="p-6 bg-gradient-to-r from-amber-950/40 via-slate-900 to-indigo-950/40 border border-amber-500/30 rounded-3xl flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
              <div className="space-y-1">
                <span className="text-xs text-amber-400 font-mono font-bold uppercase tracking-wider">
                  Target Stay Date: {impact.stay_date}
                </span>
                <h3 className="text-xl font-extrabold text-white">Combined Demand Multiplier Evaluation</h3>
                <p className="text-xs text-slate-300">
                  Active Events in {activeCity}: <strong className="text-emerald-400 font-bold">{impact.active_events.length}</strong> | Active Holidays: <strong className="text-emerald-400 font-bold">{impact.active_holidays.length}</strong>
                </p>
              </div>

              <div className="p-4 bg-slate-950/80 rounded-2xl border border-amber-500/40 text-center min-w-[180px] shadow-inner">
                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Demand Multiplier</span>
                <p className="text-3xl font-black text-amber-400 mt-0.5">
                  {impact.combined_demand_multiplier}x
                </p>
              </div>
            </div>
          )}

          {/* Navigation Bar: Live Events vs Archived Events */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-3 pt-2">
            <div className="flex items-center gap-2 p-1 bg-slate-950 border border-slate-800 rounded-2xl">
              <button
                onClick={() => setActiveTab('LIVE')}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
                  activeTab === 'LIVE'
                    ? 'bg-gradient-to-r from-amber-600 to-indigo-600 text-white shadow-lg shadow-amber-500/20'
                    : 'text-slate-400 hover:text-white hover:bg-slate-900'
                }`}
              >
                <Flame className="w-3.5 h-3.5 text-amber-400" />
                <span>Live Events & Holidays</span>
                <span className="px-2 py-0.5 text-[10px] font-mono font-extrabold bg-amber-500/20 text-amber-300 rounded-full border border-amber-500/30">
                  {totalLiveCount}
                </span>
              </button>

              <button
                onClick={() => setActiveTab('ARCHIVED')}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
                  activeTab === 'ARCHIVED'
                    ? 'bg-slate-800 text-white shadow-lg border border-slate-700'
                    : 'text-slate-400 hover:text-white hover:bg-slate-900'
                }`}
              >
                <Archive className="w-3.5 h-3.5 text-slate-400" />
                <span>Archived & Past Events</span>
                <span className="px-2 py-0.5 text-[10px] font-mono font-extrabold bg-slate-800 text-slate-400 rounded-full border border-slate-700">
                  {totalArchivedCount}
                </span>
              </button>
            </div>

            {activeTab === 'LIVE' && (
              <div className="flex items-center gap-1.5 text-xs">
                <span className="text-slate-500 text-[11px] font-bold mr-1">Status Filter:</span>
                {(['ALL', 'ACTIVE', 'UPCOMING'] as const).map((filter) => (
                  <button
                    key={filter}
                    onClick={() => setLiveFilter(filter)}
                    className={`px-3 py-1 rounded-xl text-[11px] font-bold transition-all cursor-pointer border ${
                      liveFilter === filter
                        ? filter === 'ACTIVE'
                          ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50 shadow-sm'
                          : filter === 'UPCOMING'
                          ? 'bg-sky-500/20 text-sky-300 border-sky-500/50 shadow-sm'
                          : 'bg-indigo-600 text-white border-indigo-500 shadow-sm'
                        : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
                    }`}
                  >
                    {filter === 'ALL' && `All Live (${totalLiveCount})`}
                    {filter === 'ACTIVE' && `🔥 Active Now (${totalActiveCount})`}
                    {filter === 'UPCOMING' && `📅 Upcoming (${totalUpcomingCount})`}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* TAB 1: LIVE EVENTS & HOLIDAYS */}
          {activeTab === 'LIVE' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* City Events Column */}
              <div className="p-6 bg-slate-900/90 border border-slate-800 rounded-3xl space-y-4 shadow-xl">
                <div className="flex justify-between items-center border-b border-slate-800/80 pb-3">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <PartyPopper className="w-5 h-5 text-indigo-400" />
                    Regional City Events ({activeCity})
                  </h3>
                  <span className="text-xs text-slate-400 font-mono">
                    Live: <strong className="text-emerald-400">{liveRegionalCityEvents.length}</strong>
                  </span>
                </div>

                {liveRegionalCityEvents.length === 0 ? (
                  <div className="p-8 text-center bg-slate-950/50 rounded-2xl border border-slate-800/60 space-y-2">
                    <PartyPopper className="w-8 h-8 text-slate-600 mx-auto" />
                    <p className="text-xs font-semibold text-slate-300">
                      No live or upcoming events matching filter for {activeCity}.
                    </p>
                    <p className="text-[11px] text-slate-500">
                      Completed past events are safely stored under the Archived tab.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {liveRegionalCityEvents.map((e) => {
                      const status = getEventStatus(e.start_date, e.end_date, stayDate);
                      const isActive = status === 'ACTIVE';

                      return (
                        <div
                          key={e.event_id}
                          className={`p-4 rounded-2xl space-y-2 transition-all group border ${
                            isActive
                              ? 'bg-emerald-950/20 border-emerald-500/40 shadow-lg shadow-emerald-500/5 ring-1 ring-emerald-500/20'
                              : 'bg-slate-950/70 border-slate-800 hover:border-slate-700'
                          }`}
                        >
                          <div className="flex justify-between items-start gap-2">
                            <div>
                              <div className="flex items-center gap-2">
                                <h4 className="font-bold text-white text-sm group-hover:text-indigo-300 transition-colors">
                                  {e.event_name}
                                </h4>
                                {isActive ? (
                                  <span className="px-2.5 py-0.5 bg-emerald-500/20 text-emerald-300 text-[10px] font-extrabold rounded-lg border border-emerald-500/40 flex items-center gap-1.5 shadow-sm shadow-emerald-500/20 animate-pulse">
                                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                                    ACTIVE LIVE NOW
                                  </span>
                                ) : (
                                  <span className="px-2.5 py-0.5 bg-sky-500/10 text-sky-400 text-[10px] font-bold rounded-lg border border-sky-500/30 flex items-center gap-1">
                                    UPCOMING
                                  </span>
                                )}
                              </div>
                              {e.venue && (
                                <div className="flex items-center gap-1 text-[11px] text-slate-400 mt-1">
                                  <Building className="w-3 h-3 text-slate-500" />
                                  <span>{e.venue}</span>
                                </div>
                              )}
                            </div>

                            <div className="flex items-center gap-2">
                              <span className="px-2.5 py-0.5 bg-indigo-500/10 text-indigo-400 text-[10px] font-bold rounded-lg border border-indigo-500/20">
                                {e.event_type}
                              </span>
                              <button
                                onClick={() => handleDeleteEvent(e.event_id, e.event_name)}
                                className="p-1 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded transition-colors opacity-60 group-hover:opacity-100 cursor-pointer"
                                title="Delete Event"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </div>

                          <div className="flex justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/60 font-mono">
                            <span>📅 {e.start_date} to {e.end_date}</span>
                            {e.expected_attendance && (
                              <span className="text-amber-400 font-bold">
                                Attendance: {e.expected_attendance.toLocaleString()}
                              </span>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Holidays Column */}
              <div className="p-6 bg-slate-900/90 border border-slate-800 rounded-3xl space-y-4 shadow-xl">
                <div className="flex justify-between items-center border-b border-slate-800/80 pb-3">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Flame className="w-5 h-5 text-rose-400" />
                    National & Festival Holidays (India)
                  </h3>
                  <span className="text-xs text-slate-400 font-mono">
                    Live: <strong className="text-emerald-400">{liveHolidays.length + liveHolidayCategoryEvents.length}</strong>
                  </span>
                </div>

                <div className="space-y-3">
                  {/* User Created Holiday Events */}
                  {liveHolidayCategoryEvents.map((e) => {
                    const status = getEventStatus(e.start_date, e.end_date, stayDate);
                    const isActive = status === 'ACTIVE';

                    return (
                      <div
                        key={`h-evt-${e.event_id}`}
                        className={`p-4 rounded-2xl space-y-2 group border ${
                          isActive
                            ? 'bg-emerald-950/25 border-emerald-500/50 shadow-lg shadow-emerald-500/5 ring-1 ring-emerald-500/30'
                            : 'bg-amber-950/30 border-amber-800/50'
                        }`}
                      >
                        <div className="flex justify-between items-start gap-2">
                          <div>
                            <div className="flex items-center gap-2">
                              <h4 className="font-bold text-amber-200 text-sm">{e.event_name}</h4>
                              {isActive ? (
                                <span className="px-2.5 py-0.5 bg-emerald-500/20 text-emerald-300 text-[10px] font-extrabold rounded-lg border border-emerald-500/40 flex items-center gap-1.5 shadow-sm shadow-emerald-500/20 animate-pulse">
                                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                                  ACTIVE LIVE TODAY
                                </span>
                              ) : (
                                <span className="px-2.5 py-0.5 bg-amber-500/20 text-amber-300 text-[10px] font-bold rounded-lg border border-amber-500/40">
                                  UPCOMING HOLIDAY EVENT
                                </span>
                              )}
                            </div>
                            {e.venue && (
                              <div className="flex items-center gap-1 text-[11px] text-amber-400/80 mt-1">
                                <Building className="w-3 h-3 text-amber-500" />
                                <span>{e.venue}</span>
                              </div>
                            )}
                          </div>

                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => handleDeleteEvent(e.event_id, e.event_name)}
                              className="p-1 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded transition-colors opacity-60 group-hover:opacity-100 cursor-pointer"
                              title="Delete Holiday Event"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>

                        <div className="flex justify-between text-xs text-slate-400 pt-2 border-t border-amber-900/40 font-mono">
                          <span>📅 {e.start_date} to {e.end_date} ({e.city})</span>
                          <span className="text-amber-400 font-bold">Importance: {e.importance}/5 ★</span>
                        </div>
                      </div>
                    );
                  })}

                  {/* Official National Holidays */}
                  {liveHolidays.map((h) => {
                    const status = getHolidayStatus(h.holiday_date, stayDate);
                    const isActive = status === 'ACTIVE';

                    return (
                      <div
                        key={h.holiday_id}
                        className={`p-4 rounded-2xl space-y-1 border ${
                          isActive
                            ? 'bg-emerald-950/25 border-emerald-500/50 shadow-lg shadow-emerald-500/5 ring-1 ring-emerald-500/30'
                            : 'bg-slate-950/70 border-slate-800'
                        }`}
                      >
                        <div className="flex justify-between items-start gap-2">
                          <div className="flex items-center gap-2">
                            <h4 className="font-bold text-white text-sm">{h.holiday_name}</h4>
                            {isActive ? (
                              <span className="px-2.5 py-0.5 bg-emerald-500/20 text-emerald-300 text-[10px] font-extrabold rounded-lg border border-emerald-500/40 flex items-center gap-1.5 shadow-sm shadow-emerald-500/20 animate-pulse">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                                HOLIDAY ACTIVE TODAY
                              </span>
                            ) : (
                              <span className="px-2.5 py-0.5 bg-sky-500/10 text-sky-400 text-[10px] font-bold rounded-lg border border-sky-500/30">
                                UPCOMING HOLIDAY
                              </span>
                            )}
                          </div>
                          {h.is_long_weekend && (
                            <span className="px-2.5 py-0.5 bg-amber-500/10 text-amber-400 text-[10px] font-bold rounded-lg border border-amber-500/20 flex items-center gap-1">
                              <Flame className="w-3 h-3 text-amber-400" />
                              Long Weekend
                            </span>
                          )}
                        </div>
                        <div className="flex justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/60 font-mono">
                          <span>📅 {h.holiday_date} ({h.country})</span>
                          <span className="text-emerald-400 font-bold">Demand Boost: {h.demand_multiplier}x</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: ARCHIVED & PAST EVENTS */}
          {activeTab === 'ARCHIVED' && (
            <div className="space-y-4">
              {/* Top Summary Banner */}
              <div className="p-4 bg-slate-900/90 border border-slate-800 rounded-3xl text-xs text-slate-300 flex items-center justify-between shadow-xl">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-slate-800 rounded-xl text-slate-400 border border-slate-700">
                    <Archive className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="font-bold text-white text-sm">Archived & Completed Events Repository</span>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                      Showing <strong className="text-amber-300">{totalArchivedCount}</strong> completed regional events & past holidays prior to stay date <strong className="text-white font-mono">{stayDate}</strong>.
                    </p>
                  </div>
                </div>
                <span className="px-3 py-1 bg-slate-950 text-slate-400 text-[11px] font-mono font-bold rounded-xl border border-slate-800">
                  {totalArchivedCount} Archived Records
                </span>
              </div>

              {totalArchivedCount === 0 ? (
                <div className="p-12 text-center bg-slate-900/80 border border-slate-800 rounded-3xl space-y-2">
                  <Archive className="w-10 h-10 text-slate-600 mx-auto" />
                  <h4 className="text-sm font-bold text-slate-200">No Archived Events Found</h4>
                  <p className="text-xs text-slate-500">All recorded events are currently active or upcoming for {stayDate}.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Archived Regional Events Column */}
                  <div className="p-6 bg-slate-900/90 border border-slate-800 rounded-3xl space-y-4 shadow-xl">
                    <div className="flex justify-between items-center border-b border-slate-800/80 pb-3">
                      <h3 className="text-base font-bold text-slate-300 flex items-center gap-2">
                        <Archive className="w-5 h-5 text-slate-400" />
                        Archived City Events ({activeCity})
                      </h3>
                      <span className="text-xs text-slate-400 font-mono">
                        Archived: <strong className="text-slate-200">{archivedRegionalCityEvents.length}</strong>
                      </span>
                    </div>

                    <div className="space-y-3">
                      {archivedRegionalCityEvents.map((e) => (
                        <div
                          key={e.event_id}
                          className="p-4 bg-slate-950/40 border border-slate-800/60 rounded-2xl space-y-2 opacity-80 hover:opacity-100 transition-opacity group"
                        >
                          <div className="flex justify-between items-start gap-2">
                            <div>
                              <div className="flex items-center gap-2">
                                <h4 className="font-bold text-slate-200 text-sm line-through decoration-slate-600">{e.event_name}</h4>
                                <span className="px-2.5 py-0.5 bg-slate-800 text-slate-400 text-[10px] font-bold rounded-lg border border-slate-700">
                                  COMPLETED & ARCHIVED
                                </span>
                              </div>
                              {e.venue && (
                                <div className="flex items-center gap-1 text-[11px] text-slate-500 mt-1">
                                  <Building className="w-3 h-3 text-slate-600" />
                                  <span>{e.venue}</span>
                                </div>
                              )}
                            </div>

                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => handleDeleteEvent(e.event_id, e.event_name)}
                                className="p-1 text-slate-600 hover:text-rose-400 hover:bg-rose-500/10 rounded transition-colors opacity-60 group-hover:opacity-100 cursor-pointer"
                                title="Delete Archived Event"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </div>

                          <div className="flex justify-between text-xs text-slate-500 pt-2 border-t border-slate-800/40 font-mono">
                            <span>📅 Ended: {e.end_date}</span>
                            {e.expected_attendance && (
                              <span>Past Attendance: {e.expected_attendance.toLocaleString()}</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Archived Holidays Column */}
                  <div className="p-6 bg-slate-900/90 border border-slate-800 rounded-3xl space-y-4 shadow-xl">
                    <div className="flex justify-between items-center border-b border-slate-800/80 pb-3">
                      <h3 className="text-base font-bold text-slate-300 flex items-center gap-2">
                        <Clock className="w-5 h-5 text-slate-400" />
                        Archived National & Festival Holidays
                      </h3>
                      <span className="text-xs text-slate-400 font-mono">
                        Archived: <strong className="text-slate-200">{archivedHolidays.length + archivedHolidayCategoryEvents.length}</strong>
                      </span>
                    </div>

                    <div className="space-y-3">
                      {archivedHolidayCategoryEvents.map((e) => (
                        <div
                          key={`arch-h-${e.event_id}`}
                          className="p-4 bg-slate-950/40 border border-slate-800/60 rounded-2xl space-y-2 opacity-80 hover:opacity-100 transition-opacity group"
                        >
                          <div className="flex justify-between items-start gap-2">
                            <div>
                              <div className="flex items-center gap-2">
                                <h4 className="font-bold text-slate-300 text-sm line-through decoration-slate-600">{e.event_name}</h4>
                                <span className="px-2.5 py-0.5 bg-slate-800 text-slate-400 text-[10px] font-bold rounded-lg border border-slate-700">
                                  PAST HOLIDAY EVENT
                                </span>
                              </div>
                            </div>
                            <button
                              onClick={() => handleDeleteEvent(e.event_id, e.event_name)}
                              className="p-1 text-slate-600 hover:text-rose-400 hover:bg-rose-500/10 rounded transition-colors opacity-60 group-hover:opacity-100 cursor-pointer"
                              title="Delete Archived Event"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>

                          <div className="flex justify-between text-xs text-slate-500 pt-2 border-t border-slate-800/40 font-mono">
                            <span>📅 Ended: {e.end_date}</span>
                            <span>Importance: {e.importance}/5 ★</span>
                          </div>
                        </div>
                      ))}

                      {archivedHolidays.map((h) => (
                        <div
                          key={`arch-hol-${h.holiday_id}`}
                          className="p-4 bg-slate-950/40 border border-slate-800/60 rounded-2xl space-y-1 opacity-80 hover:opacity-100 transition-opacity"
                        >
                          <div className="flex justify-between items-start gap-2">
                            <h4 className="font-bold text-slate-300 text-sm line-through decoration-slate-600">{h.holiday_name}</h4>
                            <span className="px-2.5 py-0.5 bg-slate-800 text-slate-400 text-[10px] font-bold rounded-lg border border-slate-700">
                              PAST HOLIDAY (ARCHIVED)
                            </span>
                          </div>
                          <div className="flex justify-between text-xs text-slate-500 pt-2 border-t border-slate-800/40 font-mono">
                            <span>📅 Date: {h.holiday_date} ({h.country})</span>
                            <span>Multiplier: {h.demand_multiplier}x</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* MANUAL EVENT CREATION MODAL */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4 font-sans">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl max-w-md w-full space-y-4 shadow-2xl relative overflow-hidden">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <PartyPopper className="w-5 h-5 text-amber-400" />
                Add Regional Event Manually
              </h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white cursor-pointer">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateEvent} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-300 font-bold">Event Title / Name</label>
                <input
                  type="text"
                  value={eventName}
                  onChange={(e) => setEventName(e.target.value)}
                  placeholder="e.g. Sunburn Goa Festival / Tech Summit"
                  className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-300 font-bold">City Location</label>
                  <input
                    type="text"
                    value={eventCity}
                    onChange={(e) => setEventCity(e.target.value)}
                    placeholder="e.g. Goa / Chennai"
                    className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                    required
                  />
                </div>
                <div>
                  <label className="text-slate-300 font-bold">Event Type</label>
                  <select
                    value={eventType}
                    onChange={(e) => setEventType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                  >
                    {eventTypesList.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-300 font-bold">Start Date</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1 font-mono"
                    required
                  />
                </div>
                <div>
                  <label className="text-slate-300 font-bold">End Date</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1 font-mono"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-300 font-bold">Expected Attendance</label>
                  <input
                    type="number"
                    value={attendance}
                    onChange={(e) => setAttendance(e.target.value ? Number(e.target.value) : '')}
                    placeholder="e.g. 15000"
                    className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1 font-mono"
                  />
                </div>
                <div>
                  <label className="text-slate-300 font-bold">Impact Rating (1-5)</label>
                  <select
                    value={importance}
                    onChange={(e) => setImportance(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                  >
                    <option value={1}>1 - Minor</option>
                    <option value={2}>2 - Moderate</option>
                    <option value={3}>3 - High Demand</option>
                    <option value={4}>4 - Major City Event</option>
                    <option value={5}>5 - Extreme Surge Event</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-slate-300 font-bold">Venue / Stadium / Center</label>
                <input
                  type="text"
                  value={venue}
                  onChange={(e) => setVenue(e.target.value)}
                  placeholder="e.g. Vagator Beach / International Trade Center"
                  className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                />
              </div>

              <div className="flex gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 py-2.5 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-white font-bold rounded-xl shadow-lg shadow-amber-600/30 flex items-center justify-center gap-2 cursor-pointer"
                >
                  <Sparkles className="w-4 h-4" />
                  {submitting ? 'Creating...' : 'Create Event Entry'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* UPLOAD EXCEL / CSV MODAL */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4 font-sans">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl max-w-lg w-full space-y-4 shadow-2xl relative overflow-hidden">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <FileSpreadsheet className="w-5 h-5 text-emerald-400" />
                Upload Excel / CSV Events Data
              </h3>
              <button onClick={() => setShowUploadModal(false)} className="text-slate-400 hover:text-white cursor-pointer">
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-400">
              Bulk import city events, conferences, and festival schedules directly from an Excel spreadsheet (`.xlsx`, `.xls`) or `.csv` file.
            </p>

            <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-2 text-xs">
              <div className="flex items-center gap-2 text-emerald-400 font-bold">
                <Sparkles className="w-4 h-4" />
                <span>Supported Column Headers:</span>
              </div>
              <p className="text-slate-300 font-mono text-[11px] leading-relaxed">
                <strong className="text-white">Required:</strong> Event Name, City, Start Date, End Date<br />
                <strong className="text-white">Optional:</strong> Event Type, Expected Attendance, Venue, Importance
              </p>
              <div className="p-2.5 bg-slate-900 rounded-xl border border-slate-800 text-[10px] text-slate-400 font-mono">
                Example Format: Sunburn Festival | Goa | FESTIVAL | 2026-12-27 | 2026-12-30 | 50000 | Vagator Beach
              </div>
            </div>

            <form onSubmit={handleUploadExcel} className="space-y-4 text-xs">
              <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-2xl p-6 text-center space-y-2 cursor-pointer transition-colors bg-slate-950/40">
                <UploadCloud className="w-8 h-8 text-indigo-400 mx-auto" />
                <div>
                  <label htmlFor="file-upload" className="cursor-pointer text-indigo-400 font-bold hover:underline">
                    Select Excel or CSV File
                  </label>
                  <p className="text-[11px] text-slate-400 mt-0.5">Supports .xlsx, .xls, and .csv files</p>
                </div>
                <input
                  id="file-upload"
                  type="file"
                  accept=".xlsx, .xls, .csv"
                  onChange={(e) => setUploadFile(e.target.files ? e.target.files[0] : null)}
                  className="hidden"
                />
                {uploadFile && (
                  <div className="mt-2 p-2 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 font-mono font-bold flex items-center justify-center gap-2 text-xs">
                    <FileSpreadsheet className="w-4 h-4" />
                    <span>Selected: {uploadFile.name} ({(uploadFile.size / 1024).toFixed(1)} KB)</span>
                  </div>
                )}
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="flex-1 py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!uploadFile || uploading}
                  className="flex-1 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
                >
                  <UploadCloud className="w-4 h-4" />
                  {uploading ? 'Processing & Importing...' : 'Import Events Data'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
