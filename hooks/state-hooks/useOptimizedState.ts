import { useState, useCallback, useMemo, useEffect } from 'react';

interface StateConfig<T> {
  initialValue: T;
  shouldPersist?: boolean;
  persistenceKey?: string;
  shouldValidate?: boolean;
  validationRules?: ((value: T) => string | null)[];
  shouldDebounce?: boolean;
  debounceDelay?: number;
}

interface StateResult<T> {
  value: T;
  setValue: (newValue: T | ((prev: T) => T)) => void;
  hasChanged: boolean;
  hasErrors: boolean;
  errors: string[];
  isDirty: boolean;
  isValid: boolean;
  reset: () => void;
  validate: () => boolean;
}

export const useOptimizedState = <T>(
  config: StateConfig<T>
): StateResult<T> => {
  // State with descriptive variable names using auxiliary verbs
  const [value, setValue] = useState<T>(config.initialValue);
  const [hasChanged, setHasChanged] = useState<boolean>(false);
  const [hasErrors, setHasErrors] = useState<boolean>(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [isDirty, setIsDirty] = useState<boolean>(false);
  const [isValid, setIsValid] = useState<boolean>(true);
  const [shouldValidate, setShouldValidate] = useState<boolean>(config.shouldValidate || false);
  const [hasBeenInitialized, setHasBeenInitialized] = useState<boolean>(false);

  // Validation function with descriptive name
  const validateValue = useCallback((val: T): { isValid: boolean; errors: string[] } => {
    if (!config.validationRules) {
      return { isValid: true, errors: [] };
    }

    const validationErrors: string[] = [];
    config.validationRules.forEach(rule => {
      const error = rule(val);
      if (error) validationErrors.push(error);
    });

    return {
      isValid: validationErrors.length === 0,
      errors: validationErrors,
    };
  }, [config.validationRules]);

  // Update state with validation
  const updateState = useCallback((newValue: T | ((prev: T) => T)) => {
    const resolvedValue = typeof newValue === 'function' ? (newValue as (prev: T) => T)(value) : newValue;
    
    setValue(resolvedValue);
    setHasChanged(true);
    setIsDirty(true);

    if (shouldValidate) {
      const validation = validateValue(resolvedValue);
      setHasErrors(!validation.isValid);
      setErrors(validation.errors);
      setIsValid(validation.isValid);
    }
  }, [value, shouldValidate, validateValue]);

  // Reset state with descriptive function name
  const resetState = useCallback(() => {
    setValue(config.initialValue);
    setHasChanged(false);
    setHasErrors(false);
    setErrors([]);
    setIsDirty(false);
    setIsValid(true);
  }, [config.initialValue]);

  // Validate current state with descriptive function name
  const validateCurrentState = useCallback((): boolean => {
    const validation = validateValue(value);
    setHasErrors(!validation.isValid);
    setErrors(validation.errors);
    setIsValid(validation.isValid);
    return validation.isValid;
  }, [value, validateValue]);

  // Initialize state with descriptive function name
  const initializeState = useCallback(async () => {
    if (config.shouldPersist && config.persistenceKey && !hasBeenInitialized) {
      try {
        // Simulate loading from storage
        const storedValue = await loadFromStorage(config.persistenceKey);
        if (storedValue !== null) {
          setValue(storedValue);
          setHasChanged(false);
          setIsDirty(false);
        }
      } catch (error) {
        console.warn('Failed to load persisted state:', error);
      }
    }
    setHasBeenInitialized(true);
  }, [config.shouldPersist, config.persistenceKey, hasBeenInitialized]);

  // Save to storage with descriptive function name
  const saveToStorage = useCallback(async (val: T) => {
    if (config.shouldPersist && config.persistenceKey) {
      try {
        // Simulate saving to storage
        await persistToStorage(config.persistenceKey, val);
      } catch (error) {
        console.warn('Failed to persist state:', error);
      }
    }
  }, [config.shouldPersist, config.persistenceKey]);

  // Debounced save with descriptive function name
  const debouncedSave = useMemo(() => {
    if (config.shouldDebounce && config.debounceDelay) {
      let timeoutId: NodeJS.Timeout;
      return (val: T) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => saveToStorage(val), config.debounceDelay);
      };
    }
    return saveToStorage;
  }, [config.shouldDebounce, config.debounceDelay, saveToStorage]);

  // Effect for persistence
  useEffect(() => {
    if (hasBeenInitialized && isDirty) {
      debouncedSave(value);
    }
  }, [value, isDirty, hasBeenInitialized, debouncedSave]);

  // Effect for initialization
  useEffect(() => {
    initializeState();
  }, [initializeState]);

  // Memoized result with descriptive property names
  const result = useMemo((): StateResult<T> => ({
    value,
    setValue: updateState,
    hasChanged,
    hasErrors,
    errors,
    isDirty,
    isValid,
    reset: resetState,
    validate: validateCurrentState,
  }), [
    value,
    updateState,
    hasChanged,
    hasErrors,
    errors,
    isDirty,
    isValid,
    resetState,
    validateCurrentState,
  ]);

  return result;
};

// Helper functions with descriptive names
const loadFromStorage = async (key: string): Promise<any> => {
  // Simulate AsyncStorage.getItem
  return new Promise((resolve) => {
    setTimeout(() => {
      const stored = localStorage.getItem(key);
      resolve(stored ? JSON.parse(stored) : null);
    }, 100);
  });
};

const persistToStorage = async (key: string, value: any): Promise<void> => {
  // Simulate AsyncStorage.setItem
  return new Promise((resolve) => {
    setTimeout(() => {
      localStorage.setItem(key, JSON.stringify(value));
      resolve();
    }, 100);
  });
};

// Specialized hooks with descriptive names
export const useOptimizedStringState = (
  initialValue: string,
  options?: Omit<StateConfig<string>, 'initialValue'>
) => {
  return useOptimizedState({
    initialValue,
    ...options,
  });
};

export const useOptimizedNumberState = (
  initialValue: number,
  options?: Omit<StateConfig<number>, 'initialValue'>
) => {
  return useOptimizedState({
    initialValue,
    ...options,
  });
};

export const useOptimizedBooleanState = (
  initialValue: boolean,
  options?: Omit<StateConfig<boolean>, 'initialValue'>
) => {
  return useOptimizedState({
    initialValue,
    ...options,
  });
};

export const useOptimizedArrayState = <T>(
  initialValue: T[],
  options?: Omit<StateConfig<T[]>, 'initialValue'>
) => {
  return useOptimizedState({
    initialValue,
    ...options,
  });
};

export const useOptimizedObjectState = <T extends Record<string, any>>(
  initialValue: T,
  options?: Omit<StateConfig<T>, 'initialValue'>
) => {
  return useOptimizedState({
    initialValue,
    ...options,
  });
}; 