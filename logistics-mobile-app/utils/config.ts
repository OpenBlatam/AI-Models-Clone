import Constants from 'expo-constants';

export const API_URL =
  Constants.expoConfig?.extra?.apiUrl || process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8030';

export const API_TIMEOUT = 30000; // 30 seconds

export const APP_VERSION = Constants.expoConfig?.version || '1.0.0';

export const IS_DEV = __DEV__;


