// API Endpoints
export const API_ENDPOINTS = {
  // Forwarding
  QUOTES: '/forwarding/quotes',
  QUOTE_BY_ID: (id: string) => `/forwarding/quotes/${id}`,
  BOOKINGS: '/forwarding/bookings',
  BOOKING_BY_ID: (id: string) => `/forwarding/bookings/${id}`,
  SHIPMENTS: '/forwarding/shipments',
  SHIPMENT_BY_ID: (id: string) => `/forwarding/shipments/${id}`,
  SHIPMENT_STATUS: (id: string) => `/forwarding/shipments/${id}/status`,
  CONTAINERS: '/forwarding/containers',
  CONTAINER_BY_ID: (id: string) => `/forwarding/containers/${id}`,
  CONTAINERS_BY_SHIPMENT: (shipmentId: string) => `/forwarding/containers/shipment/${shipmentId}`,
  CONTAINER_STATUS: (id: string) => `/forwarding/containers/${id}/status`,

  // Tracking
  TRACKING_SHIPMENT: (id: string) => `/tracking/shipment/${id}`,
  TRACKING_CONTAINER: (id: string) => `/tracking/container/${id}`,
  TRACKING_HISTORY: (id: string) => `/tracking/shipment/${id}/history`,
  TRACKING_UPDATE: (id: string) => `/tracking/shipment/${id}/update`,
  TRACKING_SUMMARY: '/tracking/summary',

  // Invoices
  INVOICES: '/invoices',
  INVOICE_BY_ID: (id: string) => `/invoices/${id}`,
  INVOICES_BY_SHIPMENT: (shipmentId: string) => `/invoices/shipment/${shipmentId}`,

  // Documents
  DOCUMENTS: '/documents',
  DOCUMENT_BY_ID: (id: string) => `/documents/${id}`,
  DOCUMENTS_BY_SHIPMENT: (shipmentId: string) => `/documents/shipment/${shipmentId}`,

  // Alerts
  ALERTS: '/alerts',
  ALERT_BY_ID: (id: string) => `/alerts/${id}`,
  ALERT_READ: (id: string) => `/alerts/${id}/read`,

  // Insurance
  INSURANCE: '/insurance',
  INSURANCE_BY_ID: (id: string) => `/insurance/${id}`,
  INSURANCE_BY_SHIPMENT: (shipmentId: string) => `/insurance/shipment/${shipmentId}`,

  // Reports
  DASHBOARD_STATS: '/reports/dashboard',
  SHIPMENT_REPORT: '/reports/shipments',

  // Health & Metrics
  HEALTH: '/health',
  READY: '/ready',
  METRICS: '/metrics',
  METRICS_INFO: '/metrics/info',
} as const;

// API Configuration
export const API_CONFIG = {
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 2,
  RETRY_DELAY: 1000, // 1 second
  CACHE_STALE_TIME: 5 * 60 * 1000, // 5 minutes
  REFETCH_INTERVAL: {
    TRACKING: 30000, // 30 seconds
    DASHBOARD: 60000, // 1 minute
    ALERTS: 60000, // 1 minute
  },
} as const;

// HTTP Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
} as const;

// Request Headers
export const HEADERS = {
  CONTENT_TYPE: 'Content-Type',
  AUTHORIZATION: 'Authorization',
  ACCEPT: 'Accept',
  ACCEPT_VERSION: 'Accept-Version',
  API_VERSION: 'X-API-Version',
} as const;

export const CONTENT_TYPES = {
  JSON: 'application/json',
  FORM_DATA: 'multipart/form-data',
  URL_ENCODED: 'application/x-www-form-urlencoded',
} as const;


