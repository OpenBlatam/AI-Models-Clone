import { useCallback, useState } from 'react';

/**
 * Custom hook for managing async operations with loading and error states
 * @template T - The type of data returned by the async function
 */
export function useAsync<T>() {
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    const execute = useCallback(async (asyncFn: () => Promise<T>) => {
        setLoading(true);
        setError(null);
        try {
            const result = await asyncFn();
            setData(result);
            return result;
        } catch (err) {
            const error = err instanceof Error ? err : new Error(String(err));
            setError(error);
            throw error;
        } finally {
            setLoading(false);
        }
    }, []);

    const reset = useCallback(() => {
        setData(null);
        setError(null);
        setLoading(false);
    }, []);

    return { data, loading, error, execute, reset };
}

/**
 * Custom hook for debounced values
 * @param value - The value to debounce
 * @param delay - Delay in milliseconds
 */
export function useDebounce<T>(value: T, delay: number): T {
    const [debouncedValue, setDebouncedValue] = useState(value);

    useState(() => {
        const timer = setTimeout(() => setDebouncedValue(value), delay);
        return () => clearTimeout(timer);
    });

    return debouncedValue;
}

/**
 * Custom hook for toggle state
 * @param initialValue - Initial toggle value
 */
export function useToggle(initialValue = false) {
    const [value, setValue] = useState(initialValue);

    const toggle = useCallback(() => setValue((v) => !v), []);
    const setTrue = useCallback(() => setValue(true), []);
    const setFalse = useCallback(() => setValue(false), []);

    return { value, toggle, setTrue, setFalse, setValue };
}

/**
 * Custom hook for previous value
 * @param value - Current value
 */
export function usePrevious<T>(value: T): T | undefined {
    const [current, setCurrent] = useState<T>(value);
    const [previous, setPrevious] = useState<T | undefined>(undefined);

    if (value !== current) {
        setPrevious(current);
        setCurrent(value);
    }

    return previous;
}
