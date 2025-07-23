// Performance utilities with TypeScript

export class PerformanceMonitor {
  private metrics: Map<string, number[]> = new Map();

  startTimer(label: string): () => void {
    const start = performance.now();
    return () => this.endTimer(label, start);
  }

  private endTimer(label: string, start: number): void {
    const duration = performance.now() - start;
    const existing = this.metrics.get(label) || [];
    this.metrics.set(label, [...existing, duration]);
  }

  getMetrics(label?: string): Record<string, number[]> | number[] {
    if (label) {
      return this.metrics.get(label) || [];
    }
    return Object.fromEntries(this.metrics);
  }

  getAverage(label: string): number {
    const metrics = this.metrics.get(label) || [];
    return metrics.length > 0 
      ? metrics.reduce((sum, metric) => sum + metric, 0) / metrics.length 
      : 0;
  }

  clear(): void {
    this.metrics.clear();
  }
}

// Memoization utilities
export const memoize = <T extends (...args: any[]) => any>(
  fn: T,
  getKey?: (...args: Parameters<T>) => string
): T => {
  const cache = new Map<string, ReturnType<T>>();
  
  return ((...args: Parameters<T>): ReturnType<T> => {
    const key = getKey ? getKey(...args) : JSON.stringify(args);
    
    if (cache.has(key)) {
      return cache.get(key)!;
    }
    
    const result = fn(...args);
    cache.set(key, result);
    return result;
  }) as T;
};

// Weak memoization for objects
export const weakMemoize = <T extends (...args: any[]) => any>(
  fn: T
): T => {
  const cache = new WeakMap();
  
  return ((...args: Parameters<T>): ReturnType<T> => {
    const key = args[0];
    
    if (cache.has(key)) {
      return cache.get(key);
    }
    
    const result = fn(...args);
    cache.set(key, result);
    return result;
  }) as T;
};

// Intersection Observer hook
export function useIntersectionObserver(
  options: IntersectionObserverInit = {}
) {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [entry, setEntry] = useState<IntersectionObserverEntry | null>(null);
  const elementRef = useRef<Element | null>(null);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(([entry]) => {
      setIsIntersecting(entry.isIntersecting);
      setEntry(entry);
    }, options);

    observer.observe(element);

    return () => observer.disconnect();
  }, [options]);

  return { elementRef, isIntersecting, entry };
}

// Resource loading utilities
export const preloadImage = (src: string): Promise<HTMLImageElement> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
};

export const preloadScript = (src: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.onload = () => resolve();
    script.onerror = reject;
    script.src = src;
    document.head.appendChild(script);
  });
};

// Memory management
export class MemoryPool<T> {
  private pool: T[] = [];
  private factory: () => T;
  private reset: (item: T) => void;

  constructor(factory: () => T, reset: (item: T) => void) {
    this.factory = factory;
    this.reset = reset;
  }

  acquire(): T {
    return this.pool.pop() || this.factory();
  }

  release(item: T): void {
    this.reset(item);
    this.pool.push(item);
  }

  clear(): void {
    this.pool.length = 0;
  }
} 