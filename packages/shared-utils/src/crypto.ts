// Crypto utility functions

/**
 * Generates a simple hash from a string using the djb2 algorithm
 */
export function simpleHash(str: string): string {
  if (!str || typeof str !== 'string') {
    return '0';
  }
  
  let hash = 5381;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) + str.charCodeAt(i);
  }
  
  return Math.abs(hash).toString(16);
}

/**
 * Encodes a string to Base64
 */
export function encodeBase64(str: string): string {
  if (!str || typeof str !== 'string') {
    return '';
  }
  
  try {
    // Use built-in btoa if available (browser)
    if (typeof btoa !== 'undefined') {
      return btoa(str);
    }
    
    // Node.js implementation
    return Buffer.from(str, 'utf-8').toString('base64');
  } catch {
    // Fallback manual implementation
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
    let result = '';
    let i = 0;
    
    while (i < str.length) {
      const byte1 = str.charCodeAt(i++);
      const byte2 = i < str.length ? str.charCodeAt(i++) : 0;
      const byte3 = i < str.length ? str.charCodeAt(i++) : 0;
      
      const bitmap = (byte1 << 16) | (byte2 << 8) | byte3;
      
      result += chars.charAt((bitmap >> 18) & 63);
      result += chars.charAt((bitmap >> 12) & 63);
      result += i - 2 < str.length ? chars.charAt((bitmap >> 6) & 63) : '=';
      result += i - 1 < str.length ? chars.charAt(bitmap & 63) : '=';
    }
    
    return result;
  }
}

/**
 * Decodes a Base64 string
 */
export function decodeBase64(base64: string): string {
  if (!base64 || typeof base64 !== 'string') {
    return '';
  }
  
  try {
    // Use built-in atob if available (browser)
    if (typeof atob !== 'undefined') {
      return atob(base64);
    }
    
    // Node.js implementation
    return Buffer.from(base64, 'base64').toString('utf-8');
  } catch {
    // Fallback manual implementation
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
    let result = '';
    let i = 0;
    
    base64 = base64.replace(/[^A-Za-z0-9+/]/g, '');
    
    while (i < base64.length) {
      const encoded1 = chars.indexOf(base64.charAt(i++));
      const encoded2 = chars.indexOf(base64.charAt(i++));
      const encoded3 = chars.indexOf(base64.charAt(i++));
      const encoded4 = chars.indexOf(base64.charAt(i++));
      
      const bitmap = (encoded1 << 18) | (encoded2 << 12) | (encoded3 << 6) | encoded4;
      
      result += String.fromCharCode((bitmap >> 16) & 255);
      if (encoded3 !== 64) result += String.fromCharCode((bitmap >> 8) & 255);
      if (encoded4 !== 64) result += String.fromCharCode(bitmap & 255);
    }
    
    return result;
  }
}

/**
 * Simple XOR cipher for basic obfuscation (not secure!)
 */
export function xorCipher(text: string, key: string): string {
  if (!text || !key || typeof text !== 'string' || typeof key !== 'string') {
    return text || '';
  }
  
  let result = '';
  for (let i = 0; i < text.length; i++) {
    result += String.fromCharCode(
      text.charCodeAt(i) ^ key.charCodeAt(i % key.length)
    );
  }
  
  return result;
}

/**
 * Generates a simple checksum for data integrity
 */
export function checksum(data: string): string {
  if (!data || typeof data !== 'string') {
    return '0';
  }
  
  let sum = 0;
  for (let i = 0; i < data.length; i++) {
    sum += data.charCodeAt(i);
  }
  
  return sum.toString(16);
}

/**
 * Compares two strings in constant time to prevent timing attacks
 */
export function constantTimeCompare(a: string, b: string): boolean {
  if (typeof a !== 'string' || typeof b !== 'string') {
    return false;
  }
  
  if (a.length !== b.length) {
    return false;
  }
  
  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  
  return result === 0;
}

/**
 * Sanitizes sensitive data for logging
 */
export function sanitizeForLogging(obj: Record<string, unknown>): Record<string, unknown> {
  const sensitiveKeys = [
    'password',
    'passwd',
    'pwd',
    'secret',
    'token',
    'auth',
    'authorization',
    'key',
    'apikey',
    'api_key',
    'private',
    'credential',
    'credentials'
  ];
  
  const sanitized: Record<string, unknown> = {};
  
  for (const [key, value] of Object.entries(obj)) {
    const lowerKey = key.toLowerCase();
    const isSensitive = sensitiveKeys.some(sensitive => lowerKey.includes(sensitive));
    
    if (isSensitive) {
      if (typeof value === 'string' && value.length > 0) {
        sanitized[key] = value.length > 4 ? 
          `${value.substring(0, 2)}${'*'.repeat(value.length - 4)}${value.substring(value.length - 2)}` :
          '*'.repeat(value.length);
      } else {
        sanitized[key] = '[REDACTED]';
      }
    } else if (value && typeof value === 'object' && !Array.isArray(value)) {
      sanitized[key] = sanitizeForLogging(value as Record<string, unknown>);
    } else {
      sanitized[key] = value;
    }
  }
  
  return sanitized;
}

/**
 * Generates a simple password hash (NOT secure for production!)
 */
export function simplePasswordHash(password: string, salt: string = ''): string {
  if (!password || typeof password !== 'string') {
    return '';
  }
  
  const combined = salt + password + salt;
  let hash = 0;
  
  for (let i = 0; i < combined.length; i++) {
    const char = combined.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  return Math.abs(hash).toString(16);
}

/**
 * Generates a random salt for password hashing
 */
export function generateSalt(length: number = 16): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let salt = '';
  
  for (let i = 0; i < length; i++) {
    salt += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  
  return salt;
}

/**
 * Obfuscates a string by replacing characters with similar-looking ones
 */
export function obfuscateString(str: string): string {
  if (!str || typeof str !== 'string') {
    return '';
  }
  
  const obfuscationMap: Record<string, string> = {
    'a': '@',
    'e': '3',
    'i': '!',
    'o': '0',
    's': '$',
    't': '7',
    'l': '1',
    'A': '@',
    'E': '3',
    'I': '!',
    'O': '0',
    'S': '$',
    'T': '7',
    'L': '1'
  };
  
  return str.split('').map(char => obfuscationMap[char] || char).join('');
}

/**
 * Creates a fingerprint from object data
 */
export function createFingerprint(data: Record<string, unknown>): string {
  const sortedKeys = Object.keys(data).sort();
  const fingerprint = sortedKeys.map(key => `${key}:${JSON.stringify(data[key])}`).join('|');
  return simpleHash(fingerprint);
}

/**
 * Validates a simple checksum
 */
export function validateChecksum(data: string, expectedChecksum: string): boolean {
  const actualChecksum = checksum(data);
  return constantTimeCompare(actualChecksum, expectedChecksum);
}

/**
 * Masks a string for display (keeping some characters visible)
 */
export function maskSensitiveData(
  data: string,
  visibleStart: number = 2,
  visibleEnd: number = 2,
  maskChar: string = '*'
): string {
  if (!data || typeof data !== 'string') {
    return '';
  }
  
  if (data.length <= visibleStart + visibleEnd) {
    return maskChar.repeat(data.length);
  }
  
  const start = data.substring(0, visibleStart);
  const end = data.substring(data.length - visibleEnd);
  const middle = maskChar.repeat(data.length - visibleStart - visibleEnd);
  
  return start + middle + end;
}