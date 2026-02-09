import { useState, useCallback, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface StorageOptions {
  defaultValue?: any;
  serializer?: (value: any) => string;
  deserializer?: (value: string) => any;
}

interface UseOptimizedStorageReturn<T> {
  value: T | null;
  setValue: (value: T) => Promise<void>;
  removeValue: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

const defaultSerializer = JSON.stringify;
const defaultDeserializer = JSON.parse;

export const useOptimizedStorage = <T>(
  key: string,
  options: StorageOptions = {}
): UseOptimizedStorageReturn<T> => {
  const { defaultValue, serializer = defaultSerializer, deserializer = defaultDeserializer } = options;
  
  const [value, setValueState] = useState<T | null>(defaultValue ?? null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadValue = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const storedValue = await AsyncStorage.getItem(key);
        
        if (storedValue !== null) {
          const parsedValue = deserializer(storedValue);
          setValueState(parsedValue);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load value');
      } finally {
        setIsLoading(false);
      }
    };

    loadValue();
  }, [key, deserializer]);

  const setValue = useCallback(async (newValue: T) => {
    try {
      setError(null);
      const serializedValue = serializer(newValue);
      await AsyncStorage.setItem(key, serializedValue);
      setValueState(newValue);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save value');
    }
  }, [key, serializer]);

  const removeValue = useCallback(async () => {
    try {
      setError(null);
      await AsyncStorage.removeItem(key);
      setValueState(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove value');
    }
  }, [key]);

  return { value, setValue, removeValue, isLoading, error };
};

// Specialized storage hooks
export const useStringStorage = (key: string, defaultValue?: string) => {
  return useOptimizedStorage(key, {
    defaultValue,
    serializer: (value: string) => value,
    deserializer: (value: string) => value,
  });
};

export const useNumberStorage = (key: string, defaultValue?: number) => {
  return useOptimizedStorage(key, {
    defaultValue,
    serializer: (value: number) => value.toString(),
    deserializer: (value: string) => Number(value),
  });
};

export const useBooleanStorage = (key: string, defaultValue?: boolean) => {
  return useOptimizedStorage(key, {
    defaultValue,
    serializer: (value: boolean) => value.toString(),
    deserializer: (value: string) => value === 'true',
  });
};

// Storage utilities
export const storageUtils = {
  clearAll: async (): Promise<void> => {
    await AsyncStorage.clear();
  },

  getKeys: async (): Promise<string[]> => {
    return await AsyncStorage.getAllKeys();
  },

  multiGet: async (keys: string[]): Promise<[string, string | null][]> => {
    return await AsyncStorage.multiGet(keys);
  },

  multiSet: async (keyValuePairs: [string, string][]): Promise<void> => {
    await AsyncStorage.multiSet(keyValuePairs);
  },

  multiRemove: async (keys: string[]): Promise<void> => {
    await AsyncStorage.multiRemove(keys);
  },
}; 