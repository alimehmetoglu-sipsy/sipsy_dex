// String utility functions

/**
 * Capitalizes the first letter of a string
 */
export function capitalize(str: string): string {
  if (!str || typeof str !== 'string') {
    return '';
  }
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Converts string to camelCase
 */
export function toCamelCase(str: string): string {
  if (!str || typeof str !== 'string') {
    return '';
  }
  
  return str
    .replace(/(?:^\w|[A-Z]|\b\w)/g, (word, index) => {
      return index === 0 ? word.toLowerCase() : word.toUpperCase();
    })
    .replace(/\s+/g, '');
}

/**
 * Converts string to PascalCase
 */
export function toPascalCase(str: string): string {
  if (!str || typeof str !== 'string') {
    return '';
  }
  
  return str
    .replace(/(?:^\w|[A-Z]|\b\w)/g, (word) => {
      return word.toUpperCase();
    })
    .replace(/\s+/g, '');
}

/**
 * Converts string to kebab-case
 */
export function toKebabCase(str: string): string {
  if (!str || typeof str !== 'string') {
    return '';
  }
  
  return str
    .replace(/([a-z])([A-Z])/g, '$1-$2')
    .replace(/\s+/g, '-')
    .toLowerCase();
}

/**
 * Converts string to snake_case
 */
export function toSnakeCase(str: string): string {
  if (!str || typeof str !== 'string') {
    return '';
  }
  
  return str
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/\s+/g, '_')
    .toLowerCase();
}

/**
 * Truncates a string to a specified length
 */
export function truncate(str: string, length: number, suffix: string = '...'): string {
  if (!str || typeof str !== 'string') {
    return '';
  }
  
  if (str.length <= length) {
    return str;
  }
  
  return str.substring(0, length - suffix.length) + suffix;
}

/**
 * Removes extra whitespace and normalizes spaces
 */
export function normalizeWhitespace(str: string): string {
  if (!str || typeof str !== 'string') {
    return '';
  }
  
  return str.replace(/\s+/g, ' ').trim();
}

/**
 * Escapes HTML special characters
 */
export function escapeHTML(str: string): string {
  if (!str || typeof str !== 'string') {
    return '';
  }
  
  const htmlEscapes: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;'
  };
  
  return str.replace(/[&<>"'/]/g, (match) => htmlEscapes[match]);
}

/**
 * Unescapes HTML entities
 */
export function unescapeHTML(str: string): string {
  if (!str || typeof str !== 'string') {
    return '';
  }
  
  const htmlUnescapes: Record<string, string> = {
    '&amp;': '&',
    '&lt;': '<',
    '&gt;': '>',
    '&quot;': '"',
    '&#x27;': "'",
    '&#x2F;': '/'
  };
  
  return str.replace(/&(?:amp|lt|gt|quot|#x27|#x2F);/g, (match) => htmlUnescapes[match]);
}

/**
 * Slugifies a string for URLs
 */
export function slugify(str: string): string {
  if (!str || typeof str !== 'string') {
    return '';
  }
  
  return str
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '') // Remove special characters
    .replace(/[\s_-]+/g, '-') // Replace spaces and underscores with hyphens
    .replace(/^-+|-+$/g, ''); // Remove leading/trailing hyphens
}

/**
 * Extracts initials from a name
 */
export function getInitials(name: string, maxInitials: number = 2): string {
  if (!name || typeof name !== 'string') {
    return '';
  }
  
  const words = name.trim().split(/\s+/);
  const initials = words
    .slice(0, maxInitials)
    .map(word => word.charAt(0).toUpperCase())
    .join('');
  
  return initials;
}

/**
 * Masks sensitive information in a string
 */
export function maskString(str: string, visibleChars: number = 4, maskChar: string = '*'): string {
  if (!str || typeof str !== 'string') {
    return '';
  }
  
  if (str.length <= visibleChars) {
    return maskChar.repeat(str.length);
  }
  
  const visible = str.slice(-visibleChars);
  const masked = maskChar.repeat(str.length - visibleChars);
  
  return masked + visible;
}

/**
 * Checks if a string contains only ASCII characters
 */
export function isASCII(str: string): boolean {
  if (!str || typeof str !== 'string') {
    return true;
  }
  
  return /^[\x00-\x7F]*$/.test(str);
}

/**
 * Counts words in a string
 */
export function wordCount(str: string): number {
  if (!str || typeof str !== 'string') {
    return 0;
  }
  
  return str.trim().split(/\s+/).filter(word => word.length > 0).length;
}

/**
 * Extracts domain from email or URL
 */
export function extractDomain(input: string): string {
  if (!input || typeof input !== 'string') {
    return '';
  }
  
  // Email domain
  if (input.includes('@')) {
    return input.split('@')[1] || '';
  }
  
  // URL domain
  try {
    const url = new URL(input.startsWith('http') ? input : `http://${input}`);
    return url.hostname;
  } catch {
    return '';
  }
}

/**
 * Highlights search terms in text
 */
export function highlightText(
  text: string,
  searchTerm: string,
  highlightTag: string = 'mark'
): string {
  if (!text || !searchTerm || typeof text !== 'string' || typeof searchTerm !== 'string') {
    return text;
  }
  
  const regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  return text.replace(regex, `<${highlightTag}>$1</${highlightTag}>`);
}

/**
 * Generates a random string with specified options
 */
export function generateRandomString(
  length: number = 8,
  options: {
    includeUppercase?: boolean;
    includeLowercase?: boolean;
    includeNumbers?: boolean;
    includeSymbols?: boolean;
    customChars?: string;
  } = {}
): string {
  const {
    includeUppercase = true,
    includeLowercase = true,
    includeNumbers = true,
    includeSymbols = false,
    customChars
  } = options;
  
  let chars = '';
  
  if (customChars) {
    chars = customChars;
  } else {
    if (includeUppercase) chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    if (includeLowercase) chars += 'abcdefghijklmnopqrstuvwxyz';
    if (includeNumbers) chars += '0123456789';
    if (includeSymbols) chars += '!@#$%^&*()_+-=[]{}|;:,.<>?';
  }
  
  if (!chars) {
    throw new Error('No character set specified for random string generation');
  }
  
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  
  return result;
}

/**
 * Pads a string to a specified length
 */
export function padString(
  str: string,
  length: number,
  padChar: string = ' ',
  padLeft: boolean = false
): string {
  if (!str || typeof str !== 'string') {
    str = '';
  }
  
  if (str.length >= length) {
    return str;
  }
  
  const padLength = length - str.length;
  const padding = padChar.repeat(padLength);
  
  return padLeft ? padding + str : str + padding;
}