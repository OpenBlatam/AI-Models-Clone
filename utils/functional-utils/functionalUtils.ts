// Functional utility functions - no classes, pure functions only

// Array utilities
export const arrayUtils = {
  // Pure function to filter array
  filter: <T>(array: T[], predicate: (item: T, index: number) => boolean): T[] => {
    return array.filter(predicate);
  },

  // Pure function to map array
  map: <T, U>(array: T[], mapper: (item: T, index: number) => U): U[] => {
    return array.map(mapper);
  },

  // Pure function to reduce array
  reduce: <T, U>(array: T[], reducer: (accumulator: U, item: T, index: number) => U, initialValue: U): U => {
    return array.reduce(reducer, initialValue);
  },

  // Pure function to find item
  find: <T>(array: T[], predicate: (item: T, index: number) => boolean): T | undefined => {
    return array.find(predicate);
  },

  // Pure function to check if all items match predicate
  every: <T>(array: T[], predicate: (item: T, index: number) => boolean): boolean => {
    return array.every(predicate);
  },

  // Pure function to check if any item matches predicate
  some: <T>(array: T[], predicate: (item: T, index: number) => boolean): boolean => {
    return array.some(predicate);
  },

  // Pure function to remove duplicates
  unique: <T>(array: T[]): T[] => {
    return [...new Set(array)];
  },

  // Pure function to chunk array
  chunk: <T>(array: T[], size: number): T[][] => {
    return array.reduce((chunks, item, index) => {
      const chunkIndex = Math.floor(index / size);
      if (!chunks[chunkIndex]) {
        chunks[chunkIndex] = [];
      }
      chunks[chunkIndex].push(item);
      return chunks;
    }, [] as T[][]);
  },

  // Pure function to flatten array
  flatten: <T>(array: T[][]): T[] => {
    return array.reduce((flat, item) => flat.concat(item), [] as T[]);
  },

  // Pure function to group array by key
  groupBy: <T, K extends string | number>(array: T[], keyExtractor: (item: T) => K): Record<K, T[]> => {
    return array.reduce((groups, item) => {
      const key = keyExtractor(item);
      if (!groups[key]) {
        groups[key] = [];
      }
      groups[key].push(item);
      return groups;
    }, {} as Record<K, T[]>);
  },
};

// Object utilities
export const objectUtils = {
  // Pure function to pick properties
  pick: <T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> => {
    return keys.reduce((picked, key) => {
      if (key in obj) {
        picked[key] = obj[key];
      }
      return picked;
    }, {} as Pick<T, K>);
  },

  // Pure function to omit properties
  omit: <T, K extends keyof T>(obj: T, keys: K[]): Omit<T, K> => {
    return Object.keys(obj).reduce((omitted, key) => {
      if (!keys.includes(key as K)) {
        (omitted as any)[key] = obj[key as keyof T];
      }
      return omitted;
    }, {} as Omit<T, K>);
  },

  // Pure function to merge objects
  merge: <T extends Record<string, any>>(...objects: T[]): T => {
    return objects.reduce((merged, obj) => ({ ...merged, ...obj }), {} as T);
  },

  // Pure function to deep clone object
  clone: <T>(obj: T): T => {
    if (obj === null || typeof obj !== 'object') {
      return obj;
    }
    if (obj instanceof Date) {
      return new Date(obj.getTime()) as T;
    }
    if (Array.isArray(obj)) {
      return obj.map(item => objectUtils.clone(item)) as T;
    }
    return Object.keys(obj).reduce((cloned, key) => {
      (cloned as any)[key] = objectUtils.clone((obj as any)[key]);
      return cloned;
    }, {} as T);
  },

  // Pure function to check if object is empty
  isEmpty: (obj: Record<string, any>): boolean => {
    return Object.keys(obj).length === 0;
  },

  // Pure function to get nested property
  get: <T>(obj: Record<string, any>, path: string, defaultValue?: T): T | undefined => {
    return path.split('.').reduce((current, key) => {
      return current && current[key] !== undefined ? current[key] : defaultValue;
    }, obj as any);
  },

  // Pure function to set nested property
  set: <T>(obj: Record<string, any>, path: string, value: T): Record<string, any> => {
    const keys = path.split('.');
    const result = objectUtils.clone(obj);
    let current = result;
    
    for (let i = 0; i < keys.length - 1; i++) {
      const key = keys[i];
      if (!(key in current) || typeof current[key] !== 'object') {
        current[key] = {};
      }
      current = current[key];
    }
    
    current[keys[keys.length - 1]] = value;
    return result;
  },
};

// String utilities
export const stringUtils = {
  // Pure function to capitalize string
  capitalize: (str: string): string => {
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  },

  // Pure function to camelCase string
  camelCase: (str: string): string => {
    return str.replace(/[-_\s]+(.)?/g, (_, char) => char ? char.toUpperCase() : '');
  },

  // Pure function to kebab-case string
  kebabCase: (str: string): string => {
    return str.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
  },

  // Pure function to snake_case string
  snakeCase: (str: string): string => {
    return str.replace(/([a-z])([A-Z])/g, '$1_$2').toLowerCase();
  },

  // Pure function to truncate string
  truncate: (str: string, length: number, suffix: string = '...'): string => {
    return str.length > length ? str.slice(0, length) + suffix : str;
  },

  // Pure function to generate random string
  random: (length: number = 8): string => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    return Array.from({ length }, () => chars.charAt(Math.floor(Math.random() * chars.length))).join('');
  },

  // Pure function to check if string is palindrome
  isPalindrome: (str: string): boolean => {
    const cleaned = str.toLowerCase().replace(/[^a-z0-9]/g, '');
    return cleaned === cleaned.split('').reverse().join('');
  },
};

// Number utilities
export const numberUtils = {
  // Pure function to clamp number
  clamp: (value: number, min: number, max: number): number => {
    return Math.min(Math.max(value, min), max);
  },

  // Pure function to round to decimal places
  round: (value: number, decimals: number = 0): number => {
    return Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals);
  },

  // Pure function to format number with commas
  format: (value: number): string => {
    return value.toLocaleString();
  },

  // Pure function to check if number is in range
  inRange: (value: number, min: number, max: number): boolean => {
    return value >= min && value <= max;
  },

  // Pure function to generate random number
  random: (min: number = 0, max: number = 1): number => {
    return Math.random() * (max - min) + min;
  },

  // Pure function to generate random integer
  randomInt: (min: number, max: number): number => {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  },
};

// Function utilities
export const functionUtils = {
  // Pure function to debounce
  debounce: <T extends (...args: any[]) => any>(func: T, delay: number): ((...args: Parameters<T>) => void) => {
    let timeoutId: NodeJS.Timeout;
    return (...args: Parameters<T>) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func(...args), delay);
    };
  },

  // Pure function to throttle
  throttle: <T extends (...args: any[]) => any>(func: T, delay: number): ((...args: Parameters<T>) => void) => {
    let lastCall = 0;
    return (...args: Parameters<T>) => {
      const now = Date.now();
      if (now - lastCall >= delay) {
        lastCall = now;
        func(...args);
      }
    };
  },

  // Pure function to memoize
  memoize: <T extends (...args: any[]) => any>(func: T): T => {
    const cache = new Map();
    return ((...args: Parameters<T>) => {
      const key = JSON.stringify(args);
      if (cache.has(key)) {
        return cache.get(key);
      }
      const result = func(...args);
      cache.set(key, result);
      return result;
    }) as T;
  },

  // Pure function to compose functions
  compose: <T>(...functions: ((arg: T) => T)[]): (arg: T) => T => {
    return (arg: T) => functions.reduceRight((result, func) => func(result), arg);
  },

  // Pure function to pipe functions
  pipe: <T>(...functions: ((arg: T) => T)[]): (arg: T) => T => {
    return (arg: T) => functions.reduce((result, func) => func(result), arg);
  },

  // Pure function to curry
  curry: <T extends (...args: any[]) => any>(func: T): any => {
    const arity = func.length;
    return function curried(...args: any[]) {
      if (args.length >= arity) {
        return func(...args);
      }
      return (...moreArgs: any[]) => curried(...args, ...moreArgs);
    };
  },
}; 