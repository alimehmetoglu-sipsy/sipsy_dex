// Error handling utility functions

import { APIError } from '@dexagent/shared-types';
import { getCurrentTimestamp, generateRequestId } from './index';

/**
 * Creates a standardized API error response
 */
export function createAPIError(
  code: string,
  message: string,
  details?: Array<{ field?: string; message: string; value?: unknown }>,
  requestId?: string
): APIError {
  return {
    error: {
      code,
      message,
      details
    },
    timestamp: getCurrentTimestamp(),
    requestId: requestId || generateRequestId()
  };
}

/**
 * Creates a validation error
 */
export function createValidationError(
  field: string,
  message: string,
  value?: unknown,
  requestId?: string
): APIError {
  return createAPIError(
    'VALIDATION_ERROR',
    'Validation failed',
    [{ field, message, value }],
    requestId
  );
}

/**
 * Creates an authentication error
 */
export function createAuthError(message: string = 'Authentication required', requestId?: string): APIError {
  return createAPIError('AUTHENTICATION_ERROR', message, undefined, requestId);
}

/**
 * Creates an authorization error
 */
export function createAuthzError(message: string = 'Insufficient permissions', requestId?: string): APIError {
  return createAPIError('AUTHORIZATION_ERROR', message, undefined, requestId);
}

/**
 * Creates a not found error
 */
export function createNotFoundError(resource: string, id?: string, requestId?: string): APIError {
  const message = id ? `${resource} with ID '${id}' not found` : `${resource} not found`;
  return createAPIError('RESOURCE_NOT_FOUND', message, undefined, requestId);
}

/**
 * Creates a conflict error
 */
export function createConflictError(message: string, requestId?: string): APIError {
  return createAPIError('RESOURCE_CONFLICT', message, undefined, requestId);
}

/**
 * Creates a rate limit error
 */
export function createRateLimitError(
  limit: number,
  window: number,
  requestId?: string
): APIError {
  return createAPIError(
    'RATE_LIMIT_EXCEEDED',
    `Rate limit exceeded. Maximum ${limit} requests per ${window} seconds.`,
    undefined,
    requestId
  );
}

/**
 * Creates a timeout error
 */
export function createTimeoutError(operation: string, timeout: number, requestId?: string): APIError {
  return createAPIError(
    'OPERATION_TIMEOUT',
    `Operation '${operation}' timed out after ${timeout} seconds`,
    undefined,
    requestId
  );
}

/**
 * Creates a service unavailable error
 */
export function createServiceUnavailableError(service: string, requestId?: string): APIError {
  return createAPIError(
    'SERVICE_UNAVAILABLE',
    `Service '${service}' is currently unavailable`,
    undefined,
    requestId
  );
}

/**
 * Extracts error message from various error types
 */
export function extractErrorMessage(error: unknown): string {
  if (!error) {
    return 'Unknown error occurred';
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'object' && error !== null) {
    const errorObj = error as Record<string, unknown>;
    
    // Check for API error format
    if (errorObj.error && typeof errorObj.error === 'object') {
      const apiError = errorObj.error as Record<string, unknown>;
      if (typeof apiError.message === 'string') {
        return apiError.message;
      }
    }
    
    // Check for message property
    if (typeof errorObj.message === 'string') {
      return errorObj.message;
    }
    
    // Check for error property
    if (typeof errorObj.error === 'string') {
      return errorObj.error;
    }
  }
  
  return 'Unknown error occurred';
}

/**
 * Checks if an error is a specific type
 */
export function isErrorType(error: unknown, errorCode: string): boolean {
  if (!error || typeof error !== 'object') {
    return false;
  }
  
  const errorObj = error as Record<string, unknown>;
  
  if (errorObj.error && typeof errorObj.error === 'object') {
    const apiError = errorObj.error as Record<string, unknown>;
    return apiError.code === errorCode;
  }
  
  return false;
}

/**
 * Safely executes an async function and returns result or error
 */
export async function safeAsync<T>(
  fn: () => Promise<T>
): Promise<{ success: true; data: T } | { success: false; error: string }> {
  try {
    const data = await fn();
    return { success: true, data };
  } catch (error) {
    return { success: false, error: extractErrorMessage(error) };
  }
}

/**
 * Safely executes a synchronous function and returns result or error
 */
export function safeSync<T>(
  fn: () => T
): { success: true; data: T } | { success: false; error: string } {
  try {
    const data = fn();
    return { success: true, data };
  } catch (error) {
    return { success: false, error: extractErrorMessage(error) };
  }
}

/**
 * Retries an async operation with exponential backoff
 */
export async function retryAsync<T>(
  fn: () => Promise<T>,
  options: {
    maxAttempts?: number;
    baseDelay?: number;
    maxDelay?: number;
    backoffFactor?: number;
    shouldRetry?: (error: unknown) => boolean;
  } = {}
): Promise<T> {
  const {
    maxAttempts = 3,
    baseDelay = 1000,
    maxDelay = 10000,
    backoffFactor = 2,
    shouldRetry = () => true
  } = options;
  
  let lastError: unknown;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      if (attempt === maxAttempts || !shouldRetry(error)) {
        throw error;
      }
      
      const delay = Math.min(baseDelay * Math.pow(backoffFactor, attempt - 1), maxDelay);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError;
}

/**
 * Creates a circuit breaker for error handling
 */
export function createCircuitBreaker<T extends unknown[], R>(
  fn: (...args: T) => Promise<R>,
  options: {
    failureThreshold?: number;
    recoveryTimeout?: number;
    monitoringPeriod?: number;
  } = {}
): (...args: T) => Promise<R> {
  const {
    failureThreshold = 5,
    recoveryTimeout = 60000,
    monitoringPeriod = 10000
  } = options;
  
  let state: 'closed' | 'open' | 'half-open' = 'closed';
  let failureCount = 0;
  let lastFailureTime = 0;
  let nextAttemptTime = 0;
  
  return async (...args: T): Promise<R> => {
    const now = Date.now();
    
    // Reset failure count if monitoring period has passed
    if (now - lastFailureTime > monitoringPeriod) {
      failureCount = 0;
      if (state === 'open') {
        state = 'half-open';
      }
    }
    
    // If circuit is open, check if we should attempt recovery
    if (state === 'open') {
      if (now < nextAttemptTime) {
        throw new Error('Circuit breaker is open');
      }
      state = 'half-open';
    }
    
    try {
      const result = await fn(...args);
      
      // Success - reset state
      if (state === 'half-open') {
        state = 'closed';
        failureCount = 0;
      }
      
      return result;
    } catch (error) {
      failureCount++;
      lastFailureTime = now;
      
      // Open circuit if failure threshold reached
      if (failureCount >= failureThreshold) {
        state = 'open';
        nextAttemptTime = now + recoveryTimeout;
      }
      
      throw error;
    }
  };
}

/**
 * Wraps a function to add error context
 */
export function withErrorContext<T extends unknown[], R>(
  fn: (...args: T) => R,
  context: string | (() => string)
): (...args: T) => R {
  return (...args: T): R => {
    try {
      return fn(...args);
    } catch (error) {
      const contextMessage = typeof context === 'function' ? context() : context;
      const originalMessage = extractErrorMessage(error);
      
      const enhancedError = new Error(`${contextMessage}: ${originalMessage}`);
      if (error instanceof Error) {
        enhancedError.stack = error.stack;
      }
      
      throw enhancedError;
    }
  };
}

/**
 * Groups errors by type for bulk error handling
 */
export function groupErrors(errors: unknown[]): Record<string, unknown[]> {
  const groups: Record<string, unknown[]> = {};
  
  errors.forEach(error => {
    let type = 'unknown';
    
    if (error instanceof Error) {
      type = error.constructor.name;
    } else if (typeof error === 'object' && error !== null) {
      const errorObj = error as Record<string, unknown>;
      if (errorObj.error && typeof errorObj.error === 'object') {
        const apiError = errorObj.error as Record<string, unknown>;
        type = typeof apiError.code === 'string' ? apiError.code : 'api_error';
      }
    }
    
    if (!groups[type]) {
      groups[type] = [];
    }
    groups[type].push(error);
  });
  
  return groups;
}