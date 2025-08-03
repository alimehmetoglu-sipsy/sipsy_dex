// Array and object data utility functions

/**
 * Deep clones an object or array
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime()) as unknown as T;
  }
  
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as unknown as T;
  }
  
  if (typeof obj === 'object') {
    const cloned = {} as Record<string, unknown>;
    for (const key in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        cloned[key] = deepClone((obj as Record<string, unknown>)[key]);
      }
    }
    return cloned as T;
  }
  
  return obj;
}

/**
 * Deep merges two objects
 */
export function deepMerge<T extends Record<string, unknown>>(target: T, source: Partial<T>): T {
  const result = { ...target };
  
  for (const key in source) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      const sourceValue = source[key];
      const targetValue = result[key];
      
      if (
        sourceValue &&
        typeof sourceValue === 'object' &&
        !Array.isArray(sourceValue) &&
        targetValue &&
        typeof targetValue === 'object' &&
        !Array.isArray(targetValue)
      ) {
        result[key] = deepMerge(
          targetValue as Record<string, unknown>,
          sourceValue as Record<string, unknown>
        ) as T[Extract<keyof T, string>];
      } else {
        result[key] = sourceValue;
      }
    }
  }
  
  return result;
}

/**
 * Removes undefined and null values from an object
 */
export function removeEmpty<T extends Record<string, unknown>>(obj: T): Partial<T> {
  const result: Partial<T> = {};
  
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const value = obj[key];
      if (value !== undefined && value !== null) {
        if (typeof value === 'object' && !Array.isArray(value)) {
          const cleaned = removeEmpty(value as Record<string, unknown>);
          if (Object.keys(cleaned).length > 0) {
            result[key] = cleaned as T[Extract<keyof T, string>];
          }
        } else {
          result[key] = value;
        }
      }
    }
  }
  
  return result;
}

/**
 * Groups array items by a key function
 */
export function groupBy<T, K extends string | number | symbol>(
  array: T[],
  keyFn: (item: T) => K
): Record<K, T[]> {
  const groups = {} as Record<K, T[]>;
  
  array.forEach(item => {
    const key = keyFn(item);
    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(item);
  });
  
  return groups;
}

/**
 * Creates a map from array items using a key function
 */
export function keyBy<T, K extends string | number | symbol>(
  array: T[],
  keyFn: (item: T) => K
): Record<K, T> {
  const map = {} as Record<K, T>;
  
  array.forEach(item => {
    const key = keyFn(item);
    map[key] = item;
  });
  
  return map;
}

/**
 * Removes duplicates from an array
 */
export function unique<T>(array: T[], keyFn?: (item: T) => unknown): T[] {
  if (!keyFn) {
    return [...new Set(array)];
  }
  
  const seen = new Set();
  return array.filter(item => {
    const key = keyFn(item);
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

/**
 * Chunks an array into smaller arrays of specified size
 */
export function chunk<T>(array: T[], size: number): T[][] {
  if (size <= 0) {
    return [];
  }
  
  const chunks: T[][] = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  
  return chunks;
}

/**
 * Flattens a nested array to specified depth
 */
export function flatten<T>(array: unknown[], depth: number = 1): T[] {
  if (depth <= 0) {
    return array as T[];
  }
  
  return array.reduce((acc: T[], val) => {
    if (Array.isArray(val)) {
      acc.push(...flatten<T>(val, depth - 1));
    } else {
      acc.push(val as T);
    }
    return acc;
  }, []);
}

/**
 * Sorts an array by multiple criteria
 */
export function sortBy<T>(
  array: T[],
  ...criteria: Array<{
    key: (item: T) => unknown;
    direction?: 'asc' | 'desc';
  }>
): T[] {
  return [...array].sort((a, b) => {
    for (const { key, direction = 'asc' } of criteria) {
      const aVal = key(a);
      const bVal = key(b);
      
      if (aVal === bVal) {
        continue;
      }
      
      const comparison = aVal < bVal ? -1 : 1;
      return direction === 'asc' ? comparison : -comparison;
    }
    
    return 0;
  });
}

/**
 * Paginate an array
 */
export function paginate<T>(
  array: T[],
  page: number,
  pageSize: number
): {
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
} {
  const total = array.length;
  const totalPages = Math.ceil(total / pageSize);
  const startIndex = (page - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  
  return {
    data: array.slice(startIndex, endIndex),
    pagination: {
      page,
      pageSize,
      total,
      totalPages,
      hasNext: page < totalPages,
      hasPrev: page > 1
    }
  };
}

/**
 * Finds differences between two arrays
 */
export function arrayDiff<T>(
  array1: T[],
  array2: T[],
  keyFn?: (item: T) => unknown
): {
  added: T[];
  removed: T[];
  common: T[];
} {
  const getKey = keyFn || ((item: T) => item);
  
  const set1 = new Map(array1.map(item => [getKey(item), item]));
  const set2 = new Map(array2.map(item => [getKey(item), item]));
  
  const added: T[] = [];
  const removed: T[] = [];
  const common: T[] = [];
  
  // Find items in array2 but not in array1 (added)
  for (const [key, item] of set2) {
    if (set1.has(key)) {
      common.push(item);
    } else {
      added.push(item);
    }
  }
  
  // Find items in array1 but not in array2 (removed)
  for (const [key, item] of set1) {
    if (!set2.has(key)) {
      removed.push(item);
    }
  }
  
  return { added, removed, common };
}

/**
 * Picks specified properties from an object
 */
export function pick<T extends Record<string, unknown>, K extends keyof T>(
  obj: T,
  keys: K[]
): Pick<T, K> {
  const result = {} as Pick<T, K>;
  
  keys.forEach(key => {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      result[key] = obj[key];
    }
  });
  
  return result;
}

/**
 * Omits specified properties from an object
 */
export function omit<T extends Record<string, unknown>, K extends keyof T>(
  obj: T,
  keys: K[]
): Omit<T, K> {
  const result = { ...obj };
  
  keys.forEach(key => {
    delete result[key];
  });
  
  return result;
}

/**
 * Gets a nested value from an object using dot notation
 */
export function get<T>(
  obj: Record<string, unknown>,
  path: string,
  defaultValue?: T
): T | undefined {
  const keys = path.split('.');
  let current: unknown = obj;
  
  for (const key of keys) {
    if (current === null || current === undefined || typeof current !== 'object') {
      return defaultValue;
    }
    current = (current as Record<string, unknown>)[key];
  }
  
  return current !== undefined ? (current as T) : defaultValue;
}

/**
 * Sets a nested value in an object using dot notation
 */
export function set<T extends Record<string, unknown>>(
  obj: T,
  path: string,
  value: unknown
): T {
  const keys = path.split('.');
  const lastKey = keys.pop();
  
  if (!lastKey) {
    return obj;
  }
  
  let current: Record<string, unknown> = obj;
  
  for (const key of keys) {
    if (!(key in current) || typeof current[key] !== 'object' || current[key] === null) {
      current[key] = {};
    }
    current = current[key] as Record<string, unknown>;
  }
  
  current[lastKey] = value;
  return obj;
}

/**
 * Checks if an object has a nested property using dot notation
 */
export function has(obj: Record<string, unknown>, path: string): boolean {
  const keys = path.split('.');
  let current: unknown = obj;
  
  for (const key of keys) {
    if (current === null || current === undefined || typeof current !== 'object') {
      return false;
    }
    if (!(key in (current as Record<string, unknown>))) {
      return false;
    }
    current = (current as Record<string, unknown>)[key];
  }
  
  return true;
}

/**
 * Transforms object keys using a transformation function
 */
export function transformKeys<T extends Record<string, unknown>>(
  obj: T,
  transform: (key: string) => string
): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const newKey = transform(key);
      result[newKey] = obj[key];
    }
  }
  
  return result;
}

/**
 * Inverts an object (swaps keys and values)
 */
export function invert<T extends Record<string, string | number>>(obj: T): Record<string, string> {
  const result: Record<string, string> = {};
  
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      result[String(obj[key])] = key;
    }
  }
  
  return result;
}