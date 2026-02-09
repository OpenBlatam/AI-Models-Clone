// Navigation Routes
export const ROUTES = {
  // Tabs
  DASHBOARD: '/(tabs)',
  SHIPMENTS: '/(tabs)/shipments',
  TRACKING: '/(tabs)/tracking',
  ALERTS: '/(tabs)/alerts',

  // Shipments
  SHIPMENT_DETAIL: (id: string) => `/shipment/${id}`,

  // Quotes
  QUOTE_CREATE: '/quote/create',
  QUOTE_DETAIL: (id: string) => `/quote/${id}`,

  // Bookings
  BOOKING_CREATE: '/booking/create',
  BOOKING_DETAIL: (id: string) => `/booking/${id}`,

  // Documents
  DOCUMENT_VIEW: (id: string) => `/document/${id}`,
  DOCUMENT_UPLOAD: (shipmentId: string) => `/document/upload/${shipmentId}`,

  // Invoices
  INVOICE_DETAIL: (id: string) => `/invoice/${id}`,

  // Settings
  SETTINGS: '/settings',
  PROFILE: '/profile',
} as const;

// Deep Link Schemes
export const DEEP_LINKS = {
  SCHEME: 'logistics',
  PREFIXES: ['logistics://', 'https://logistics.app', 'https://*.logistics.app'],
} as const;


