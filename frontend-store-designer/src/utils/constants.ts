export const ROUTES = {
  HOME: '/',
  CHAT: '/chat',
  DESIGN: '/design',
  DESIGNS: '/designs',
  DASHBOARD: '/dashboard',
} as const

export const QUERY_KEYS = {
  DESIGNS: ['designs'] as const,
  DESIGN: (id: string) => ['design', id] as const,
  CHAT: (id: string) => ['chat', id] as const,
  ANALYSIS: (id: string) => ['analysis', id] as const,
  DASHBOARD: ['dashboard'] as const,
} as const

export const STORAGE_KEYS = {
  THEME: 'theme',
  PREFERENCES: 'preferences',
  RECENT_DESIGNS: 'recent_designs',
} as const

export const API_TIMEOUT = 30000
export const CACHE_TTL = 5 * 60 * 1000 // 5 minutos


