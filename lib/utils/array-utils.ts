// Array utilities with TypeScript

export const chunk = <T>(array: T[], size: number): T[][] => {
  const chunks: T[][] = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
};

export const groupBy = <T, K extends string | number>(
  array: T[],
  keyFn: (item: T) => K
): Record<K, T[]> => {
  return array.reduce((groups, item) => {
    const key = keyFn(item);
    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(item);
    return groups;
  }, {} as Record<K, T[]>);
};

export const unique = <T>(array: T[]): T[] => {
  return [...new Set(array)];
};

export const uniqueBy = <T, K>(array: T[], keyFn: (item: T) => K): T[] => {
  const seen = new Set<K>();
  return array.filter(item => {
    const key = keyFn(item);
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
};

export const shuffle = <T>(array: T[]): T[] => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};

export const sample = <T>(array: T[], count: number = 1): T[] => {
  const shuffled = shuffle(array);
  return shuffled.slice(0, count);
};

export const sampleOne = <T>(array: T[]): T | undefined => {
  return array[Math.floor(Math.random() * array.length)];
};

export const range = (start: number, end: number, step: number = 1): number[] => {
  const result: number[] = [];
  for (let i = start; i < end; i += step) {
    result.push(i);
  }
  return result;
};

export const flatten = <T>(array: (T | T[])[]): T[] => {
  return array.reduce<T[]>((flat, item) => {
    return flat.concat(Array.isArray(item) ? flatten(item) : item);
  }, []);
};

export const flattenDeep = <T>(array: any[]): T[] => {
  return array.reduce<T[]>((flat, item) => {
    return flat.concat(Array.isArray(item) ? flattenDeep(item) : item);
  }, []);
};

export const intersection = <T>(...arrays: T[][]): T[] => {
  return arrays.reduce((common, array) => {
    return common.filter(item => array.includes(item));
  });
};

export const union = <T>(...arrays: T[][]): T[] => {
  return unique(flatten(arrays));
};

export const difference = <T>(array1: T[], array2: T[]): T[] => {
  return array1.filter(item => !array2.includes(item));
};

export const symmetricDifference = <T>(array1: T[], array2: T[]): T[] => {
  return union(difference(array1, array2), difference(array2, array1));
};

export const sortBy = <T, K>(array: T[], keyFn: (item: T) => K): T[] => {
  return [...array].sort((a, b) => {
    const keyA = keyFn(a);
    const keyB = keyFn(b);
    return keyA < keyB ? -1 : keyA > keyB ? 1 : 0;
  });
};

export const sortByDesc = <T, K>(array: T[], keyFn: (item: T) => K): T[] => {
  return [...array].sort((a, b) => {
    const keyA = keyFn(a);
    const keyB = keyFn(b);
    return keyA > keyB ? -1 : keyA < keyB ? 1 : 0;
  });
};

export const partition = <T>(array: T[], predicate: (item: T) => boolean): [T[], T[]] => {
  return array.reduce<[T[], T[]]>(
    ([pass, fail], item) => {
      predicate(item) ? pass.push(item) : fail.push(item);
      return [pass, fail];
    },
    [[], []]
  );
};

export const zip = <T, U>(array1: T[], array2: U[]): [T, U][] => {
  const length = Math.min(array1.length, array2.length);
  const result: [T, U][] = [];
  for (let i = 0; i < length; i++) {
    result.push([array1[i], array2[i]]);
  }
  return result;
};

export const unzip = <T, U>(array: [T, U][]): [T[], U[]] => {
  return array.reduce<[T[], U[]]>(
    ([a, b], [x, y]) => {
      a.push(x);
      b.push(y);
      return [a, b];
    },
    [[], []]
  );
};

export const rotate = <T>(array: T[], positions: number): T[] => {
  const length = array.length;
  if (length === 0) return array;
  
  const normalizedPositions = ((positions % length) + length) % length;
  return [...array.slice(normalizedPositions), ...array.slice(0, normalizedPositions)];
};

export const countBy = <T, K extends string | number>(
  array: T[],
  keyFn: (item: T) => K
): Record<K, number> => {
  return array.reduce((counts, item) => {
    const key = keyFn(item);
    counts[key] = (counts[key] || 0) + 1;
    return counts;
  }, {} as Record<K, number>);
};

export const findLast = <T>(array: T[], predicate: (item: T, index: number) => boolean): T | undefined => {
  for (let i = array.length - 1; i >= 0; i--) {
    if (predicate(array[i], i)) {
      return array[i];
    }
  }
  return undefined;
};

export const findLastIndex = <T>(array: T[], predicate: (item: T, index: number) => boolean): number => {
  for (let i = array.length - 1; i >= 0; i--) {
    if (predicate(array[i], i)) {
      return i;
    }
  }
  return -1;
}; 