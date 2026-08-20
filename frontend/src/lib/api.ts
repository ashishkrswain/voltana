import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

export interface Vehicle {
  id: string;
  category: string;
  make: string;
  model: string;
  variant: string;
  model_year: number;
  battery_capacity_kwh: number;
  battery_chemistry: string | null;
  arai_range_km: number;
  real_world_range_km: number;
  top_speed_kmph: number | null;
  efficiency_wh_per_km: number;
  ac_charge_port_type: string | null;
  dc_charge_port_type: string | null;
  max_ac_charge_kw: number | null;
  max_dc_charge_kw: number | null;
  dc_10_80_time_minutes: number | null;
  price_ex_showroom_inr: number | null;
  status: string;
  efficiency_curve: EfficiencyCurvePoint[];
  range_confidence: RangeConfidence | null;
}

export interface EfficiencyCurvePoint {
  id: string;
  vehicle_id: string;
  speed_band_kmph: number;
  wh_per_km: number;
  source: string;
}

export interface RangeConfidence {
  vehicle_id: string;
  confidence: string;
}

export interface VehicleListResponse {
  vehicles: Vehicle[];
  total: number;
  page: number;
  page_size: number;
}

export interface ChargerNetwork {
  id: string;
  name: string;
  slug: string;
  website: string | null;
  api_endpoint: string | null;
  ocpi_endpoint: string | null;
  is_active: number;
}

export interface Charger {
  id: string;
  network_id: string | null;
  name: string;
  address: string | null;
  latitude: number;
  longitude: number;
  connector_types: string;
  power_kw: number;
  status: string;
  notes: string | null;
  network: ChargerNetwork | null;
}

export interface ChargerListResponse {
  chargers: Charger[];
  total: number;
  page: number;
  page_size: number;
}

export interface TripPlanRequest {
  vehicle_id: string;
  origin_lat: number;
  origin_lng: number;
  dest_lat: number;
  dest_lng: number;
  assumed_avg_speed_kmph: number;
  starting_battery_pct: number;
  safety_buffer_pct: number;
}

export interface TripStop {
  charger_name: string;
  km_marker: number;
  arrival_battery_pct: number;
  charge_to_pct: number;
  estimated_charge_time_min: number;
  charger_id: string;
}

export interface TripLeg {
  from_km: number;
  to_km: number;
  duration_min: number;
  battery_start_pct: number;
  battery_end_pct: number;
  stop: TripStop | null;
}

export interface TripPlanResponse {
  total_distance_km: number;
  assumed_avg_speed_kmph: number;
  total_estimated_duration_min: number;
  legs: TripLeg[];
}

export async function listVehicles(params?: {
  page?: number;
  page_size?: number;
  category?: string;
  make?: string;
  search?: string;
}): Promise<VehicleListResponse> {
  const { data } = await api.get('/vehicles', { params });
  return data;
}

export async function listMakes(): Promise<string[]> {
  const { data } = await api.get('/vehicles/makes');
  return data;
}

export async function getVehicle(id: string): Promise<Vehicle> {
  const { data } = await api.get(`/vehicles/${id}`);
  return data;
}

export async function listChargerNetworks(): Promise<ChargerNetwork[]> {
  const { data } = await api.get('/chargers/networks');
  return data;
}

export async function listChargers(params?: {
  page?: number;
  page_size?: number;
  network_id?: string;
  connector_type?: string;
  min_power_kw?: number;
  status?: string;
  lat?: number;
  lng?: number;
  radius_km?: number;
}): Promise<ChargerListResponse> {
  const { data } = await api.get('/chargers', { params });
  return data;
}

export async function planTrip(request: TripPlanRequest): Promise<TripPlanResponse> {
  const { data } = await api.post('/trip/plan', request);
  return data;
}