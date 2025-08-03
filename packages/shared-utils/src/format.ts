// Formatting utility functions

/**
 * Formats bytes to human-readable string
 */
export function formatBytes(bytes: number, decimals: number = 2): string {
  if (!Number.isFinite(bytes) || bytes === 0) {
    return '0 Bytes';
  }
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(Math.abs(bytes)) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Formats a number with thousand separators
 */
export function formatNumber(num: number, separator: string = ','): string {
  if (!Number.isFinite(num)) {
    return '0';
  }
  
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, separator);
}

/**
 * Formats a percentage
 */
export function formatPercentage(value: number, decimals: number = 1): string {
  if (!Number.isFinite(value)) {
    return '0%';
  }
  
  return `${value.toFixed(decimals)}%`;
}

/**
 * Formats currency
 */
export function formatCurrency(
  amount: number,
  currency: string = 'USD',
  locale: string = 'en-US'
): string {
  if (!Number.isFinite(amount)) {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency
    }).format(0);
  }
  
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency
  }).format(amount);
}

/**
 * Formats a phone number
 */
export function formatPhoneNumber(phoneNumber: string, format: string = 'US'): string {
  if (!phoneNumber || typeof phoneNumber !== 'string') {
    return '';
  }
  
  // Remove all non-numeric characters
  const cleaned = phoneNumber.replace(/\D/g, '');
  
  if (format === 'US') {
    // US format: (123) 456-7890
    if (cleaned.length === 10) {
      return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
    } else if (cleaned.length === 11 && cleaned[0] === '1') {
      return `+1 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
    }
  }
  
  return phoneNumber; // Return original if can't format
}

/**
 * Formats an IP address with validation
 */
export function formatIPAddress(ip: string): string {
  if (!ip || typeof ip !== 'string') {
    return '';
  }
  
  // IPv4 formatting
  const ipv4Parts = ip.split('.');
  if (ipv4Parts.length === 4 && ipv4Parts.every(part => {
    const num = parseInt(part, 10);
    return !isNaN(num) && num >= 0 && num <= 255;
  })) {
    return ipv4Parts.map(part => parseInt(part, 10).toString()).join('.');
  }
  
  // IPv6 formatting (basic)
  if (ip.includes(':')) {
    return ip.toLowerCase();
  }
  
  return ip;
}

/**
 * Formats a file extension
 */
export function formatFileExtension(filename: string): string {
  if (!filename || typeof filename !== 'string') {
    return '';
  }
  
  const lastDotIndex = filename.lastIndexOf('.');
  if (lastDotIndex === -1 || lastDotIndex === filename.length - 1) {
    return '';
  }
  
  return filename.slice(lastDotIndex + 1).toLowerCase();
}

/**
 * Formats a file path for display
 */
export function formatFilePath(path: string, maxLength: number = 50): string {
  if (!path || typeof path !== 'string') {
    return '';
  }
  
  if (path.length <= maxLength) {
    return path;
  }
  
  // Try to show beginning and end of path
  const separator = path.includes('/') ? '/' : '\\';
  const parts = path.split(separator);
  
  if (parts.length <= 2) {
    return `...${path.slice(-(maxLength - 3))}`;
  }
  
  const fileName = parts[parts.length - 1];
  const firstPart = parts[0];
  const available = maxLength - fileName.length - firstPart.length - 6; // 6 for separator and "..."
  
  if (available > 0) {
    return `${firstPart}${separator}...${separator}${fileName}`;
  }
  
  return `...${separator}${fileName}`;
}

/**
 * Formats a version number
 */
export function formatVersion(version: string): string {
  if (!version || typeof version !== 'string') {
    return '0.0.0';
  }
  
  // Clean version string and ensure it has at least 3 parts
  const parts = version.replace(/[^0-9.]/g, '').split('.').filter(part => part !== '');
  
  while (parts.length < 3) {
    parts.push('0');
  }
  
  return parts.slice(0, 3).join('.');
}

/**
 * Formats a command for display (truncates long commands)
 */
export function formatCommand(command: string, maxLength: number = 100): string {
  if (!command || typeof command !== 'string') {
    return '';
  }
  
  // Normalize whitespace
  const normalized = command.replace(/\s+/g, ' ').trim();
  
  if (normalized.length <= maxLength) {
    return normalized;
  }
  
  return normalized.substring(0, maxLength - 3) + '...';
}

/**
 * Formats an agent name for display
 */
export function formatAgentName(name: string, hostname?: string): string {
  if (!name || typeof name !== 'string') {
    return hostname || 'Unknown Agent';
  }
  
  // If name is just the hostname, format it nicely
  if (hostname && name.toLowerCase() === hostname.toLowerCase()) {
    return hostname.split('.')[0]; // Remove domain part
  }
  
  return name;
}

/**
 * Formats a list of items with proper grammar
 */
export function formatList(items: string[], conjunction: string = 'and'): string {
  if (!Array.isArray(items) || items.length === 0) {
    return '';
  }
  
  if (items.length === 1) {
    return items[0];
  }
  
  if (items.length === 2) {
    return `${items[0]} ${conjunction} ${items[1]}`;
  }
  
  const allButLast = items.slice(0, -1).join(', ');
  const last = items[items.length - 1];
  
  return `${allButLast}, ${conjunction} ${last}`;
}

/**
 * Formats a status with color coding (returns CSS class name)
 */
export function formatStatusClass(status: string): string {
  if (!status || typeof status !== 'string') {
    return 'status-unknown';
  }
  
  const normalizedStatus = status.toLowerCase();
  
  switch (normalizedStatus) {
    case 'online':
    case 'active':
    case 'running':
    case 'completed':
    case 'success':
      return 'status-success';
    
    case 'offline':
    case 'inactive':
    case 'stopped':
    case 'failed':
    case 'error':
      return 'status-error';
    
    case 'pending':
    case 'waiting':
    case 'queued':
      return 'status-warning';
    
    case 'connecting':
    case 'starting':
    case 'processing':
    case 'running':
      return 'status-info';
    
    default:
      return 'status-unknown';
  }
}

/**
 * Formats text for code display (preserves formatting)
 */
export function formatCode(code: string, language?: string): string {
  if (!code || typeof code !== 'string') {
    return '';
  }
  
  // Basic formatting - preserve line breaks and indentation
  return code
    .replace(/\t/g, '    ') // Convert tabs to spaces
    .replace(/\r\n/g, '\n') // Normalize line endings
    .trimEnd(); // Remove trailing whitespace
}