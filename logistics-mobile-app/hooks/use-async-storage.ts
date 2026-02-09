import { useState, useEffect, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export function useAsyncStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(initialValue);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function loadStoredValue() {
      try {
        const item = await AsyncStorage.getItem(key);
        if (item !== null) {
          setStoredValue(JSON.parse(item));
        }
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to load from storage'));
      } finally {
        setIsLoading(false);
      }
    }

    loadStoredValue();
  }, [key]);

  const setValue = useCallback(
    async (value: T | ((val: T) => T)) => {
      try {
        const valueToStore = value instanceof Function ? value(storedValue) : value;
        setStoredValue(valueToStore);
        await AsyncStorage.setItem(key, JSON.stringify(valueToStore));
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to save to storage'));
      }
    },
    [key, storedValue]
  );

  const removeValue = useCallback(async () => {
    try {
      await AsyncStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to remove from storage'));
    }
  }, [key, initialValue]);

  return { storedValue, setValue, removeValue, isLoading, error };
}


