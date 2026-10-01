export interface User {
  user_id: number;
  email: string;
  full_name: string;
  role: 'Super Admin' | 'Administrator' | 'Revenue Manager' | 'Hotel Manager' | 'Analyst' | 'Read-only User';
  is_active: boolean;
  assigned_hotels?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface Hotel {
  hotel_id: number;
  hotel_code: string;
  hotel_name: string;
  city: string;
  country: string;
  currency: string;
  total_rooms: number;
  min_price_floor?: number;
  max_price_ceiling?: number;
  max_daily_price_change_pct?: number;
  status: string;
  star_rating?: number;
}

export interface RoomType {
  room_type_id: number;
  hotel_id: number;
  room_type_code: string;
  room_type_name: string;
  max_occupancy: number;
  base_price: number;
  total_inventory: number;
  status: string;
}

export interface RevenueSummary {
  hotel_id: number;
  start_date: string;
  end_date: string;
  total_sellable_rooms: number;
  total_occupied_rooms: number;
  total_revenue: number;
  occupancy_pct: number;
  adr: number;
  revpar: number;
  trevpar: number;
  cancellation_rate_pct: number;
  average_lead_time_days: number;
}

export interface PickupPace {
  hotel_id: number;
  stay_date: string;
  current_booked_rooms: number;
  pickup_1d: number;
  pickup_3d: number;
  pickup_7d: number;
  pickup_14d: number;
  pickup_30d: number;
}

export interface PriceRecommendation {
  recommendation_id?: number;
  hotel_id: number;
  room_type_id: number;
  stay_date: string;
  recommended_rate: number;
  min_rate: number;
  max_rate: number;
  current_rate: number;
  occupancy: number;
  forecast_demand: number;
  competitor_median: number;
  demand_index: number;
  price_reason: string;
  confidence_score: number;
  status: string;
  requires_approval: boolean;
}

export interface AgentChatResponse {
  answer: string;
  recommendation?: PriceRecommendation;
  factors: string[];
  tools_used: { tool_name: string; execution_time_ms: number }[];
  requires_approval: boolean;
  agent_run_id: string;
  execution_time_seconds: number;
}

export interface CompetitorHotel {
  competitor_id: number;
  hotel_id: number;
  competitor_name: string;
  city: string;
  star_rating: number;
  status: string;
  latitude?: number;
  longitude?: number;
  distance_km?: number;
  weight_factor?: number;
  is_active?: boolean;
}

export interface CompetitorOTARate {
  ota_name: string;
  rate: number;
  is_lowest?: boolean;
}

export interface CompetitorRateDetail {
  competitor_id: number;
  competitor_name: string;
  rate: number;
  lowest_ota_name?: string;
  ota_name?: string;
  source: string;
  captured_at?: string;
  ota_rates?: CompetitorOTARate[];
}

export interface CompetitorAnalysis {
  hotel_id: number;
  stay_date: string;
  my_rate: number;
  my_hotel_rate?: number;
  competitor_count: number;
  competitor_rates: CompetitorRateDetail[];
  median_rate: number;
  competitor_median?: number;
  min_rate: number;
  competitor_min?: number;
  max_rate: number;
  competitor_max?: number;
  price_gap_pct: number;
  percentile_rank: number;
  positioning: string;
  anomaly_detected?: boolean;
  anomaly_reason?: string;
}

export interface EventItem {
  event_id: number;
  event_name: string;
  event_type: string;
  city: string;
  start_date: string;
  end_date: string;
  expected_attendance?: number;
  importance?: number;
  venue?: string;
  source?: string;
}

export interface HolidayItem {
  holiday_id: number;
  holiday_name: string;
  holiday_date: string;
  country: string;
  is_long_weekend: boolean;
  demand_multiplier: number;
}

export interface CalendarImpact {
  hotel_id: number;
  stay_date: string;
  combined_demand_multiplier: number;
  active_events: EventItem[];
  active_holidays: HolidayItem[];
}

export interface ForecastItem {
  stay_date: string;
  predicted_demand: number;
  lower_bound: number;
  upper_bound: number;
  confidence_score: number;
  model_name: string;
}

export interface AuditLogItem {
  audit_id: number;
  user_id?: number;
  action: string;
  entity_type: string;
  entity_id?: number;
  old_value?: string;
  new_value?: string;
  ip_address?: string;
  created_at: string;
}

export interface RAGSearchResult {
  chunk_id: string;
  title: string;
  category: string;
  content: string;
  similarity_score: number;
}

