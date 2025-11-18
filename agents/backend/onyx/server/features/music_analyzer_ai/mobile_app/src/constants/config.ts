import Constants from 'expo-constants';

export const API_BASE_URL =
  Constants.expoConfig?.extra?.apiUrl || 'http://localhost:8010';

export const API_ENDPOINTS = {
  SEARCH: '/music/search',
  ANALYZE: '/music/analyze',
  ANALYZE_BY_ID: (trackId: string) => `/music/analyze/${trackId}`,
  TRACK_INFO: (trackId: string) => `/music/track/${trackId}/info`,
  AUDIO_FEATURES: (trackId: string) => `/music/track/${trackId}/audio-features`,
  AUDIO_ANALYSIS: (trackId: string) => `/music/track/${trackId}/audio-analysis`,
  RECOMMENDATIONS: (trackId: string) =>
    `/music/track/${trackId}/recommendations`,
  COMPARE: '/music/compare',
  COACHING: '/music/coaching',
  HEALTH: '/music/health',
  HISTORY: '/music/history',
  HISTORY_STATS: '/music/history/stats',
  FAVORITES: '/music/favorites',
  FAVORITES_STATS: '/music/favorites/stats',
  EXPORT: (trackId: string, format?: string) =>
    `/music/export/${trackId}${format ? `?format=${format}` : ''}`,
  CONTEXTUAL_RECOMMENDATIONS: '/music/recommendations/contextual',
  TIME_OF_DAY_RECOMMENDATIONS: '/music/recommendations/time-of-day',
  ACTIVITY_RECOMMENDATIONS: '/music/recommendations/activity',
  MOOD_RECOMMENDATIONS: '/music/recommendations/mood',
  DISCOVERY_SIMILAR_ARTISTS: '/music/discovery/similar-artists',
  DISCOVERY_UNDERGROUND: '/music/discovery/underground',
  DISCOVERY_MOOD_TRANSITION: '/music/discovery/mood-transition',
  DISCOVERY_FRESH: '/music/discovery/fresh',
  ARTIST_COMPARE: '/music/artists/compare',
  ARTIST_EVOLUTION: '/music/artists/evolution',
  TRENDS_POPULARITY: '/music/trends/popularity',
  TRENDS_ARTISTS: '/music/trends/artists',
} as const;

export const COLORS = {
  primary: '#6366f1',
  primaryDark: '#4f46e5',
  secondary: '#8b5cf6',
  background: '#0f172a',
  surface: '#1e293b',
  surfaceLight: '#334155',
  text: '#f1f5f9',
  textSecondary: '#cbd5e1',
  error: '#ef4444',
  success: '#10b981',
  warning: '#f59e0b',
  info: '#3b82f6',
} as const;

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

export const BORDER_RADIUS = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
} as const;

export const TYPOGRAPHY = {
  h1: {
    fontSize: 32,
    fontWeight: '700' as const,
    lineHeight: 40,
  },
  h2: {
    fontSize: 24,
    fontWeight: '600' as const,
    lineHeight: 32,
  },
  h3: {
    fontSize: 20,
    fontWeight: '600' as const,
    lineHeight: 28,
  },
  body: {
    fontSize: 16,
    fontWeight: '400' as const,
    lineHeight: 24,
  },
  bodySmall: {
    fontSize: 14,
    fontWeight: '400' as const,
    lineHeight: 20,
  },
  caption: {
    fontSize: 12,
    fontWeight: '400' as const,
    lineHeight: 16,
  },
} as const;

