// Date and time utility functions

import { Timestamp } from '@dexagent/shared-types';

/**
 * Formats a timestamp to ISO 8601 string
 */
export function formatTimestamp(date: Date = new Date()): Timestamp {
  return date.toISOString();
}

/**
 * Parses an ISO 8601 timestamp string to Date object
 */
export function parseTimestamp(timestamp: Timestamp): Date {
  return new Date(timestamp);
}

/**
 * Gets the current timestamp as ISO 8601 string
 */
export function getCurrentTimestamp(): Timestamp {
  return formatTimestamp();
}

/**
 * Checks if a timestamp is valid
 */
export function isValidTimestamp(timestamp: string): boolean {
  const date = new Date(timestamp);
  return !isNaN(date.getTime()) && date.toISOString() === timestamp;
}

/**
 * Calculates time difference in milliseconds
 */
export function getTimeDifference(start: Timestamp, end: Timestamp): number {
  return parseTimestamp(end).getTime() - parseTimestamp(start).getTime();
}

/**
 * Calculates duration in seconds
 */
export function getDurationInSeconds(start: Timestamp, end?: Timestamp): number {
  const endTime = end ? parseTimestamp(end) : new Date();
  const startTime = parseTimestamp(start);
  return Math.round((endTime.getTime() - startTime.getTime()) / 1000);
}

/**
 * Formats duration in a human-readable format
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds}s`;
  }
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  if (minutes < 60) {
    return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  if (hours < 24) {
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
  }
  
  const days = Math.floor(hours / 24);
  const remainingHours = hours % 24;
  
  return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`;
}

/**
 * Formats a timestamp for display
 */
export function formatTimestampForDisplay(
  timestamp: Timestamp,
  options: {
    includeTime?: boolean;
    includeSeconds?: boolean;
    timeZone?: string;
    locale?: string;
  } = {}
): string {
  const {
    includeTime = true,
    includeSeconds = false,
    timeZone = 'UTC',
    locale = 'en-US'
  } = options;
  
  const date = parseTimestamp(timestamp);
  
  const dateOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    timeZone
  };
  
  if (includeTime) {
    dateOptions.hour = '2-digit';
    dateOptions.minute = '2-digit';
    
    if (includeSeconds) {
      dateOptions.second = '2-digit';
    }
  }
  
  return date.toLocaleDateString(locale, dateOptions);
}

/**
 * Gets relative time string (e.g., "2 minutes ago")
 */
export function getRelativeTime(timestamp: Timestamp, now?: Date): string {
  const date = parseTimestamp(timestamp);
  const currentTime = now || new Date();
  const diffMs = currentTime.getTime() - date.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  
  if (diffSeconds < 60) {
    return diffSeconds <= 1 ? 'just now' : `${diffSeconds} seconds ago`;
  }
  
  const diffMinutes = Math.floor(diffSeconds / 60);
  if (diffMinutes < 60) {
    return diffMinutes === 1 ? '1 minute ago' : `${diffMinutes} minutes ago`;
  }
  
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) {
    return diffHours === 1 ? '1 hour ago' : `${diffHours} hours ago`;
  }
  
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 30) {
    return diffDays === 1 ? '1 day ago' : `${diffDays} days ago`;
  }
  
  const diffMonths = Math.floor(diffDays / 30);
  if (diffMonths < 12) {
    return diffMonths === 1 ? '1 month ago' : `${diffMonths} months ago`;
  }
  
  const diffYears = Math.floor(diffMonths / 12);
  return diffYears === 1 ? '1 year ago' : `${diffYears} years ago`;
}

/**
 * Checks if a timestamp is within a time range
 */
export function isWithinTimeRange(
  timestamp: Timestamp,
  start: Timestamp,
  end: Timestamp
): boolean {
  const date = parseTimestamp(timestamp);
  const startDate = parseTimestamp(start);
  const endDate = parseTimestamp(end);
  
  return date >= startDate && date <= endDate;
}

/**
 * Adds time to a timestamp
 */
export function addTime(
  timestamp: Timestamp,
  amount: number,
  unit: 'seconds' | 'minutes' | 'hours' | 'days' = 'seconds'
): Timestamp {
  const date = parseTimestamp(timestamp);
  
  switch (unit) {
    case 'seconds':
      date.setSeconds(date.getSeconds() + amount);
      break;
    case 'minutes':
      date.setMinutes(date.getMinutes() + amount);
      break;
    case 'hours':
      date.setHours(date.getHours() + amount);
      break;
    case 'days':
      date.setDate(date.getDate() + amount);
      break;
  }
  
  return formatTimestamp(date);
}

/**
 * Gets start and end of day for a timestamp
 */
export function getDayBounds(timestamp: Timestamp): {
  startOfDay: Timestamp;
  endOfDay: Timestamp;
} {
  const date = parseTimestamp(timestamp);
  
  const startOfDay = new Date(date);
  startOfDay.setHours(0, 0, 0, 0);
  
  const endOfDay = new Date(date);
  endOfDay.setHours(23, 59, 59, 999);
  
  return {
    startOfDay: formatTimestamp(startOfDay),
    endOfDay: formatTimestamp(endOfDay)
  };
}