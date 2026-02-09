// Transportation Modes
export const TRANSPORTATION_MODES = {
  AIR: 'air',
  MARITIME: 'maritime',
  GROUND: 'ground',
  MULTIMODAL: 'multimodal',
} as const;

// Shipment Statuses
export const SHIPMENT_STATUS = {
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

// Container Statuses
export const CONTAINER_STATUS = {
  EMPTY: 'empty',
  LOADED: 'loaded',
  IN_TRANSIT: 'in_transit',
  AT_PORT: 'at_port',
  AT_TERMINAL: 'at_terminal',
  DELIVERED: 'delivered',
  DAMAGED: 'damaged',
} as const;

// Container Types
export const CONTAINER_TYPES = {
  '20FT': '20FT',
  '40FT': '40FT',
  '40HC': '40HC',
  '45HC': '45HC',
  REEFER: 'REEFER',
  TANK: 'TANK',
  FLAT_RACK: 'FLAT_RACK',
} as const;

// Unit Types
export const UNIT_TYPES = {
  UNT: 'UNT', // Unit
  CTN: 'CTN', // Carton
  PLT: 'PLT', // Pallet
  PKG: 'PKG', // Package
  BOX: 'BOX', // Box
  DRUM: 'DRUM', // Drum
} as const;

// Alert Severities
export const ALERT_SEVERITY = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
} as const;

// Alert Types
export const ALERT_TYPES = {
  DELAY: 'delay',
  CUSTOMS: 'customs',
  WEATHER: 'weather',
  SECURITY: 'security',
  DOCUMENT: 'document',
  PAYMENT: 'payment',
  SYSTEM: 'system',
} as const;

// Document Types
export const DOCUMENT_TYPES = {
  BILL_OF_LADING: 'bill_of_lading',
  COMMERCIAL_INVOICE: 'commercial_invoice',
  PACKING_LIST: 'packing_list',
  CERTIFICATE_OF_ORIGIN: 'certificate_of_origin',
  INSURANCE_CERTIFICATE: 'insurance_certificate',
  CUSTOMS_DECLARATION: 'customs_declaration',
  PHOTO: 'photo',
  OTHER: 'other',
} as const;

// Invoice Statuses
export const INVOICE_STATUS = {
  DRAFT: 'draft',
  PENDING: 'pending',
  PAID: 'paid',
  OVERDUE: 'overdue',
  CANCELLED: 'cancelled',
} as const;

// Payment Terms
export const PAYMENT_TERMS = {
  PREPAID: 'PREPAID',
  COLLECT: 'COLLECT',
  NET_15: 'NET 15',
  NET_30: 'NET 30',
  NET_45: 'NET 45',
  NET_60: 'NET 60',
  DUE_ON_RECEIPT: 'DUE ON RECEIPT',
} as const;

// Currency Codes
export const CURRENCIES = {
  USD: 'USD',
  EUR: 'EUR',
  GBP: 'GBP',
  MXN: 'MXN',
  BRL: 'BRL',
  ARS: 'ARS',
  CLP: 'CLP',
  COP: 'COP',
} as const;

// Service Levels
export const SERVICE_LEVELS = {
  EXPRESS: 'express',
  STANDARD: 'standard',
  ECONOMY: 'economy',
  PREMIUM: 'premium',
} as const;


