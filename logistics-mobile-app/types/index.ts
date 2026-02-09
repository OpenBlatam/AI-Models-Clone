// Transportation Modes
export const TransportationMode = {
  AIR: 'air',
  MARITIME: 'maritime',
  GROUND: 'ground',
  MULTIMODAL: 'multimodal',
} as const;

export type TransportationMode = (typeof TransportationMode)[keyof typeof TransportationMode];

// Shipment Status
export const ShipmentStatus = {
  PENDING: 'pending',
  QUOTED: 'quoted',
  BOOKED: 'booked',
  IN_TRANSIT: 'in_transit',
  IN_CUSTOMS: 'in_customs',
  DELIVERED: 'delivered',
  DELAYED: 'delayed',
  CANCELLED: 'cancelled',
  EXCEPTION: 'exception',
} as const;

export type ShipmentStatus = (typeof ShipmentStatus)[keyof typeof ShipmentStatus];

// Container Status
export const ContainerStatus = {
  EMPTY: 'empty',
  LOADED: 'loaded',
  IN_TRANSIT: 'in_transit',
  AT_PORT: 'at_port',
  AT_TERMINAL: 'at_terminal',
  DELIVERED: 'delivered',
  DAMAGED: 'damaged',
} as const;

export type ContainerStatus = (typeof ContainerStatus)[keyof typeof ContainerStatus];

// Location
export interface Location {
  country: string;
  city: string;
  port_code?: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  timezone?: string;
}

// GPS Location
export interface GPSLocation {
  latitude: number;
  longitude: number;
  timestamp: string;
  accuracy?: number;
  speed?: number;
  heading?: number;
}

// Cargo Details
export interface CargoDetails {
  description: string;
  weight_kg: number;
  volume_m3?: number;
  quantity: number;
  unit_type: string;
  value_usd?: number;
  hs_code?: string;
  dangerous_goods: boolean;
  temperature_controlled: boolean;
  special_handling?: string;
}

// Quote Models
export interface QuoteRequest {
  origin: Location;
  destination: Location;
  cargo: CargoDetails;
  transportation_mode: TransportationMode;
  preferred_departure_date?: string;
  preferred_arrival_date?: string;
  insurance_required: boolean;
  special_requirements?: string;
}

export interface QuoteOption {
  quote_id: string;
  transportation_mode: TransportationMode;
  carrier: string;
  estimated_departure: string;
  estimated_arrival: string;
  transit_days: number;
  price_usd: number;
  currency: string;
  service_level: string;
  features: string[];
}

export interface QuoteResponse {
  quote_id: string;
  request_id: string;
  origin: Location;
  destination: Location;
  cargo: CargoDetails;
  options: QuoteOption[];
  valid_until: string;
  created_at: string;
}

// Booking Models
export interface ShipperInfo {
  name: string;
  email: string;
  phone: string;
  address?: string;
  company?: string;
}

export interface ConsigneeInfo {
  name: string;
  email: string;
  phone: string;
  address?: string;
  company?: string;
}

export interface BookingRequest {
  quote_id: string;
  selected_option_id: string;
  shipper_info: ShipperInfo;
  consignee_info: ConsigneeInfo;
  payment_terms: string;
  special_instructions?: string;
}

export interface BookingResponse {
  booking_id: string;
  quote_id: string;
  shipment_id: string;
  status: ShipmentStatus;
  booking_reference: string;
  carrier_reference?: string;
  created_at: string;
  estimated_departure: string;
  estimated_arrival: string;
}

// Shipment Models
export interface ShipmentRequest {
  booking_id?: string;
  origin: Location;
  destination: Location;
  cargo: CargoDetails;
  transportation_mode: TransportationMode;
  carrier?: string;
}

export interface TrackingEvent {
  event_type: string;
  location: Location;
  timestamp: string;
  description: string;
  status: ShipmentStatus;
  metadata?: Record<string, unknown>;
}

export interface ShipmentResponse {
  shipment_id: string;
  booking_id?: string;
  shipment_reference: string;
  tracking_number?: string;
  house_bill_number?: string;
  master_bill_number?: string;
  origin: Location;
  destination: Location;
  cargo: CargoDetails;
  transportation_mode: TransportationMode;
  status: ShipmentStatus;
  carrier?: string;
  tracking_events: TrackingEvent[];
  estimated_departure?: string;
  estimated_arrival?: string;
  actual_departure?: string;
  actual_arrival?: string;
  created_at: string;
  updated_at: string;
}

// Container Models
export interface ContainerRequest {
  container_type: string;
  shipment_id?: string;
  container_number?: string;
}

export interface ContainerResponse {
  container_id: string;
  container_number: string;
  container_type: string;
  shipment_id?: string;
  status: ContainerStatus;
  location?: Location;
  gps_location?: GPSLocation;
  loaded_at?: string;
  delivered_at?: string;
  created_at: string;
  updated_at: string;
}

// Invoice Models
export interface InvoiceResponse {
  invoice_id: string;
  shipment_id: string;
  invoice_number: string;
  amount: number;
  currency: string;
  status: string;
  due_date: string;
  created_at: string;
}

// Document Models
export interface DocumentResponse {
  document_id: string;
  shipment_id: string;
  document_type: string;
  file_name: string;
  file_size: number;
  mime_type: string;
  uploaded_at: string;
  url?: string;
}

export interface DocumentRequest {
  shipment_id: string;
  document_type: string;
  file: {
    uri: string;
    type: string;
    name: string;
  };
}

// Alert Models
export interface AlertResponse {
  alert_id: string;
  shipment_id?: string;
  container_id?: string;
  alert_type: string;
  message: string;
  severity: string;
  is_read: boolean;
  created_at: string;
}

export interface AlertRequest {
  shipment_id?: string;
  container_id?: string;
  alert_type: string;
  message: string;
  severity: string;
}

// Insurance Models
export interface InsuranceResponse {
  insurance_id: string;
  shipment_id: string;
  policy_number: string;
  coverage_amount: number;
  premium: number;
  currency: string;
  coverage_type: string;
  valid_from: string;
  valid_until: string;
  created_at: string;
}

export interface InsuranceRequest {
  shipment_id: string;
  coverage_amount: number;
  coverage_type: string;
}

// Report Models
export interface DashboardStats {
  total_shipments: number;
  active_shipments: number;
  pending_shipments: number;
  delivered_shipments: number;
  total_revenue: number;
  average_transit_time: number;
}

export interface ShipmentReport {
  shipment_id: string;
  status: ShipmentStatus;
  origin: Location;
  destination: Location;
  created_at: string;
  estimated_arrival: string;
}

// API Response Wrapper
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface ApiError {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
}

// Filter and Pagination
export interface PaginationParams {
  page?: number;
  limit?: number;
}

export interface ShipmentFilters extends PaginationParams {
  status?: ShipmentStatus;
  transportation_mode?: TransportationMode;
  origin_country?: string;
  destination_country?: string;
}

// Re-export all type modules
export * from './ui';
export * from './navigation';
export * from './forms';
export * from './events';
export * from './state';
export * from './api';
export * from './hooks';
export * from './storage';
export * from './theme';
export * from './common';
export * from './refs';
export * from './gestures';
export * from './animations';

