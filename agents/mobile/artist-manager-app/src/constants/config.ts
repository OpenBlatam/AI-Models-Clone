import Constants from 'expo-constants';

const API_BASE_URL =
  Constants.expoConfig?.extra?.apiBaseUrl ||
  process.env.EXPO_PUBLIC_API_BASE_URL ||
  'http://localhost:8000';

export const Config = {
  apiBaseUrl: API_BASE_URL,
  apiPrefix: '/artist-manager',
  timeout: 30000,
  retryAttempts: 3,
  cacheTime: 1000 * 60 * 5, // 5 minutes
} as const;

export function getApiUrl(path: string): string {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${Config.apiBaseUrl}${Config.apiPrefix}${cleanPath}`;
}


