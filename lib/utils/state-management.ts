import { useState, useCallback, useRef, useEffect } from 'react';

// Generic state manager
export class StateManager<T> {
  private listeners: Set<(state: T) => void> = new Set();
  private state: T;

  constructor(initialState: T) {
    this.state = initialState;
  }

  getState(): T {
    return this.state;
  }

  setState(newState: T | ((prev: T) => T)): void {
    this.state = typeof newState === 'function' 
      ? (newState as (prev: T) => T)(this.state)
      : newState;
    
    this.listeners.forEach(listener => listener(this.state));
  }

  subscribe(listener: (state: T) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }
}

// Custom hook for state management
export function useStateManager<T>(initialState: T) {
  const managerRef = useRef<StateManager<T>>();
  
  if (!managerRef.current) {
    managerRef.current = new StateManager(initialState);
  }

  const [state, setState] = useState<T>(managerRef.current.getState());

  useEffect(() => {
    return managerRef.current!.subscribe(setState);
  }, []);

  const updateState = useCallback((newState: T | ((prev: T) => T)) => {
    managerRef.current!.setState(newState);
  }, []);

  return [state, updateState] as const;
}

// Immutable state updates
export const updateState = {
  set: <T, K extends keyof T>(obj: T, key: K, value: T[K]): T => ({
    ...obj,
    [key]: value,
  }),
  
  toggle: <T, K extends keyof T>(obj: T, key: K): T => ({
    ...obj,
    [key]: !obj[key],
  }),
  
  increment: <T, K extends keyof T>(obj: T, key: K, amount: number = 1): T => ({
    ...obj,
    [key]: (obj[key] as number) + amount,
  }),
  
  append: <T, K extends keyof T>(obj: T, key: K, item: T[K] extends Array<infer U> ? U : never): T => ({
    ...obj,
    [key]: [...(obj[key] as any[]), item],
  }),
  
  remove: <T, K extends keyof T>(obj: T, key: K, index: number): T => ({
    ...obj,
    [key]: (obj[key] as any[]).filter((_, i) => i !== index),
  }),
};

// Local storage state hook
export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = useCallback((value: T | ((prev: T) => T)) => {
    try {
      const valueToStore = typeof value === 'function' 
        ? (value as (prev: T) => T)(storedValue)
        : value;
      
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  return [storedValue, setValue];
}; 