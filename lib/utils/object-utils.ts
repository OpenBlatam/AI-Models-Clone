// Object utilities with TypeScript

export const pick = <T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> => {
  const result = {} as Pick<T, K>;
  keys.forEach(key => {
    if (key in obj) {
      result[key] = obj[key];
    }
  });
  return result;
};

export const omit = <T, K extends keyof T>(obj: T, keys: K[]): Omit<T, K> => {
  const result = { ...obj };
  keys.forEach(key => {
    delete result[key];
  });
  return result;
};

export const deepClone = <T>(obj: T): T => {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime()) as T;
  }
  
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as T;
  }
  
  if (typeof obj === 'object') {
    const cloned = {} as T;
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = deepClone(obj[key]);
      }
    }
    return cloned;
  }
  
  return obj;
};

export const merge = <T extends Record<string, any>>(target: T, ...sources: Partial<T>[]): T => {
  const result = { ...target };
  
  sources.forEach(source => {
    if (source) {
      Object.keys(source).forEach(key => {
        const value = source[key];
        if (value !== undefined) {
          if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
            result[key] = merge(result[key] || {}, value);
          } else {
            result[key] = value;
          }
        }
      });
    }
  });
  
  return result;
};

export const deepEqual = (obj1: any, obj2: any): boolean => {
  if (obj1 === obj2) return true;
  
  if (obj1 == null || obj2 == null) return obj1 === obj2;
  
  if (typeof obj1 !== typeof obj2) return false;
  
  if (typeof obj1 !== 'object') return obj1 === obj2;
  
  if (Array.isArray(obj1) !== Array.isArray(obj2)) return false;
  
  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);
  
  if (keys1.length !== keys2.length) return false;
  
  return keys1.every(key => keys2.includes(key) && deepEqual(obj1[key], obj2[key]));
};

export const flattenObject = (obj: Record<string, any>, prefix: string = ''): Record<string, any> => {
  return Object.keys(obj).reduce((acc, key) => {
    const pre = prefix.length ? prefix + '.' : '';
    
    if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
      Object.assign(acc, flattenObject(obj[key], pre + key));
    } else {
      acc[pre + key] = obj[key];
    }
    
    return acc;
  }, {} as Record<string, any>);
};

export const unflattenObject = (obj: Record<string, any>): Record<string, any> => {
  const result: Record<string, any> = {};
  
  Object.keys(obj).forEach(key => {
    const keys = key.split('.');
    let current = result;
    
    keys.forEach((k, index) => {
      if (index === keys.length - 1) {
        current[k] = obj[key];
      } else {
        current[k] = current[k] || {};
        current = current[k];
      }
    });
  });
  
  return result;
};

export const get = (obj: any, path: string, defaultValue?: any): any => {
  const keys = path.split('.');
  let result = obj;
  
  for (const key of keys) {
    if (result == null || typeof result !== 'object') {
      return defaultValue;
    }
    result = result[key];
  }
  
  return result !== undefined ? result : defaultValue;
};

export const set = (obj: any, path: string, value: any): void => {
  const keys = path.split('.');
  let current = obj;
  
  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i];
    if (!(key in current) || typeof current[key] !== 'object') {
      current[key] = {};
    }
    current = current[key];
  }
  
  current[keys[keys.length - 1]] = value;
};

export const has = (obj: any, path: string): boolean => {
  const keys = path.split('.');
  let current = obj;
  
  for (const key of keys) {
    if (current == null || typeof current !== 'object' || !(key in current)) {
      return false;
    }
    current = current[key];
  }
  
  return true;
};

export const keys = (obj: Record<string, any>): string[] => {
  return Object.keys(obj);
};

export const values = <T>(obj: Record<string, T>): T[] => {
  return Object.values(obj);
};

export const entries = <T>(obj: Record<string, T>): [string, T][] => {
  return Object.entries(obj);
};

export const fromEntries = <T>(entries: [string, T][]): Record<string, T> => {
  return Object.fromEntries(entries);
};

export const isEmpty = (obj: any): boolean => {
  if (obj == null) return true;
  if (Array.isArray(obj) || typeof obj === 'string') return obj.length === 0;
  if (obj instanceof Map || obj instanceof Set) return obj.size === 0;
  if (typeof obj === 'object') return Object.keys(obj).length === 0;
  return false;
};

export const size = (obj: any): number => {
  if (obj == null) return 0;
  if (Array.isArray(obj) || typeof obj === 'string') return obj.length;
  if (obj instanceof Map || obj instanceof Set) return obj.size;
  if (typeof obj === 'object') return Object.keys(obj).length;
  return 0;
};

export const invert = <T extends Record<string, any>>(obj: T): Record<string, string> => {
  const result: Record<string, string> = {};
  Object.keys(obj).forEach(key => {
    const value = String(obj[key]);
    result[value] = key;
  });
  return result;
};

export const mapValues = <T, U>(
  obj: Record<string, T>,
  fn: (value: T, key: string) => U
): Record<string, U> => {
  const result: Record<string, U> = {};
  Object.keys(obj).forEach(key => {
    result[key] = fn(obj[key], key);
  });
  return result;
};

export const mapKeys = <T>(
  obj: Record<string, T>,
  fn: (key: string, value: T) => string
): Record<string, T> => {
  const result: Record<string, T> = {};
  Object.keys(obj).forEach(key => {
    const newKey = fn(key, obj[key]);
    result[newKey] = obj[key];
  });
  return result;
}; 