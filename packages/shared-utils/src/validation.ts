// Validation utility functions

/**
 * Validates an agent ID format
 */
export function validateAgentId(agentId: string): boolean {
  if (!agentId || typeof agentId !== 'string') {
    return false;
  }
  
  // Agent ID should be at least 3 characters and contain only alphanumeric, hyphens, underscores
  return /^[a-zA-Z0-9_-]{3,}$/.test(agentId);
}

/**
 * Validates an email address
 */
export function validateEmail(email: string): boolean {
  if (!email || typeof email !== 'string') {
    return false;
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email.trim());
}

/**
 * Validates a hostname
 */
export function validateHostname(hostname: string): boolean {
  if (!hostname || typeof hostname !== 'string') {
    return false;
  }
  
  // RFC 1123 hostname validation
  const hostnameRegex = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
  return hostname.length <= 253 && hostnameRegex.test(hostname);
}

/**
 * Validates an IP address (IPv4 or IPv6)
 */
export function validateIPAddress(ip: string): boolean {
  if (!ip || typeof ip !== 'string') {
    return false;
  }
  
  // IPv4 validation
  const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  if (ipv4Regex.test(ip)) {
    return true;
  }
  
  // IPv6 validation (simplified)
  const ipv6Regex = /^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$/;
  return ipv6Regex.test(ip);
}

/**
 * Validates a port number
 */
export function validatePort(port: number): boolean {
  return Number.isInteger(port) && port >= 1 && port <= 65535;
}

/**
 * Validates a username
 */
export function validateUsername(username: string): boolean {
  if (!username || typeof username !== 'string') {
    return false;
  }
  
  // Username: 3-50 characters, alphanumeric, underscores, hyphens
  return /^[a-zA-Z0-9_-]{3,50}$/.test(username);
}

/**
 * Validates a password strength
 */
export function validatePasswordStrength(password: string): {
  isValid: boolean;
  score: number;
  requirements: {
    length: boolean;
    uppercase: boolean;
    lowercase: boolean;
    numbers: boolean;
    symbols: boolean;
  };
} {
  if (!password || typeof password !== 'string') {
    return {
      isValid: false,
      score: 0,
      requirements: {
        length: false,
        uppercase: false,
        lowercase: false,
        numbers: false,
        symbols: false
      }
    };
  }
  
  const requirements = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    numbers: /[0-9]/.test(password),
    symbols: /[^a-zA-Z0-9]/.test(password)
  };
  
  const score = Object.values(requirements).filter(Boolean).length;
  const isValid = score >= 4 && requirements.length;
  
  return { isValid, score, requirements };
}

/**
 * Validates a URL
 */
export function validateURL(url: string): boolean {
  if (!url || typeof url !== 'string') {
    return false;
  }
  
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validates a command name
 */
export function validateCommandName(name: string): boolean {
  if (!name || typeof name !== 'string') {
    return false;
  }
  
  // Command name: 1-100 characters, no leading/trailing spaces
  return name.trim() === name && name.length >= 1 && name.length <= 100;
}

/**
 * Validates a file path
 */
export function validateFilePath(path: string): boolean {
  if (!path || typeof path !== 'string') {
    return false;
  }
  
  // Basic file path validation (Windows and Unix)
  const invalidChars = /[<>:"|?*\x00-\x1f]/;
  return !invalidChars.test(path) && path.length <= 260;
}

/**
 * Validates a cron expression
 */
export function validateCronExpression(expression: string): boolean {
  if (!expression || typeof expression !== 'string') {
    return false;
  }
  
  const parts = expression.trim().split(/\s+/);
  if (parts.length !== 5 && parts.length !== 6) {
    return false;
  }
  
  // Basic cron validation (simplified)
  const cronRegex = /^(\*|[0-5]?\d)(\s+(\*|[01]?\d|2[0-3]))(\s+(\*|[0-2]?\d|3[01]))(\s+(\*|[0-9]|1[0-2]))(\s+(\*|[0-6]))(\s+(\*|[12]\d{3}))?$/;
  return cronRegex.test(expression);
}

/**
 * Validates JSON string
 */
export function validateJSON(jsonString: string): boolean {
  if (!jsonString || typeof jsonString !== 'string') {
    return false;
  }
  
  try {
    JSON.parse(jsonString);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validates a timeout value in seconds
 */
export function validateTimeout(timeout: number): boolean {
  return Number.isInteger(timeout) && timeout > 0 && timeout <= 3600; // Max 1 hour
}

/**
 * Sanitizes a string for safe display
 */
export function sanitizeString(input: string): string {
  if (!input || typeof input !== 'string') {
    return '';
  }
  
  return input
    .replace(/[<>]/g, '') // Remove angle brackets
    .replace(/[&]/g, '&amp;') // Escape ampersands
    .replace(/["']/g, '') // Remove quotes
    .trim();
}

/**
 * Validates and sanitizes user input
 */
export function validateAndSanitizeInput(
  input: string,
  options: {
    maxLength?: number;
    allowHTML?: boolean;
    required?: boolean;
  } = {}
): { isValid: boolean; sanitized: string; errors: string[] } {
  const { maxLength = 1000, allowHTML = false, required = false } = options;
  const errors: string[] = [];
  
  if (!input || typeof input !== 'string') {
    if (required) {
      errors.push('Input is required');
    }
    return { isValid: !required, sanitized: '', errors };
  }
  
  let sanitized = input.trim();
  
  if (sanitized.length === 0 && required) {
    errors.push('Input cannot be empty');
  }
  
  if (sanitized.length > maxLength) {
    errors.push(`Input exceeds maximum length of ${maxLength} characters`);
    sanitized = sanitized.substring(0, maxLength);
  }
  
  if (!allowHTML) {
    sanitized = sanitized.replace(/<[^>]*>/g, ''); // Strip HTML tags
  }
  
  return { isValid: errors.length === 0, sanitized, errors };
}