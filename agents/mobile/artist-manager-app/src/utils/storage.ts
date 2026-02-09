import * as SecureStore from 'react-native-encrypted-storage';
import AsyncStorage from '@react-native-async-storage/async-storage';

const STORAGE_KEYS = {
  ARTIST_ID: 'artist_id',
  API_KEY: 'api_key',
  THEME: 'theme',
} as const;

export async function getArtistId(): Promise<string | null> {
  try {
    return await SecureStore.getItem(STORAGE_KEYS.ARTIST_ID);
  } catch (error) {
    console.error('Error getting artist ID:', error);
    return null;
  }
}

export async function setArtistId(artistId: string): Promise<void> {
  try {
    await SecureStore.setItem(STORAGE_KEYS.ARTIST_ID, artistId);
  } catch (error) {
    console.error('Error setting artist ID:', error);
  }
}

export async function getApiKey(): Promise<string | null> {
  try {
    return await SecureStore.getItem(STORAGE_KEYS.API_KEY);
  } catch (error) {
    console.error('Error getting API key:', error);
    return null;
  }
}

export async function setApiKey(apiKey: string): Promise<void> {
  try {
    await SecureStore.setItem(STORAGE_KEYS.API_KEY, apiKey);
  } catch (error) {
    console.error('Error setting API key:', error);
  }
}

export async function getTheme(): Promise<'light' | 'dark' | 'auto' | null> {
  try {
    return (await AsyncStorage.getItem(STORAGE_KEYS.THEME)) as 'light' | 'dark' | 'auto' | null;
  } catch (error) {
    console.error('Error getting theme:', error);
    return null;
  }
}

export async function setTheme(theme: 'light' | 'dark' | 'auto'): Promise<void> {
  try {
    await AsyncStorage.setItem(STORAGE_KEYS.THEME, theme);
  } catch (error) {
    console.error('Error setting theme:', error);
  }
}

export async function clearStorage(): Promise<void> {
  try {
    await SecureStore.clear();
    await AsyncStorage.clear();
  } catch (error) {
    console.error('Error clearing storage:', error);
  }
}


