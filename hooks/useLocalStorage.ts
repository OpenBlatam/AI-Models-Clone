import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for managing local storage with TypeScript support
 * @param key - The local storage key
 * @param initialValue - The initial value if no value exists in storage
 * @returns [storedValue, setValue, removeValue] - Tuple with current value, setter, and remover
 */
export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((val: T) => T)) => void, () => void] {
  // State to store our value
  // Pass initial state function to useState so logic is only executed once
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // Return a wrapped version of useState's setter function that ...
  // ... persists the new value to localStorage.
  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      // Allow value to be a function so we have the same API as useState
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      
      // Save state
      setStoredValue(valueToStore);
      
      // Save to local storage
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  // Remove value from local storage
  const removeValue = useCallback(() => {
    try {
      setStoredValue(initialValue);
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(key);
      }
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  // Listen for changes to this localStorage key in other tabs/windows
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.newValue !== null) {
        try {
          setStoredValue(JSON.parse(e.newValue));
        } catch (error) {
          console.warn(`Error parsing localStorage value for key "${key}":`, error);
        }
      }
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('storage', handleStorageChange);
      return () => window.removeEventListener('storage', handleStorageChange);
    }
  }, [key]);

  return [storedValue, setValue, removeValue];
}

/**
 * Hook for managing multiple local storage values
 * @param keys - Object with key-value pairs for local storage
 * @returns Object with current values and setters
 */
export function useMultipleLocalStorage<T extends Record<string, any>>(
  keys: T
): {
  values: T;
  setValues: (newValues: Partial<T>) => void;
  resetValues: () => void;
} {
  const [values, setValues] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return keys;
    }

    const result = { ...keys };
    Object.keys(keys).forEach(key => {
      try {
        const item = window.localStorage.getItem(key);
        if (item) {
          result[key as keyof T] = JSON.parse(item);
        }
      } catch (error) {
        console.warn(`Error reading localStorage key "${key}":`, error);
      }
    });
    return result;
  });

  const setValues = useCallback((newValues: Partial<T>) => {
    const updatedValues = { ...values, ...newValues };
    setValues(updatedValues);

    if (typeof window !== 'undefined') {
      Object.entries(newValues).forEach(([key, value]) => {
        try {
          window.localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
          console.warn(`Error setting localStorage key "${key}":`, error);
        }
      });
    }
  }, [values]);

  const resetValues = useCallback(() => {
    setValues(keys);
    if (typeof window !== 'undefined') {
      Object.keys(keys).forEach(key => {
        try {
          window.localStorage.removeItem(key);
        } catch (error) {
          console.warn(`Error removing localStorage key "${key}":`, error);
        }
      });
    }
  }, [keys]);

  return { values, setValues, resetValues };
}
