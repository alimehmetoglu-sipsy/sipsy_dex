// ID generation utility functions

import { UUID } from '@dexagent/shared-types';

/**
 * Generates a random UUID v4
 */
export function generateRequestId(): UUID {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * Generates a unique identifier for commands
 */
export function generateCommandId(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2);
  return `cmd_${timestamp}_${random}`;
}

/**
 * Generates a unique identifier for agent sessions
 */
export function generateSessionId(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2);
  return `sess_${timestamp}_${random}`;
}

/**
 * Generates a unique identifier for executions
 */
export function generateExecutionId(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2);
  return `exec_${timestamp}_${random}`;
}

/**
 * Generates a random string of specified length
 */
export function generateRandomString(length: number = 8): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

/**
 * Generates a random numeric ID
 */
export function generateNumericId(length: number = 6): string {
  const chars = '0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

/**
 * Validates if a string is a valid UUID v4
 */
export function isValidUUID(uuid: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
}

/**
 * Generates a short unique identifier (base36)
 */
export function generateShortId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substring(2, 5);
}

/**
 * Generates a correlation ID for tracking requests
 */
export function generateCorrelationId(): string {
  return `corr_${generateShortId()}`;
}

/**
 * Generates a trace ID for distributed tracing
 */
export function generateTraceId(): string {
  return `trace_${generateRequestId()}`;
}

/**
 * Extracts timestamp from time-based IDs
 */
export function extractTimestampFromId(id: string): number | null {
  try {
    // Extract timestamp part (assuming format: prefix_timestamp_random)
    const parts = id.split('_');
    if (parts.length >= 2) {
      const timestamp = parseInt(parts[1], 36);
      return isNaN(timestamp) ? null : timestamp;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Generates an agent ID with hostname prefix
 */
export function generateAgentId(hostname: string): string {
  const cleanHostname = hostname.toLowerCase().replace(/[^a-z0-9]/g, '');
  const shortId = generateShortId();
  return `agent_${cleanHostname}_${shortId}`;
}

/**
 * Generates a group ID
 */
export function generateGroupId(name: string): string {
  const cleanName = name.toLowerCase().replace(/[^a-z0-9]/g, '');
  const shortId = generateShortId();
  return `group_${cleanName}_${shortId}`;
}

/**
 * Generates a batch ID for bulk operations
 */
export function generateBatchId(): string {
  return `batch_${generateShortId()}`;
}

/**
 * Validates ID format based on prefix
 */
export function validateIdFormat(id: string, expectedPrefix?: string): boolean {
  if (!id || typeof id !== 'string') {
    return false;
  }
  
  if (expectedPrefix) {
    return id.startsWith(`${expectedPrefix}_`);
  }
  
  // General ID format validation (prefix_timestamp_random or UUID)
  return id.includes('_') || isValidUUID(id);
}