import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import { STORAGE_KEYS, SECURE_STORAGE_KEYS } from '@/constants';

// AsyncStorage Helpers
export async function getStorageItem<T>(key: string): Promise<T | null> {
  try {
    const item = await AsyncStorage.getItem(key);
    if (item === null) return null;
    return JSON.parse(item) as T;
  } catch (error) {
    console.error(`Error getting storage item ${key}:`, error);
    return null;
  }
}

export async function setStorageItem<T>(key: string, value: T): Promise<boolean> {
  try {
    await AsyncStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (error) {
    console.error(`Error setting storage item ${key}:`, error);
    return false;
  }
}

export async function removeStorageItem(key: string): Promise<boolean> {
  try {
    await AsyncStorage.removeItem(key);
    return true;
  } catch (error) {
    console.error(`Error removing storage item ${key}:`, error);
    return false;
  }
}

export async function clearStorage(): Promise<boolean> {
  try {
    await AsyncStorage.clear();
    return true;
  } catch (error) {
    console.error('Error clearing storage:', error);
    return false;
  }
}

export async function getAllStorageKeys(): Promise<string[]> {
  try {
    return await AsyncStorage.getAllKeys();
  } catch (error) {
    console.error('Error getting all storage keys:', error);
    return [];
  }
}

// SecureStore Helpers
export async function getSecureItem(key: string): Promise<string | null> {
  try {
    return await SecureStore.getItemAsync(key);
  } catch (error) {
    console.error(`Error getting secure item ${key}:`, error);
    return null;
  }
}

export async function setSecureItem(key: string, value: string): Promise<boolean> {
  try {
    await SecureStore.setItemAsync(key, value);
    return true;
  } catch (error) {
    console.error(`Error setting secure item ${key}:`, error);
    return false;
  }
}

export async function removeSecureItem(key: string): Promise<boolean> {
  try {
    await SecureStore.deleteItemAsync(key);
    return true;
  } catch (error) {
    console.error(`Error removing secure item ${key}:`, error);
    return false;
  }
}

// Convenience Functions
export async function getAuthToken(): Promise<string | null> {
  return getSecureItem(SECURE_STORAGE_KEYS.AUTH_TOKEN);
}

export async function setAuthToken(token: string): Promise<boolean> {
  return setSecureItem(SECURE_STORAGE_KEYS.AUTH_TOKEN, token);
}

export async function removeAuthToken(): Promise<boolean> {
  return removeSecureItem(SECURE_STORAGE_KEYS.AUTH_TOKEN);
}

export async function getUserData<T>(): Promise<T | null> {
  return getStorageItem<T>(STORAGE_KEYS.USER_DATA);
}

export async function setUserData<T>(data: T): Promise<boolean> {
  return setStorageItem(STORAGE_KEYS.USER_DATA, data);
}

