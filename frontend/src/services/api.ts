import axios from 'axios';
import {
  AuthResponse,
  Hotel,
  RoomType,
  RevenueSummary,
  PickupPace,
  PriceRecommendation,
  AgentChatResponse,
  CompetitorHotel,
  CompetitorAnalysis,
  EventItem,
  HolidayItem,
  CalendarImpact,
  ForecastItem,
  AuditLogItem,
  RAGSearchResult,
} from '../types';

const API_BASE_URL = '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      console.warn('Session expired or unauthorized request. Clearing session token.');
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_role');
      localStorage.removeItem('user_email');
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        window.location.href = '/login?expired=true';
      }
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Auth
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const res = await apiClient.post('/auth/login', { email, password });
    return res.data;
  },

  getMe: async () => {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },

  // Hotels & Inventory
  getHotels: async (): Promise<Hotel[]> => {
    const res = await apiClient.get('/hotels');
    return res.data;
  },

  getRoomTypes: async (hotelId: number): Promise<RoomType[]> => {
    const res = await apiClient.get(`/hotels/${hotelId}/room-types`);
    return res.data;
  },

  // Analytics
  getRevenueSummary: async (hotelId: number, startDate: string, endDate: string): Promise<RevenueSummary> => {
    const res = await apiClient.get(`/hotels/${hotelId}/analytics/metrics`, {
      params: { start_date: startDate, end_date: endDate },
    });
    return res.data;
  },

  getPickupPace: async (hotelId: number, stayDate: string): Promise<PickupPace> => {
    const res = await apiClient.get(`/hotels/${hotelId}/analytics/pickup`, {
      params: { stay_date: stayDate },
    });
    return res.data;
  },

  // Demand Forecasting
  runForecast: async (hotelId: number, roomTypeId: number, startDate: string, horizonDays: number = 30): Promise<any> => {
    const res = await apiClient.post(`/hotels/${hotelId}/forecasts/run`, {
      room_type_id: roomTypeId,
      start_date: startDate,
      horizon_days: horizonDays,
    });
    return res.data;
  },

  getForecasts: async (hotelId: number, roomTypeId: number, startDate: string, endDate: string): Promise<ForecastItem[]> => {
    const res = await apiClient.get(`/hotels/${hotelId}/forecasts`, {
      params: { room_type_id: roomTypeId, start_date: startDate, end_date: endDate },
    });
    return res.data;
  },

  // Pricing Engine
  getRecommendations: async (hotelId: number, status?: string): Promise<PriceRecommendation[]> => {
    const res = await apiClient.get(`/hotels/${hotelId}/pricing/recommendations`, {
      params: { status },
    });
    return res.data;
  },

  recommendPriceBatch: async (hotelId: number, daysCount: number = 30, roomTypeId?: number): Promise<any> => {
    const res = await apiClient.post(`/hotels/${hotelId}/pricing/recommend-batch`, {
      start_date: new Date().toISOString().split('T')[0],
      days_count: daysCount,
      room_type_id: roomTypeId,
    });
    return res.data;
  },

  // 5-Stage Controlled Autonomous Pricing Flow
  runAutonomousCycle: async (hotelId: number, horizonDays: number = 30): Promise<any> => {
    const res = await apiClient.post(`/hotels/${hotelId}/pricing/autonomous-cycle`, null, {
      params: { horizon_days: horizonDays },
    });
    return res.data;
  },

  getPipelineStatus: async (hotelId: number): Promise<any> => {
    const res = await apiClient.get(`/hotels/${hotelId}/pricing/pipeline-status`);
    return res.data;
  },

  publishRecommendation: async (hotelId: number, recommendationId: number): Promise<any> => {
    const res = await apiClient.post(`/hotels/${hotelId}/pricing/publish/${recommendationId}`);
    return res.data;
  },


  // Approval Workflow
  getPendingApprovals: async (hotelId: number): Promise<PriceRecommendation[]> => {
    const res = await apiClient.get(`/hotels/${hotelId}/approvals/pending`);
    return res.data;
  },

  approveRecommendation: async (hotelId: number, recId: number): Promise<any> => {
    const res = await apiClient.post(`/hotels/${hotelId}/approvals/${recId}/approve`);
    return res.data;
  },

  overrideRecommendation: async (hotelId: number, recId: number, overrideRate: number, reason: string): Promise<any> => {
    const res = await apiClient.post(`/hotels/${hotelId}/approvals/${recId}/override`, {
      override_rate: overrideRate,
      reason,
    });
    return res.data;
  },

  rejectRecommendation: async (hotelId: number, recId: number, reason: string): Promise<any> => {
    const res = await apiClient.post(`/hotels/${hotelId}/approvals/${recId}/reject`, {
      reason,
    });
    return res.data;
  },

  // Competitor Intelligence
  getCompetitors: async (hotelId: number): Promise<CompetitorHotel[]> => {
    const res = await apiClient.get(`/hotels/${hotelId}/competitors`);
    return res.data;
  },

  getCompetitorAnalysis: async (hotelId: number, stayDate: string, myRate: number): Promise<CompetitorAnalysis> => {
    const res = await apiClient.get(`/hotels/${hotelId}/competitors/analysis`, {
      params: { stay_date: stayDate, my_rate: myRate },
    });
    return res.data;
  },

  syncGoogleCompetitorRates: async (hotelId: number, stayDate?: string): Promise<any> => {
    const res = await apiClient.post(`/hotels/${hotelId}/competitors/sync-google-rates`, null, {
      params: stayDate ? { stay_date: stayDate } : {},
    });
    return res.data;
  },


  // Events & Holidays
  getHolidays: async (country: string = 'India', startDate?: string, endDate?: string): Promise<HolidayItem[]> => {
    const res = await apiClient.get('/holidays', {
      params: { country, start_date: startDate, end_date: endDate },
    });
    return res.data;
  },

  getEvents: async (city: string, startDate?: string, endDate?: string): Promise<EventItem[]> => {
    const res = await apiClient.get('/events', {
      params: { city, start_date: startDate, end_date: endDate },
    });
    return res.data;
  },

  createEvent: async (data: {
    city: string;
    event_name: string;
    event_type: string;
    start_date: string;
    end_date: string;
    expected_attendance?: number;
    venue?: string;
    importance?: number;
  }): Promise<EventItem> => {
    const res = await apiClient.post('/events', data);
    return res.data;
  },

  uploadEventsExcel: async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post('/events/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  deleteEvent: async (eventId: number): Promise<any> => {
    const res = await apiClient.delete(`/events/${eventId}`);
    return res.data;
  },

  getCalendarImpact: async (hotelId: number, stayDate: string): Promise<CalendarImpact> => {
    const res = await apiClient.get(`/hotels/${hotelId}/calendar-impact`, {
      params: { stay_date: stayDate },
    });
    return res.data;
  },

  // Reports
  getReportDownloadUrl: (hotelId: number, startDate: string, endDate: string) => {
    return `/api/v1/exports/download?hotel_id=${hotelId}&start_date=${startDate}&end_date=${endDate}`;
  },

  // RAG Knowledge Base
  searchRAG: async (query: string, hotelId?: number): Promise<{ results: RAGSearchResult[] }> => {
    const res = await apiClient.post('/rag/search', {
      query,
      hotel_id: hotelId,
      top_k: 5,
    });
    return res.data;
  },

  uploadRAGDocument: async (title: string, category: string, content: string, hotelId?: number): Promise<any> => {
    const res = await apiClient.post('/rag/documents/upload', {
      title,
      category,
      content,
      hotel_id: hotelId,
      version: '1.0',
    });
    return res.data;
  },

  scrapeRAGWebsite: async (url: string, hotelId?: number, maxSublinks: number = 8): Promise<any> => {
    const res = await apiClient.post('/rag/documents/scrape-url', {
      url,
      hotel_id: hotelId,
      max_sublinks: maxSublinks,
    });
    return res.data;
  },

  // Audit Logs
  getAuditLogs: async (action?: string, entityType?: string): Promise<AuditLogItem[]> => {
    const res = await apiClient.get('/audit/logs', {
      params: { action, entity_type: entityType, limit: 100 },
    });
    return res.data;
  },

  // Super Admin User & Role Access Management
  getAdminUsers: async (): Promise<any[]> => {
    const res = await apiClient.get('/admin/users');
    return res.data;
  },

  createAdminUser: async (data: { email: string; password: string; full_name: string; role: string; assigned_hotels?: string }): Promise<any> => {
    const res = await apiClient.post('/admin/users', data);
    return res.data;
  },

  updateAdminUser: async (userId: number, data: { full_name?: string; role?: string; assigned_hotels?: string; is_active?: boolean }): Promise<any> => {
    const res = await apiClient.put(`/admin/users/${userId}`, data);
    return res.data;
  },

  deleteAdminUser: async (userId: number): Promise<any> => {
    const res = await apiClient.delete(`/admin/users/${userId}`);
    return res.data;
  },

  createHotel: async (data: { hotel_code: string; hotel_name: string; city: string; country: string; total_rooms: number; star_rating: number; min_price_floor?: number; max_price_ceiling?: number }): Promise<any> => {
    const res = await apiClient.post('/hotels', data);
    return res.data;
  },

  updateHotel: async (hotelId: number, data: Partial<{ hotel_code: string; hotel_name: string; city: string; country: string; total_rooms: number; star_rating: number; min_price_floor: number; max_price_ceiling: number }>): Promise<any> => {
    const res = await apiClient.put(`/hotels/${hotelId}`, data);
    return res.data;
  },

  deleteHotel: async (hotelId: number): Promise<any> => {
    const res = await apiClient.delete(`/hotels/${hotelId}`);
    return res.data;
  },

  addCompetitor: async (hotelId: number, data: { competitor_name: string; city: string; star_rating: number; website_url?: string }): Promise<any> => {
    const res = await apiClient.post(`/hotels/${hotelId}/competitors`, data);
    return res.data;
  },

  updateCompetitor: async (hotelId: number, competitorId: number, data: { competitor_name?: string; city?: string; star_rating?: number; website_url?: string }): Promise<any> => {
    const res = await apiClient.put(`/hotels/${hotelId}/competitors/${competitorId}`, data);
    return res.data;
  },

  deleteCompetitor: async (hotelId: number, competitorId: number): Promise<any> => {
    const res = await apiClient.delete(`/hotels/${hotelId}/competitors/${competitorId}`);
    return res.data;
  },


  // System Architecture Flow
  getArchitectureFlow: async (hotelId?: number): Promise<any> => {
    const res = await apiClient.get('/architecture-flow', {
      params: { hotel_id: hotelId },
    });
    return res.data;
  },

  // Agent Chat
  sendAgentChat: async (hotelId: number, message: string, sessionId?: string): Promise<AgentChatResponse> => {
    const res = await apiClient.post('/agent/chat', {
      hotel_id: hotelId,
      message,
      session_id: sessionId,
    });
    return res.data;
  },
};


