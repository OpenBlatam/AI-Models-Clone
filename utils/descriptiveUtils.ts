// Utility functions with descriptive variable names using auxiliary verbs

// Array utilities with descriptive names
export const arrayUtils = {
  // Check if array has duplicates
  hasDuplicates: <T>(array: T[]): boolean => {
    const uniqueSet = new Set(array);
    return uniqueSet.size !== array.length;
  },

  // Check if array has specific item
  hasItem: <T>(array: T[], item: T): boolean => {
    return array.includes(item);
  },

  // Check if array has items matching predicate
  hasMatchingItems: <T>(array: T[], predicate: (item: T) => boolean): boolean => {
    return array.some(predicate);
  },

  // Check if array has all items matching predicate
  hasAllMatchingItems: <T>(array: T[], predicate: (item: T) => boolean): boolean => {
    return array.every(predicate);
  },

  // Check if array is empty
  isEmpty: <T>(array: T[]): boolean => {
    return array.length === 0;
  },

  // Check if array is not empty
  isNotEmpty: <T>(array: T[]): boolean => {
    return array.length > 0;
  },

  // Check if array has single item
  hasSingleItem: <T>(array: T[]): boolean => {
    return array.length === 1;
  },

  // Check if array has multiple items
  hasMultipleItems: <T>(array: T[]): boolean => {
    return array.length > 1;
  },

  // Get items that are duplicates
  getDuplicateItems: <T>(array: T[]): T[] => {
    const seen = new Set<T>();
    const duplicates = new Set<T>();
    
    array.forEach(item => {
      if (seen.has(item)) {
        duplicates.add(item);
      } else {
        seen.add(item);
      }
    });
    
    return Array.from(duplicates);
  },

  // Get items that are unique
  getUniqueItems: <T>(array: T[]): T[] => {
    return Array.from(new Set(array));
  },

  // Get items that match predicate
  getMatchingItems: <T>(array: T[], predicate: (item: T) => boolean): T[] => {
    return array.filter(predicate);
  },

  // Get items that don't match predicate
  getNonMatchingItems: <T>(array: T[], predicate: (item: T) => boolean): T[] => {
    return array.filter(item => !predicate(item));
  },
};

// Object utilities with descriptive names
export const objectUtils = {
  // Check if object has property
  hasProperty: <T extends Record<string, any>>(obj: T, key: keyof T): boolean => {
    return key in obj;
  },

  // Check if object has all properties
  hasAllProperties: <T extends Record<string, any>>(obj: T, keys: (keyof T)[]): boolean => {
    return keys.every(key => key in obj);
  },

  // Check if object has any properties
  hasAnyProperties: <T extends Record<string, any>>(obj: T, keys: (keyof T)[]): boolean => {
    return keys.some(key => key in obj);
  },

  // Check if object is empty
  isEmpty: (obj: Record<string, any>): boolean => {
    return Object.keys(obj).length === 0;
  },

  // Check if object is not empty
  isNotEmpty: (obj: Record<string, any>): boolean => {
    return Object.keys(obj).length > 0;
  },

  // Check if object has nested property
  hasNestedProperty: (obj: Record<string, any>, path: string): boolean => {
    return path.split('.').every(key => obj && typeof obj === 'object' && key in obj);
  },

  // Get properties that exist
  getExistingProperties: <T extends Record<string, any>>(obj: T, keys: (keyof T)[]): (keyof T)[] => {
    return keys.filter(key => key in obj);
  },

  // Get properties that don't exist
  getMissingProperties: <T extends Record<string, any>>(obj: T, keys: (keyof T)[]): (keyof T)[] => {
    return keys.filter(key => !(key in obj));
  },

  // Get nested property value
  getNestedProperty: <T>(obj: Record<string, any>, path: string, defaultValue?: T): T | undefined => {
    return path.split('.').reduce((current, key) => {
      return current && typeof current === 'object' && key in current ? current[key] : defaultValue;
    }, obj as any);
  },

  // Set nested property value
  setNestedProperty: <T>(obj: Record<string, any>, path: string, value: T): Record<string, any> => {
    const keys = path.split('.');
    const result = { ...obj };
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

// String utilities with descriptive names
export const stringUtils = {
  // Check if string is empty
  isEmpty: (str: string): boolean => {
    return str.length === 0;
  },

  // Check if string is not empty
  isNotEmpty: (str: string): boolean => {
    return str.length > 0;
  },

  // Check if string has content (not just whitespace)
  hasContent: (str: string): boolean => {
    return str.trim().length > 0;
  },

  // Check if string has whitespace
  hasWhitespace: (str: string): boolean => {
    return /\s/.test(str);
  },

  // Check if string has numbers
  hasNumbers: (str: string): boolean => {
    return /\d/.test(str);
  },

  // Check if string has letters
  hasLetters: (str: string): boolean => {
    return /[a-zA-Z]/.test(str);
  },

  // Check if string has special characters
  hasSpecialCharacters: (str: string): boolean => {
    return /[!@#$%^&*(),.?":{}|<>]/.test(str);
  },

  // Check if string is valid email
  isValidEmail: (str: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(str);
  },

  // Check if string is valid URL
  isValidUrl: (str: string): boolean => {
    try {
      new URL(str);
      return true;
    } catch {
      return false;
    }
  },

  // Check if string is palindrome
  isPalindrome: (str: string): boolean => {
    const cleaned = str.toLowerCase().replace(/[^a-z0-9]/g, '');
    return cleaned === cleaned.split('').reverse().join('');
  },

  // Get words from string
  getWords: (str: string): string[] => {
    return str.trim().split(/\s+/).filter(word => word.length > 0);
  },

  // Get characters from string
  getCharacters: (str: string): string[] => {
    return str.split('');
  },

  // Get unique characters from string
  getUniqueCharacters: (str: string): string[] => {
    return Array.from(new Set(str.split('')));
  },

  // Get duplicate characters from string
  getDuplicateCharacters: (str: string): string[] => {
    const charCount: Record<string, number> = {};
    const duplicates: string[] = [];
    
    str.split('').forEach(char => {
      charCount[char] = (charCount[char] || 0) + 1;
      if (charCount[char] === 2) {
        duplicates.push(char);
      }
    });
    
    return duplicates;
  },
};

// Number utilities with descriptive names
export const numberUtils = {
  // Check if number is positive
  isPositive: (num: number): boolean => {
    return num > 0;
  },

  // Check if number is negative
  isNegative: (num: number): boolean => {
    return num < 0;
  },

  // Check if number is zero
  isZero: (num: number): boolean => {
    return num === 0;
  },

  // Check if number is even
  isEven: (num: number): boolean => {
    return num % 2 === 0;
  },

  // Check if number is odd
  isOdd: (num: number): boolean => {
    return num % 2 !== 0;
  },

  // Check if number is integer
  isInteger: (num: number): boolean => {
    return Number.isInteger(num);
  },

  // Check if number is finite
  isFinite: (num: number): boolean => {
    return Number.isFinite(num);
  },

  // Check if number is in range
  isInRange: (num: number, min: number, max: number): boolean => {
    return num >= min && num <= max;
  },

  // Check if number is between (exclusive)
  isBetween: (num: number, min: number, max: number): boolean => {
    return num > min && num < max;
  },

  // Check if number is valid percentage
  isValidPercentage: (num: number): boolean => {
    return num >= 0 && num <= 100;
  },

  // Get digits from number
  getDigits: (num: number): number[] => {
    return Math.abs(num).toString().split('').map(Number);
  },

  // Get unique digits from number
  getUniqueDigits: (num: number): number[] => {
    return Array.from(new Set(Math.abs(num).toString().split('').map(Number)));
  },

  // Get factorial of number
  getFactorial: (num: number): number => {
    if (num < 0) return NaN;
    if (num === 0 || num === 1) return 1;
    return num * numberUtils.getFactorial(num - 1);
  },

  // Get fibonacci number
  getFibonacci: (num: number): number => {
    if (num <= 1) return num;
    return numberUtils.getFibonacci(num - 1) + numberUtils.getFibonacci(num - 2);
  },
};

// Function utilities with descriptive names
export const functionUtils = {
  // Check if function is async
  isAsync: (func: Function): boolean => {
    return func.constructor.name === 'AsyncFunction';
  },

  // Check if function is generator
  isGenerator: (func: Function): boolean => {
    return func.constructor.name === 'GeneratorFunction';
  },

  // Check if function is arrow function
  isArrowFunction: (func: Function): boolean => {
    return !func.hasOwnProperty('prototype');
  },

  // Check if function has parameters
  hasParameters: (func: Function): boolean => {
    return func.length > 0;
  },

  // Check if function is pure (no side effects)
  isPure: (func: Function): boolean => {
    // This is a simplified check - in practice, determining if a function is pure is complex
    const source = func.toString();
    const hasSideEffects = /(console\.|alert\(|confirm\(|prompt\(|window\.|document\.|localStorage\.|sessionStorage\.)/.test(source);
    return !hasSideEffects;
  },

  // Get function parameters
  getParameters: (func: Function): string[] => {
    const match = func.toString().match(/\(([^)]*)\)/);
    if (!match) return [];
    return match[1].split(',').map(param => param.trim()).filter(param => param.length > 0);
  },

  // Get function name
  getName: (func: Function): string => {
    return func.name || 'anonymous';
  },

  // Get function length (number of parameters)
  getLength: (func: Function): number => {
    return func.length;
  },

  // Check if function returns promise
  returnsPromise: (func: Function): boolean => {
    const source = func.toString();
    return source.includes('async') || source.includes('Promise');
  },

  // Check if function is memoized
  isMemoized: (func: Function): boolean => {
    return func.hasOwnProperty('cache') || func.hasOwnProperty('memoized');
  },
};

// Validation utilities with descriptive names
export const validationUtils = {
  // Check if value is defined
  isDefined: (value: any): boolean => {
    return value !== undefined && value !== null;
  },

  // Check if value is undefined
  isUndefined: (value: any): boolean => {
    return value === undefined;
  },

  // Check if value is null
  isNull: (value: any): boolean => {
    return value === null;
  },

  // Check if value is truthy
  isTruthy: (value: any): boolean => {
    return !!value;
  },

  // Check if value is falsy
  isFalsy: (value: any): boolean => {
    return !value;
  },

  // Check if value is primitive
  isPrimitive: (value: any): boolean => {
    return value !== Object(value);
  },

  // Check if value is object
  isObject: (value: any): boolean => {
    return typeof value === 'object' && value !== null && !Array.isArray(value);
  },

  // Check if value is function
  isFunction: (value: any): boolean => {
    return typeof value === 'function';
  },

  // Check if value is array
  isArray: (value: any): boolean => {
    return Array.isArray(value);
  },

  // Check if value is date
  isDate: (value: any): boolean => {
    return value instanceof Date && !isNaN(value.getTime());
  },

  // Check if value is regex
  isRegex: (value: any): boolean => {
    return value instanceof RegExp;
  },

  // Check if value is error
  isError: (value: any): boolean => {
    return value instanceof Error;
  },

  // Check if value is promise
  isPromise: (value: any): boolean => {
    return value && typeof value.then === 'function';
  },

  // Check if value is iterable
  isIterable: (value: any): boolean => {
    return value && typeof value[Symbol.iterator] === 'function';
  },

  // Check if value is async iterable
  isAsyncIterable: (value: any): boolean => {
    return value && typeof value[Symbol.asyncIterator] === 'function';
  },
}; 