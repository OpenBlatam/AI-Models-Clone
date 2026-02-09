// Object Utilities

export function omit<T extends Record<string, unknown>, K extends keyof T>(
  obj: T,
  keys: K[]
): Omit<T, K> {
  const result = { ...obj };
  keys.forEach((key) => {
    delete result[key];
  });
  return result;
}

export function pick<T extends Record<string, unknown>, K extends keyof T>(
  obj: T,
  keys: K[]
): Pick<T, K> {
  const result = {} as Pick<T, K>;
  keys.forEach((key) => {
    if (key in obj) {
      result[key] = obj[key];
    }
  });
  return result;
}

export function isEmpty(obj: Record<string, unknown> | null | undefined): boolean {
  if (!obj) return true;
  return Object.keys(obj).length === 0;
}

export function isNotEmpty(obj: Record<string, unknown> | null | undefined): boolean {
  return !isEmpty(obj);
}

export function deepMerge<T extends Record<string, unknown>>(target: T, source: Partial<T>): T {
  const output = { ...target };
  
  if (isObject(target) && isObject(source)) {
    Object.keys(source).forEach((key) => {
      const sourceValue = source[key];
      const targetValue = target[key];
      
      if (isObject(sourceValue) && isObject(targetValue)) {
        output[key] = deepMerge(targetValue as Record<string, unknown>, sourceValue as Record<string, unknown>) as T[Extract<keyof T, string>];
      } else {
        output[key] = sourceValue as T[Extract<keyof T, string>];
      }
    });
  }
  
  return output;
}

export function isObject(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

export function clone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime()) as unknown as T;
  if (Array.isArray(obj)) return obj.map((item) => clone(item)) as unknown as T;
  
  const cloned = {} as T;
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      cloned[key] = clone(obj[key]);
    }
  }
  return cloned;
}

export function getNestedValue<T>(obj: Record<string, unknown>, path: string): T | undefined {
  const keys = path.split('.');
  let current: unknown = obj;
  
  for (const key of keys) {
    if (current === null || current === undefined || typeof current !== 'object') {
      return undefined;
    }
    current = (current as Record<string, unknown>)[key];
  }
  
  return current as T | undefined;
}

export function setNestedValue(
  obj: Record<string, unknown>,
  path: string,
  value: unknown
): void {
  const keys = path.split('.');
  const lastKey = keys.pop();
  if (!lastKey) return;
  
  let current: Record<string, unknown> = obj;
  for (const key of keys) {
    if (!(key in current) || typeof current[key] !== 'object' || current[key] === null) {
      current[key] = {};
    }
    current = current[key] as Record<string, unknown>;
  }
  
  current[lastKey] = value;
}

export function flattenObject(
  obj: Record<string, unknown>,
  prefix: string = '',
  separator: string = '.'
): Record<string, unknown> {
  const flattened: Record<string, unknown> = {};
  
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const newKey = prefix ? `${prefix}${separator}${key}` : key;
      const value = obj[key];
      
      if (isObject(value)) {
        Object.assign(flattened, flattenObject(value as Record<string, unknown>, newKey, separator));
      } else {
        flattened[newKey] = value;
      }
    }
  }
  
  return flattened;
}

export function keysOf<T extends Record<string, unknown>>(obj: T): Array<keyof T> {
  return Object.keys(obj) as Array<keyof T>;
}

export function valuesOf<T extends Record<string, unknown>>(obj: T): T[keyof T][] {
  return Object.values(obj);
}

export function entriesOf<T extends Record<string, unknown>>(obj: T): [keyof T, T[keyof T]][] {
  return Object.entries(obj) as [keyof T, T[keyof T]][];
}


