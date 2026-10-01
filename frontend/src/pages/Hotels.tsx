import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { Hotel, RoomType, CompetitorHotel } from '../types';
import {
  Building2,
  BedDouble,
  Shield,
  MapPin,
  Sparkles,
  Trash2,
  Edit3,
  Plus,
  Star,
  CheckCircle2,
  AlertTriangle,
  Scale,
  X,
  Power,
} from 'lucide-react';
import { ProvisioningPercentageLoader } from '../components/ProvisioningPercentageLoader';
import { useHotel } from '../context/HotelContext';
import { useAuth } from '../auth/AuthContext';

interface StatusToggleProps {
  status: string;
  onToggle: (e: React.MouseEvent) => void;
  disabled?: boolean;
}

const StatusToggleSwitch: React.FC<StatusToggleProps> = ({ status, onToggle, disabled }) => {
  const isActive = status === 'ACTIVE';
  return (
    <button
      type="button"
      onClick={onToggle}
      disabled={disabled}
      className={`relative inline-flex items-center h-6 rounded-full px-2.5 py-0.5 text-[10px] font-extrabold uppercase tracking-wider transition-all duration-300 gap-1.5 cursor-pointer border ${
        isActive
          ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 shadow-sm shadow-emerald-500/20 hover:bg-emerald-500/30'
          : 'bg-slate-800/90 text-slate-400 border-slate-700 hover:bg-slate-800 hover:text-slate-300'
      }`}
      title={`Click to toggle status (Current: ${status})`}
    >
      <Power className={`w-3 h-3 ${isActive ? 'text-emerald-400' : 'text-slate-500'}`} />
      <span>{isActive ? 'ACTIVE' : 'INACTIVE'}</span>
      <div
        className={`w-3.5 h-3.5 rounded-full transition-transform duration-300 transform ${
          isActive ? 'bg-emerald-400 shadow-sm shadow-emerald-400/80 translate-x-0.5' : 'bg-slate-500 -translate-x-0.5'
        }`}
      />
    </button>
  );
};

export const Hotels: React.FC = () => {
  const { hotels, selectedHotel, setSelectedHotel, refreshHotels } = useHotel();
  const { user } = useAuth();
  const [roomTypes, setRoomTypes] = useState<RoomType[]>([]);
  const [competitors, setCompetitors] = useState<CompetitorHotel[]>([]);
  const [loadingCompetitors, setLoadingCompetitors] = useState(false);
  const [loading, setLoading] = useState(false);

  // Modals state
  const [showAddHotelModal, setShowAddHotelModal] = useState(false);
  const [editingHotel, setEditingHotel] = useState<Hotel | null>(null);
  const [deletingHotel, setDeletingHotel] = useState<Hotel | null>(null);

  const [showAddCompModal, setShowAddCompModal] = useState(false);
  const [editingComp, setEditingComp] = useState<CompetitorHotel | null>(null);
  const [deletingComp, setDeletingComp] = useState<CompetitorHotel | null>(null);

  // New Hotel Form State
  const [hotelCode, setHotelCode] = useState('');
  const [hotelName, setHotelName] = useState('');
  const [city, setCity] = useState('');
  const [country, setCountry] = useState('India');
  const [totalRooms, setTotalRooms] = useState(50);
  const [starRating, setStarRating] = useState(4.0);
  const [creating, setCreating] = useState(false);
  const [provisionProgress, setProvisionProgress] = useState(0);
  const [provisionStep, setProvisionStep] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Edit Hotel Form State
  const [editCode, setEditCode] = useState('');
  const [editName, setEditName] = useState('');
  const [editCity, setEditCity] = useState('');
  const [editCountry, setEditCountry] = useState('India');
  const [editTotalRooms, setEditTotalRooms] = useState(50);
  const [editStarRating, setEditStarRating] = useState(4.0);
  const [editMinFloor, setEditMinFloor] = useState(3000);
  const [editMaxCeiling, setEditMaxCeiling] = useState(25000);
  const [editMaxDailyChange, setEditMaxDailyChange] = useState(20);
  const [editStatus, setEditStatus] = useState('ACTIVE');
  const [savingHotel, setSavingHotel] = useState(false);

  // Competitor Form State
  const [compName, setCompName] = useState('');
  const [compCity, setCompCity] = useState('');
  const [compStar, setCompStar] = useState(4.0);
  const [compStatus, setCompStatus] = useState('ACTIVE');
  const [savingComp, setSavingComp] = useState(false);

  const canManageHotels = !user || ['Super Admin', 'Administrator', 'Revenue Manager'].includes(user.role);

  useEffect(() => {
    if (selectedHotel) {
      fetchRoomTypes(selectedHotel.hotel_id);
      fetchCompetitors(selectedHotel.hotel_id);
    }
  }, [selectedHotel]);

  const fetchRoomTypes = async (hotelId: number) => {
    try {
      const data = await apiService.getRoomTypes(hotelId);
      setRoomTypes(data);
    } catch (err) {
      console.error('Failed to load room types:', err);
    }
  };

  const fetchCompetitors = async (hotelId: number) => {
    try {
      setLoadingCompetitors(true);
      const data = await apiService.getCompetitors(hotelId);
      setCompetitors(data);
    } catch (err) {
      console.error('Failed to load competitor hotels:', err);
    } finally {
      setLoadingCompetitors(false);
    }
  };

  const handleSelectHotel = (hotel: Hotel) => {
    setSelectedHotel(hotel);
    fetchRoomTypes(hotel.hotel_id);
    fetchCompetitors(hotel.hotel_id);
  };

  // --- HOTEL STATUS TOGGLE & CRUD ACTIONS ---

  const handleToggleHotelStatus = async (h: Hotel, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!canManageHotels) return;
    const newStatus = h.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    try {
      const updated = await apiService.updateHotel(h.hotel_id, { status: newStatus });
      setSuccessMsg(`Status for '${h.hotel_name}' updated to ${newStatus}`);
      await refreshHotels();
      if (selectedHotel?.hotel_id === h.hotel_id) {
        setSelectedHotel(updated);
      }
    } catch (err: any) {
      console.error('Failed to toggle status:', err);
      alert(err?.response?.data?.detail || 'Failed to update hotel status.');
    }
  };

  const handleCreateHotel = async (e: React.FormEvent) => {
    e.preventDefault();
    let progressInterval: any = null;
    try {
      setCreating(true);
      setProvisionProgress(5);
      setProvisionStep('Registering Hotel Master Record & Guardrails...');

      let currentPct = 5;
      progressInterval = setInterval(() => {
        currentPct += Math.floor(Math.random() * 3) + 2;
        if (currentPct > 92) currentPct = 92;

        setProvisionProgress(currentPct);

        if (currentPct < 25) {
          setProvisionStep('Registering Hotel Master Record & Security Guardrails...');
        } else if (currentPct < 50) {
          setProvisionStep('Instantiating Multi-Tenant Hotel Revenue AI Agent...');
        } else if (currentPct < 75) {
          setProvisionStep('Provisioning Room Categories (Superior, Deluxe, Suite)...');
        } else {
          setProvisionStep('Benchmarking City Competitor Parity Feeds & Yield Logic...');
        }
      }, 70);

      const res = await apiService.createHotel({
        hotel_code: hotelCode.toUpperCase().trim(),
        hotel_name: hotelName.trim(),
        city: city.trim(),
        country: country.trim(),
        total_rooms: Number(totalRooms),
        star_rating: Number(starRating),
        min_price_floor: 3000,
        max_price_ceiling: 25000,
      });

      if (progressInterval) clearInterval(progressInterval);
      setProvisionProgress(100);
      setProvisionStep('5-Stage Autonomous Pricing Pipeline Active & Memory Scope Ready!');

      setTimeout(async () => {
        setSuccessMsg(`Hotel '${hotelName}' created! Dedicated Hotel AI Agent auto-provisioned.`);
        setShowAddHotelModal(false);
        setHotelCode('');
        setHotelName('');
        setCity('');
        setCreating(false);
        setProvisionProgress(0);

        await refreshHotels();
        if (res && res.hotel_id) {
          const updatedHotels = await apiService.getHotels();
          const newlyCreated = updatedHotels.find((h: Hotel) => h.hotel_id === res.hotel_id);
          if (newlyCreated) {
            setSelectedHotel(newlyCreated);
          }
        }
      }, 800);
    } catch (err: any) {
      if (progressInterval) clearInterval(progressInterval);
      console.error('Failed to create hotel property:', err);
      setCreating(false);
      setProvisionProgress(0);

      if (err?.response?.status !== 401) {
        const errMsg = err?.response?.data?.detail || err?.response?.data?.error?.message || 'Failed to register hotel property. Please check inputs.';
        alert(errMsg);
      }
    }
  };

  const openEditHotelModal = (h: Hotel, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingHotel(h);
    setEditCode(h.hotel_code);
    setEditName(h.hotel_name);
    setEditCity(h.city);
    setEditCountry(h.country || 'India');
    setEditTotalRooms(h.total_rooms);
    setEditStarRating(h.star_rating || 4.0);
    setEditMinFloor(h.min_price_floor || 3000);
    setEditMaxCeiling(h.max_price_ceiling || 25000);
    setEditMaxDailyChange(h.max_daily_price_change_pct || 20);
    setEditStatus(h.status || 'ACTIVE');
  };

  const handleUpdateHotel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingHotel) return;
    try {
      setSavingHotel(true);
      const updated = await apiService.updateHotel(editingHotel.hotel_id, {
        hotel_code: editCode.toUpperCase().trim(),
        hotel_name: editName.trim(),
        city: editCity.trim(),
        country: editCountry.trim(),
        total_rooms: Number(editTotalRooms),
        star_rating: Number(editStarRating),
        min_price_floor: Number(editMinFloor),
        max_price_ceiling: Number(editMaxCeiling),
        max_daily_price_change_pct: Number(editMaxDailyChange),
        status: editStatus,
      });

      setSuccessMsg(`Hotel '${editName}' updated successfully!`);
      setEditingHotel(null);
      await refreshHotels();

      if (selectedHotel?.hotel_id === editingHotel.hotel_id) {
        setSelectedHotel(updated);
      }
    } catch (err: any) {
      console.error('Failed to update hotel:', err);
      alert(err?.response?.data?.detail || 'Failed to update hotel property.');
    } finally {
      setSavingHotel(false);
    }
  };

  const openDeleteHotelModal = (h: Hotel, e: React.MouseEvent) => {
    e.stopPropagation();
    setDeletingHotel(h);
  };

  const handleDeleteHotel = async () => {
    if (!deletingHotel) return;
    try {
      setSavingHotel(true);
      await apiService.deleteHotel(deletingHotel.hotel_id);
      setSuccessMsg(`Hotel '${deletingHotel.hotel_name}' and all associated master data deleted.`);
      
      const wasSelected = selectedHotel?.hotel_id === deletingHotel.hotel_id;
      setDeletingHotel(null);
      await refreshHotels();

      if (wasSelected) {
        const remaining = hotels.filter((h) => h.hotel_id !== deletingHotel.hotel_id);
        if (remaining.length > 0) {
          setSelectedHotel(remaining[0]);
        } else {
          setSelectedHotel(null);
        }
      }
    } catch (err: any) {
      console.error('Failed to delete hotel property:', err);
      alert(err?.response?.data?.detail || 'Failed to delete hotel property.');
    } finally {
      setSavingHotel(false);
    }
  };

  // --- COMPETITOR STATUS TOGGLE & CRUD ACTIONS ---

  const handleToggleCompetitorStatus = async (c: CompetitorHotel, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!selectedHotel || !canManageHotels) return;
    const newStatus = c.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    try {
      await apiService.updateCompetitor(selectedHotel.hotel_id, c.competitor_id, { status: newStatus });
      setSuccessMsg(`Competitor '${c.competitor_name}' status updated to ${newStatus}`);
      await fetchCompetitors(selectedHotel.hotel_id);
    } catch (err: any) {
      console.error('Failed to toggle competitor status:', err);
      alert(err?.response?.data?.detail || 'Failed to update competitor status.');
    }
  };

  const handleAddCompetitor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHotel) return;
    try {
      setSavingComp(true);
      await apiService.addCompetitor(selectedHotel.hotel_id, {
        competitor_name: compName.trim(),
        city: compCity.trim() || selectedHotel.city,
        star_rating: Number(compStar),
      });

      setSuccessMsg(`Competitor '${compName}' added to competitive set.`);
      setShowAddCompModal(false);
      setCompName('');
      setCompCity('');
      setCompStar(4.0);
      await fetchCompetitors(selectedHotel.hotel_id);
    } catch (err: any) {
      console.error('Failed to add competitor:', err);
      alert(err?.response?.data?.detail || 'Failed to add competitor hotel.');
    } finally {
      setSavingComp(false);
    }
  };

  const openEditCompModal = (c: CompetitorHotel) => {
    setEditingComp(c);
    setCompName(c.competitor_name);
    setCompCity(c.city);
    setCompStar(c.star_rating);
    setCompStatus(c.status || 'ACTIVE');
  };

  const handleUpdateCompetitor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHotel || !editingComp) return;
    try {
      setSavingComp(true);
      await apiService.updateCompetitor(selectedHotel.hotel_id, editingComp.competitor_id, {
        competitor_name: compName.trim(),
        city: compCity.trim(),
        star_rating: Number(compStar),
      });

      setSuccessMsg(`Competitor '${compName}' updated.`);
      setEditingComp(null);
      await fetchCompetitors(selectedHotel.hotel_id);
    } catch (err: any) {
      console.error('Failed to update competitor:', err);
      alert(err?.response?.data?.detail || 'Failed to update competitor.');
    } finally {
      setSavingComp(false);
    }
  };

  const handleDeleteCompetitor = async () => {
    if (!selectedHotel || !deletingComp) return;
    try {
      setSavingComp(true);
      await apiService.deleteCompetitor(selectedHotel.hotel_id, deletingComp.competitor_id);
      setSuccessMsg(`Competitor '${deletingComp.competitor_name}' removed from competitive set.`);
      setDeletingComp(null);
      await fetchCompetitors(selectedHotel.hotel_id);
    } catch (err: any) {
      console.error('Failed to delete competitor:', err);
      alert(err?.response?.data?.detail || 'Failed to delete competitor.');
    } finally {
      setSavingComp(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 font-sans">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-3">
            <div className="p-2.5 bg-gradient-to-tr from-indigo-600 to-purple-600 rounded-2xl shadow-lg shadow-indigo-600/30">
              <Building2 className="w-6 h-6 text-white" />
            </div>
            Hotel Properties & Multi-Tenancy Management
          </h1>
          <p className="text-slate-400 text-xs mt-1">
            Manage hotel properties, room categories, autonomous rate guardrails, and competitive intelligence sets.
          </p>
        </div>

        {canManageHotels && (
          <button
            onClick={() => setShowAddHotelModal(true)}
            className="px-5 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-bold rounded-2xl shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition-all hover:scale-[1.02]"
          >
            <Plus className="w-4 h-4" />
            Add New Hotel Property
          </button>
        )}
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

      {/* Hotel Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {hotels.map((h) => {
          const isSelected = selectedHotel?.hotel_id === h.hotel_id;
          return (
            <div
              key={h.hotel_id}
              onClick={() => handleSelectHotel(h)}
              className={`group p-5 rounded-3xl border cursor-pointer transition-all duration-200 relative overflow-hidden ${
                isSelected
                  ? 'bg-slate-900/90 border-indigo-500/60 shadow-xl shadow-indigo-500/10 ring-1 ring-indigo-500/30'
                  : 'bg-slate-900/50 border-slate-800 hover:border-slate-700 hover:bg-slate-900/80'
              }`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-lg border border-indigo-500/20">
                    {h.hotel_code}
                  </span>
                  <h3 className="text-lg font-bold text-white mt-2.5 group-hover:text-indigo-300 transition-colors">
                    {h.hotel_name}
                  </h3>
                  <div className="flex items-center text-xs text-slate-400 mt-1">
                    <MapPin className="w-3.5 h-3.5 mr-1 text-slate-500" />
                    {h.city}, {h.country}
                  </div>
                </div>

                <div className="flex flex-col items-end gap-2">
                  {/* Customized Interactive Active / Inactive Status Toggle */}
                  <StatusToggleSwitch
                    status={h.status}
                    onToggle={(e) => handleToggleHotelStatus(h, e)}
                    disabled={!canManageHotels}
                  />

                  {canManageHotels && (
                    <div className="flex items-center gap-1 opacity-80 group-hover:opacity-100 transition-opacity mt-1">
                      <button
                        onClick={(e) => openEditHotelModal(h, e)}
                        className="p-1.5 text-slate-400 hover:text-indigo-400 hover:bg-indigo-500/10 rounded-lg transition-colors"
                        title="Edit Hotel Profile"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={(e) => openDeleteHotelModal(h, e)}
                        className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                        title="Delete Hotel Property"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 mt-4 pt-4 border-t border-slate-800/80 text-xs">
                <div>
                  <span className="text-slate-500">Total Capacity</span>
                  <p className="text-slate-200 font-bold text-sm mt-0.5">{h.total_rooms} Rooms</p>
                </div>
                <div>
                  <span className="text-slate-500">Star Rating</span>
                  <p className="text-amber-400 font-bold text-sm mt-0.5 flex items-center gap-1">
                    <Star className="w-3.5 h-3.5 fill-amber-400" />
                    {h.star_rating || 4.0} Stars
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Hotel Guardrails, Room Types, & Competitor Set */}
      {selectedHotel && (
        <div className="space-y-6 pt-2">
          {/* Section Header for Selected Hotel */}
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Building2 className="w-5 h-5 text-indigo-400" />
              Active Property Scope: <span className="text-indigo-300 font-extrabold">{selectedHotel.hotel_name}</span>
            </h2>
            <div className="flex items-center gap-3 text-xs">
              <span className="text-slate-400 font-mono">Code: <strong className="text-slate-200">{selectedHotel.hotel_code}</strong></span>
              <StatusToggleSwitch
                status={selectedHotel.status}
                onToggle={(e) => handleToggleHotelStatus(selectedHotel, e)}
                disabled={!canManageHotels}
              />
            </div>
          </div>

          {/* Price Guardrails Overview */}
          <div className="p-6 bg-slate-900/90 border border-slate-800 rounded-3xl shadow-xl space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Shield className="w-4 h-4 text-emerald-400" />
              Autonomous Rate Guardrails & Risk Constraints
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-slate-950/70 rounded-2xl border border-slate-800/80">
                <span className="text-xs text-slate-400">Min Rate Floor</span>
                <p className="text-xl font-bold text-emerald-400 mt-1">
                  ₹{selectedHotel.min_price_floor?.toLocaleString() || '3,000'}
                </p>
                <span className="text-[10px] text-slate-500">Absolute minimum room rate allowed</span>
              </div>
              <div className="p-4 bg-slate-950/70 rounded-2xl border border-slate-800/80">
                <span className="text-xs text-slate-400">Max Rate Ceiling</span>
                <p className="text-xl font-bold text-indigo-400 mt-1">
                  ₹{selectedHotel.max_price_ceiling?.toLocaleString() || '25,000'}
                </p>
                <span className="text-[10px] text-slate-500">Peak demand rate ceiling cap</span>
              </div>
              <div className="p-4 bg-slate-950/70 rounded-2xl border border-slate-800/80">
                <span className="text-xs text-slate-400">Max Daily Rate Shift</span>
                <p className="text-xl font-bold text-amber-400 mt-1">
                  ±{selectedHotel.max_daily_price_change_pct || 20}%
                </p>
                <span className="text-[10px] text-slate-500">Maximum price fluctuation per 24h</span>
              </div>
            </div>
          </div>

          {/* Competitor Set Section */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Scale className="w-5 h-5 text-indigo-400" />
                  Competitor Intelligence Set — {selectedHotel.hotel_name}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Track price parity, rate gaps, and positioning against local market competitors.
                </p>
              </div>

              {canManageHotels && (
                <button
                  onClick={() => {
                    setCompName('');
                    setCompCity(selectedHotel.city);
                    setCompStar(4.0);
                    setShowAddCompModal(true);
                  }}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-indigo-600/30 flex items-center gap-1.5 transition-all self-start md:self-auto"
                >
                  <Plus className="w-4 h-4" />
                  Add Competitor Hotel
                </button>
              )}
            </div>

            {loadingCompetitors ? (
              <div className="flex justify-center items-center h-32">
                <div className="animate-spin rounded-full h-7 w-7 border-b-2 border-indigo-500"></div>
              </div>
            ) : competitors.length === 0 ? (
              <div className="p-8 text-center bg-slate-950/50 rounded-2xl border border-slate-800/60 space-y-2">
                <Scale className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-xs font-semibold text-slate-300">No competitor hotels added yet for this property.</p>
                <p className="text-[11px] text-slate-500">Add competitors to enable automated market median rate tracking.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {competitors.map((c) => (
                  <div
                    key={c.competitor_id}
                    className="p-4 bg-slate-950/60 rounded-2xl border border-slate-800/80 space-y-3 relative group"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors">
                          {c.competitor_name}
                        </h4>
                        <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
                          <MapPin className="w-3.5 h-3.5 text-slate-500" />
                          <span>{c.city}</span>
                        </div>
                      </div>

                      {/* Interactive Status Toggle for Competitors */}
                      <StatusToggleSwitch
                        status={c.status || 'ACTIVE'}
                        onToggle={(e) => handleToggleCompetitorStatus(c, e)}
                        disabled={!canManageHotels}
                      />
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-xs">
                      <div className="flex items-center gap-1 text-amber-400 font-bold">
                        <Star className="w-3.5 h-3.5 fill-amber-400" />
                        <span>{c.star_rating} Stars</span>
                      </div>

                      {canManageHotels && (
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => openEditCompModal(c)}
                            className="p-1 text-slate-400 hover:text-indigo-400 hover:bg-slate-800 rounded transition-colors"
                            title="Edit Competitor"
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => setDeletingComp(c)}
                            className="p-1 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded transition-colors"
                            title="Delete Competitor"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Room Types Table */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <BedDouble className="w-5 h-5 text-indigo-400" />
              Room Categories & Master Inventory
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-bold uppercase tracking-wider">
                    <th className="pb-3 px-3">Room Code</th>
                    <th className="pb-3 px-3">Category Name</th>
                    <th className="pb-3 px-3">Max Guests</th>
                    <th className="pb-3 px-3">Total Inventory</th>
                    <th className="pb-3 px-3">Baseline Rate</th>
                    <th className="pb-3 px-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {roomTypes.map((rt) => (
                    <tr key={rt.room_type_id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-3.5 px-3 font-mono font-bold text-indigo-300">{rt.room_type_code}</td>
                      <td className="py-3.5 px-3 font-medium text-white">{rt.room_type_name}</td>
                      <td className="py-3.5 px-3 text-slate-300">{rt.max_occupancy} Adults</td>
                      <td className="py-3.5 px-3 font-bold text-slate-200">{rt.total_inventory} Units</td>
                      <td className="py-3.5 px-3 font-bold text-emerald-400">₹{rt.base_price?.toLocaleString()}</td>
                      <td className="py-3.5 px-3">
                        <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 text-[10px] font-bold rounded border border-emerald-500/20">
                          {rt.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* CREATE NEW HOTEL MODAL */}
      {showAddHotelModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl max-w-md w-full space-y-4 shadow-2xl relative overflow-hidden">
            {creating ? (
              <ProvisioningPercentageLoader
                progress={provisionProgress}
                currentStep={provisionStep}
                title="Auto-Provisioning Hotel AI Agent..."
                subtitle={`Deploying dedicated AI revenue model for ${hotelName || 'New Property'}...`}
              />
            ) : (
              <>
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Building2 className="w-5 h-5 text-indigo-400" />
                    Register New Hotel & Provision AI Agent
                  </h3>
                  <button onClick={() => setShowAddHotelModal(false)} className="text-slate-400 hover:text-white">
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <form onSubmit={handleCreateHotel} className="space-y-3 text-xs">
                  <div>
                    <label className="text-slate-300 font-bold">Hotel Property Name</label>
                    <input
                      type="text"
                      value={hotelName}
                      onChange={(e) => setHotelName(e.target.value)}
                      placeholder="e.g. Royal Palms Beach Resort"
                      className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                      required
                    />
                  </div>

                  <div>
                    <label className="text-slate-300 font-bold">Property Code</label>
                    <input
                      type="text"
                      value={hotelCode}
                      onChange={(e) => setHotelCode(e.target.value)}
                      placeholder="e.g. HTL_ROYALPALMS"
                      className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1 font-mono uppercase"
                      required
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-slate-300 font-bold">City</label>
                      <input
                        type="text"
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                        placeholder="e.g. Goa / Chennai"
                        className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                        required
                      />
                    </div>
                    <div>
                      <label className="text-slate-300 font-bold">Country</label>
                      <input
                        type="text"
                        value={country}
                        onChange={(e) => setCountry(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-slate-300 font-bold">Total Rooms</label>
                      <input
                        type="number"
                        value={totalRooms}
                        onChange={(e) => setTotalRooms(Number(e.target.value))}
                        className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                        required
                      />
                    </div>
                    <div>
                      <label className="text-slate-300 font-bold">Star Rating</label>
                      <input
                        type="number"
                        step="0.5"
                        value={starRating}
                        onChange={(e) => setStarRating(Number(e.target.value))}
                        className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                        required
                      />
                    </div>
                  </div>

                  <div className="flex gap-2 pt-3">
                    <button
                      type="button"
                      onClick={() => setShowAddHotelModal(false)}
                      className="flex-1 py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={creating}
                      className="flex-1 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold rounded-xl shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2"
                    >
                      <Sparkles className="w-4 h-4" />
                      Create Hotel & Provision Agent
                    </button>
                  </div>
                </form>
              </>
            )}
          </div>
        </div>
      )}

      {/* EDIT HOTEL MODAL */}
      {editingHotel && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl max-w-md w-full space-y-4 shadow-2xl">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Edit3 className="w-5 h-5 text-indigo-400" />
                Edit Hotel Master Profile
              </h3>
              <button onClick={() => setEditingHotel(null)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpdateHotel} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-300 font-bold">Hotel Property Name</label>
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                  required
                />
              </div>

              {/* Status Toggle Switch inside Edit Modal */}
              <div>
                <label className="text-slate-300 font-bold block mb-1">Hotel Operational Status</label>
                <button
                  type="button"
                  onClick={() => setEditStatus(editStatus === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE')}
                  className={`w-full py-2.5 px-4 rounded-xl border flex items-center justify-between font-bold text-xs transition-all ${
                    editStatus === 'ACTIVE'
                      ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-400 shadow-lg shadow-emerald-500/10'
                      : 'bg-slate-950 border-slate-800 text-slate-400'
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <span className={`w-2.5 h-2.5 rounded-full ${editStatus === 'ACTIVE' ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'}`} />
                    <span>{editStatus === 'ACTIVE' ? 'Property Active (Receiving AI Rate Automation)' : 'Property Inactive (Disabled)'}</span>
                  </span>
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase border ${
                    editStatus === 'ACTIVE' ? 'bg-emerald-500/30 text-emerald-300 border-emerald-400/40' : 'bg-slate-800 text-slate-400 border-slate-700'
                  }`}>
                    {editStatus}
                  </span>
                </button>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-300 font-bold">Property Code</label>
                  <input
                    type="text"
                    value={editCode}
                    onChange={(e) => setEditCode(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1 font-mono uppercase"
                    required
                  />
                </div>
                <div>
                  <label className="text-slate-300 font-bold">City</label>
                  <input
                    type="text"
                    value={editCity}
                    onChange={(e) => setEditCity(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-300 font-bold">Total Capacity (Rooms)</label>
                  <input
                    type="number"
                    value={editTotalRooms}
                    onChange={(e) => setEditTotalRooms(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                    required
                  />
                </div>
                <div>
                  <label className="text-slate-300 font-bold">Star Rating</label>
                  <input
                    type="number"
                    step="0.5"
                    value={editStarRating}
                    onChange={(e) => setEditStarRating(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-300 font-bold">Min Rate Floor (₹)</label>
                  <input
                    type="number"
                    value={editMinFloor}
                    onChange={(e) => setEditMinFloor(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1 font-mono"
                    required
                  />
                </div>
                <div>
                  <label className="text-slate-300 font-bold">Max Rate Ceiling (₹)</label>
                  <input
                    type="number"
                    value={editMaxCeiling}
                    onChange={(e) => setEditMaxCeiling(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1 font-mono"
                    required
                  />
                </div>
              </div>

              <div className="flex gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setEditingHotel(null)}
                  className="flex-1 py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingHotel}
                  className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-indigo-600/30"
                >
                  {savingHotel ? 'Saving...' : 'Save Profile Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* DELETE HOTEL CONFIRM MODAL */}
      {deletingHotel && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl max-w-md w-full space-y-4 shadow-2xl">
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-2xl flex items-center gap-3">
              <AlertTriangle className="w-6 h-6 text-rose-400 shrink-0" />
              <div>
                <h4 className="text-sm font-bold text-rose-300">Delete Hotel Property</h4>
                <p className="text-[11px] text-rose-200/80">This action will cascade delete all linked room categories, reservations, and compsets.</p>
              </div>
            </div>

            <p className="text-xs text-slate-300">
              Are you sure you want to permanently delete <strong className="text-white">{deletingHotel.hotel_name}</strong> ({deletingHotel.hotel_code})?
            </p>

            <div className="flex gap-2 pt-2">
              <button
                type="button"
                onClick={() => setDeletingHotel(null)}
                className="flex-1 py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl text-xs"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleDeleteHotel}
                disabled={savingHotel}
                className="flex-1 py-2.5 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-xl shadow-lg shadow-rose-600/30 text-xs flex items-center justify-center gap-1.5"
              >
                <Trash2 className="w-4 h-4" />
                {savingHotel ? 'Deleting...' : 'Confirm Delete Property'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ADD COMPETITOR MODAL */}
      {showAddCompModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl max-w-md w-full space-y-4 shadow-2xl">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Scale className="w-5 h-5 text-indigo-400" />
                Add Competitor Hotel
              </h3>
              <button onClick={() => setShowAddCompModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddCompetitor} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-300 font-bold">Competitor Hotel Name</label>
                <input
                  type="text"
                  value={compName}
                  onChange={(e) => setCompName(e.target.value)}
                  placeholder="e.g. Taj Exotica Goa"
                  className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-300 font-bold">City Location</label>
                  <input
                    type="text"
                    value={compCity}
                    onChange={(e) => setCompCity(e.target.value)}
                    placeholder="e.g. Goa"
                    className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                    required
                  />
                </div>
                <div>
                  <label className="text-slate-300 font-bold">Star Rating</label>
                  <input
                    type="number"
                    step="0.5"
                    value={compStar}
                    onChange={(e) => setCompStar(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                    required
                  />
                </div>
              </div>

              <div className="flex gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddCompModal(false)}
                  className="flex-1 py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingComp}
                  className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-indigo-600/30"
                >
                  {savingComp ? 'Adding...' : 'Add to Compset'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* EDIT COMPETITOR MODAL */}
      {editingComp && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl max-w-md w-full space-y-4 shadow-2xl">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Edit3 className="w-5 h-5 text-indigo-400" />
                Edit Competitor Profile
              </h3>
              <button onClick={() => setEditingComp(null)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpdateCompetitor} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-300 font-bold">Competitor Hotel Name</label>
                <input
                  type="text"
                  value={compName}
                  onChange={(e) => setCompName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-300 font-bold">City Location</label>
                  <input
                    type="text"
                    value={compCity}
                    onChange={(e) => setCompCity(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                    required
                  />
                </div>
                <div>
                  <label className="text-slate-300 font-bold">Star Rating</label>
                  <input
                    type="number"
                    step="0.5"
                    value={compStar}
                    onChange={(e) => setCompStar(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                    required
                  />
                </div>
              </div>

              <div className="flex gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setEditingComp(null)}
                  className="flex-1 py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingComp}
                  className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-indigo-600/30"
                >
                  {savingComp ? 'Saving...' : 'Save Competitor Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* DELETE COMPETITOR CONFIRM MODAL */}
      {deletingComp && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl max-w-md w-full space-y-4 shadow-2xl">
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-2xl flex items-center gap-3">
              <AlertTriangle className="w-6 h-6 text-rose-400 shrink-0" />
              <div>
                <h4 className="text-sm font-bold text-rose-300">Remove Competitor</h4>
                <p className="text-[11px] text-rose-200/80">Remove competitor from competitive pricing analysis set.</p>
              </div>
            </div>

            <p className="text-xs text-slate-300">
              Are you sure you want to remove <strong className="text-white">{deletingComp.competitor_name}</strong> from compset?
            </p>

            <div className="flex gap-2 pt-2">
              <button
                type="button"
                onClick={() => setDeletingComp(null)}
                className="flex-1 py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl text-xs"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleDeleteCompetitor}
                disabled={savingComp}
                className="flex-1 py-2.5 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-xl shadow-lg shadow-rose-600/30 text-xs flex items-center justify-center gap-1.5"
              >
                <Trash2 className="w-4 h-4" />
                {savingComp ? 'Removing...' : 'Confirm Remove Competitor'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
