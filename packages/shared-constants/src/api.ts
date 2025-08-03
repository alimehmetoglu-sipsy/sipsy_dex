// API-related constants

// API base paths
export const API_PATHS = {
  BASE: '/api/v1',
  AUTH: '/api/v1/auth',
  AGENTS: '/api/v1/agents',
  COMMANDS: '/api/v1/commands',
  SYSTEM: '/api/v1/system',
  SETTINGS: '/api/v1/settings',
  USERS: '/api/v1/users',
  WEBHOOKS: '/api/v1/webhooks',
  AI: '/api/v1/ai'
} as const;

// HTTP status codes
export const HTTP_STATUS = {
  // Success
  OK: 200,
  CREATED: 201,
  ACCEPTED: 202,
  NO_CONTENT: 204,
  
  // Client errors
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  METHOD_NOT_ALLOWED: 405,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  
  // Server errors
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504
} as const;

// HTTP methods
export const HTTP_METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  PATCH: 'PATCH',
  DELETE: 'DELETE',
  HEAD: 'HEAD',
  OPTIONS: 'OPTIONS'
} as const;

// Content types
export const CONTENT_TYPES = {
  JSON: 'application/json',
  FORM_DATA: 'multipart/form-data',
  URL_ENCODED: 'application/x-www-form-urlencoded',
  TEXT_PLAIN: 'text/plain',
  OCTET_STREAM: 'application/octet-stream'
} as const;

// API headers
export const API_HEADERS = {
  AUTHORIZATION: 'Authorization',
  CONTENT_TYPE: 'Content-Type',
  REQUEST_ID: 'X-Request-ID',
  API_VERSION: 'X-API-Version',
  RATE_LIMIT_REMAINING: 'X-Rate-Limit-Remaining',
  RATE_LIMIT_RESET: 'X-Rate-Limit-Reset',
  CORRELATION_ID: 'X-Correlation-ID',
  USER_AGENT: 'User-Agent'
} as const;

// API error codes
export const API_ERROR_CODES = {
  // Authentication errors
  AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR: 'AUTHORIZATION_ERROR',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  TOKEN_INVALID: 'TOKEN_INVALID',
  
  // Validation errors
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  REQUIRED_FIELD_MISSING: 'REQUIRED_FIELD_MISSING',
  INVALID_FORMAT: 'INVALID_FORMAT',
  VALUE_OUT_OF_RANGE: 'VALUE_OUT_OF_RANGE',
  
  // Resource errors
  RESOURCE_NOT_FOUND: 'RESOURCE_NOT_FOUND',
  RESOURCE_CONFLICT: 'RESOURCE_CONFLICT',
  RESOURCE_LOCKED: 'RESOURCE_LOCKED',
  
  // Operation errors
  OPERATION_FAILED: 'OPERATION_FAILED',
  OPERATION_TIMEOUT: 'OPERATION_TIMEOUT',
  OPERATION_CANCELLED: 'OPERATION_CANCELLED',
  
  // System errors
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
  DATABASE_ERROR: 'DATABASE_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR',
  
  // Rate limiting
  RATE_LIMIT_EXCEEDED: 'RATE_LIMIT_EXCEEDED',
  
  // Agent errors
  AGENT_OFFLINE: 'AGENT_OFFLINE',
  AGENT_BUSY: 'AGENT_BUSY',
  AGENT_ERROR: 'AGENT_ERROR',
  
  // Command errors
  COMMAND_FAILED: 'COMMAND_FAILED',
  COMMAND_TIMEOUT: 'COMMAND_TIMEOUT',
  COMMAND_INVALID: 'COMMAND_INVALID',
  
  // File errors
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',
  FILE_TYPE_NOT_ALLOWED: 'FILE_TYPE_NOT_ALLOWED',
  FILE_UPLOAD_FAILED: 'FILE_UPLOAD_FAILED'
} as const;

// API timeouts (in milliseconds)
export const API_TIMEOUTS = {
  DEFAULT_REQUEST: 30000, // 30 seconds
  LONG_RUNNING: 300000, // 5 minutes
  FILE_UPLOAD: 600000, // 10 minutes
  HEALTH_CHECK: 5000, // 5 seconds
  AUTHENTICATION: 10000 // 10 seconds
} as const;

// Pagination defaults
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 25,
  MAX_LIMIT: 100,
  VALID_SORT_ORDERS: ['asc', 'desc']
} as const;

// API versioning
export const API_VERSIONS = {
  V1: 'v1',
  CURRENT: 'v1'
} as const;

// Response formats
export const RESPONSE_FORMATS = {
  JSON: 'json',
  CSV: 'csv',
  XLSX: 'xlsx',
  PDF: 'pdf'
} as const;

// File upload constraints
export const FILE_UPLOAD = {
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_EXTENSIONS: ['.exe', '.msi', '.zip', '.ps1', '.bat', '.cmd', '.txt', '.log'],
  CHUNK_SIZE: 1024 * 1024, // 1MB chunks
  MAX_CONCURRENT_UPLOADS: 3
} as const;

// Request ID configuration
export const REQUEST_ID = {
  HEADER_NAME: 'X-Request-ID',
  LENGTH: 16,
  CHARSET: 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
} as const;