// Error-related constants

// Error categories
export const ERROR_CATEGORIES = {
  AUTHENTICATION: 'authentication',
  AUTHORIZATION: 'authorization',
  VALIDATION: 'validation',
  NETWORK: 'network',
  DATABASE: 'database',
  SYSTEM: 'system',
  AGENT: 'agent',
  COMMAND: 'command',
  FILE: 'file',
  CONFIGURATION: 'configuration',
  RATE_LIMIT: 'rate_limit',
  UNKNOWN: 'unknown'
} as const;

// Error severity levels
export const ERROR_SEVERITY = {
  LOW: 1,
  MEDIUM: 2,
  HIGH: 3,
  CRITICAL: 4
} as const;

// HTTP error codes with descriptions
export const HTTP_ERROR_CODES = {
  // Client errors (4xx)
  BAD_REQUEST: {
    code: 400,
    message: 'Bad Request',
    description: 'The request could not be understood by the server'
  },
  UNAUTHORIZED: {
    code: 401,
    message: 'Unauthorized',
    description: 'Authentication is required and has failed or has not been provided'
  },
  FORBIDDEN: {
    code: 403,
    message: 'Forbidden',
    description: 'The server understood the request but refuses to authorize it'
  },
  NOT_FOUND: {
    code: 404,
    message: 'Not Found',
    description: 'The requested resource could not be found'
  },
  METHOD_NOT_ALLOWED: {
    code: 405,
    message: 'Method Not Allowed',
    description: 'The request method is not supported for the requested resource'
  },
  CONFLICT: {
    code: 409,
    message: 'Conflict',
    description: 'The request could not be completed due to a conflict'
  },
  UNPROCESSABLE_ENTITY: {
    code: 422,
    message: 'Unprocessable Entity',
    description: 'The request was well-formed but was unable to be followed due to semantic errors'
  },
  TOO_MANY_REQUESTS: {
    code: 429,
    message: 'Too Many Requests',
    description: 'The user has sent too many requests in a given amount of time'
  },
  
  // Server errors (5xx)
  INTERNAL_SERVER_ERROR: {
    code: 500,
    message: 'Internal Server Error',
    description: 'The server encountered an unexpected condition'
  },
  BAD_GATEWAY: {
    code: 502,
    message: 'Bad Gateway',
    description: 'The server received an invalid response from an upstream server'
  },
  SERVICE_UNAVAILABLE: {
    code: 503,
    message: 'Service Unavailable',
    description: 'The server is currently unavailable'
  },
  GATEWAY_TIMEOUT: {
    code: 504,
    message: 'Gateway Timeout',
    description: 'The server did not receive a timely response from an upstream server'
  }
} as const;

// Application-specific error codes
export const APPLICATION_ERROR_CODES = {
  // Authentication errors (1000-1099)
  AUTH_INVALID_CREDENTIALS: 1001,
  AUTH_TOKEN_EXPIRED: 1002,
  AUTH_TOKEN_INVALID: 1003,
  AUTH_SESSION_EXPIRED: 1004,
  AUTH_ACCOUNT_LOCKED: 1005,
  AUTH_ACCOUNT_DISABLED: 1006,
  AUTH_PASSWORD_EXPIRED: 1007,
  AUTH_TWO_FACTOR_REQUIRED: 1008,
  AUTH_TWO_FACTOR_INVALID: 1009,
  
  // Authorization errors (1100-1199)
  AUTHZ_INSUFFICIENT_PERMISSIONS: 1101,
  AUTHZ_RESOURCE_ACCESS_DENIED: 1102,
  AUTHZ_OPERATION_NOT_ALLOWED: 1103,
  AUTHZ_ROLE_REQUIRED: 1104,
  
  // Validation errors (1200-1299)
  VALIDATION_REQUIRED_FIELD: 1201,
  VALIDATION_INVALID_FORMAT: 1202,
  VALIDATION_VALUE_TOO_SHORT: 1203,
  VALIDATION_VALUE_TOO_LONG: 1204,
  VALIDATION_VALUE_OUT_OF_RANGE: 1205,
  VALIDATION_INVALID_CHOICE: 1206,
  VALIDATION_DUPLICATE_VALUE: 1207,
  VALIDATION_INVALID_TYPE: 1208,
  
  // Agent errors (1300-1399)
  AGENT_NOT_FOUND: 1301,
  AGENT_OFFLINE: 1302,
  AGENT_BUSY: 1303,
  AGENT_CONNECTION_FAILED: 1304,
  AGENT_AUTHENTICATION_FAILED: 1305,
  AGENT_VERSION_MISMATCH: 1306,
  AGENT_REGISTRATION_FAILED: 1307,
  AGENT_HEARTBEAT_TIMEOUT: 1308,
  AGENT_DUPLICATE_ID: 1309,
  AGENT_INVALID_STATE: 1310,
  
  // Command errors (1400-1499)
  COMMAND_NOT_FOUND: 1401,
  COMMAND_EXECUTION_FAILED: 1402,
  COMMAND_TIMEOUT: 1403,
  COMMAND_CANCELLED: 1404,
  COMMAND_INVALID_SYNTAX: 1405,
  COMMAND_FORBIDDEN_OPERATION: 1406,
  COMMAND_PARAMETER_MISSING: 1407,
  COMMAND_PARAMETER_INVALID: 1408,
  COMMAND_QUEUE_FULL: 1409,
  COMMAND_ALREADY_RUNNING: 1410,
  
  // File errors (1500-1599)
  FILE_NOT_FOUND: 1501,
  FILE_ACCESS_DENIED: 1502,
  FILE_TOO_LARGE: 1503,
  FILE_INVALID_TYPE: 1504,
  FILE_UPLOAD_FAILED: 1505,
  FILE_DOWNLOAD_FAILED: 1506,
  FILE_CORRUPTED: 1507,
  FILE_ALREADY_EXISTS: 1508,
  FILE_DISK_FULL: 1509,
  
  // Database errors (1600-1699)
  DB_CONNECTION_FAILED: 1601,
  DB_QUERY_FAILED: 1602,
  DB_CONSTRAINT_VIOLATION: 1603,
  DB_RECORD_NOT_FOUND: 1604,
  DB_DUPLICATE_RECORD: 1605,
  DB_TRANSACTION_FAILED: 1606,
  DB_TIMEOUT: 1607,
  DB_MIGRATION_FAILED: 1608,
  
  // Network errors (1700-1799)
  NETWORK_CONNECTION_FAILED: 1701,
  NETWORK_TIMEOUT: 1702,
  NETWORK_DNS_RESOLUTION_FAILED: 1703,
  NETWORK_HOST_UNREACHABLE: 1704,
  NETWORK_PORT_CLOSED: 1705,
  NETWORK_SSL_ERROR: 1706,
  NETWORK_PROXY_ERROR: 1707,
  
  // System errors (1800-1899)
  SYSTEM_RESOURCE_EXHAUSTED: 1801,
  SYSTEM_DISK_FULL: 1802,
  SYSTEM_MEMORY_EXHAUSTED: 1803,
  SYSTEM_CPU_OVERLOAD: 1804,
  SYSTEM_SERVICE_UNAVAILABLE: 1805,
  SYSTEM_CONFIGURATION_ERROR: 1806,
  SYSTEM_PERMISSION_DENIED: 1807,
  SYSTEM_PROCESS_FAILED: 1808,
  
  // Configuration errors (1900-1999)
  CONFIG_INVALID_VALUE: 1901,
  CONFIG_MISSING_REQUIRED: 1902,
  CONFIG_FILE_NOT_FOUND: 1903,
  CONFIG_PARSE_ERROR: 1904,
  CONFIG_VALIDATION_FAILED: 1905,
  
  // Rate limiting errors (2000-2099)
  RATE_LIMIT_EXCEEDED: 2001,
  RATE_LIMIT_QUOTA_EXCEEDED: 2002,
  RATE_LIMIT_CONCURRENT_LIMIT: 2003
} as const;

// Error messages
export const ERROR_MESSAGES = {
  // Generic messages
  UNKNOWN_ERROR: 'An unknown error occurred',
  INTERNAL_ERROR: 'Internal server error',
  SERVICE_UNAVAILABLE: 'Service is temporarily unavailable',
  NETWORK_ERROR: 'Network connection error',
  
  // Authentication messages
  INVALID_CREDENTIALS: 'Invalid username or password',
  TOKEN_EXPIRED: 'Your session has expired. Please log in again',
  TOKEN_INVALID: 'Invalid authentication token',
  SESSION_EXPIRED: 'Your session has expired',
  ACCOUNT_LOCKED: 'Account is locked due to multiple failed login attempts',
  ACCOUNT_DISABLED: 'Account is disabled',
  
  // Authorization messages
  INSUFFICIENT_PERMISSIONS: 'You do not have permission to perform this action',
  ACCESS_DENIED: 'Access denied to this resource',
  OPERATION_NOT_ALLOWED: 'This operation is not allowed',
  
  // Agent messages
  AGENT_NOT_FOUND: 'Agent not found',
  AGENT_OFFLINE: 'Agent is currently offline',
  AGENT_BUSY: 'Agent is busy executing another command',
  AGENT_CONNECTION_FAILED: 'Failed to connect to agent',
  AGENT_AUTHENTICATION_FAILED: 'Agent authentication failed',
  
  // Command messages
  COMMAND_NOT_FOUND: 'Command not found',
  COMMAND_EXECUTION_FAILED: 'Command execution failed',
  COMMAND_TIMEOUT: 'Command execution timed out',
  COMMAND_CANCELLED: 'Command was cancelled',
  COMMAND_INVALID_SYNTAX: 'Invalid command syntax',
  COMMAND_FORBIDDEN: 'Command contains forbidden operations',
  
  // File messages
  FILE_NOT_FOUND: 'File not found',
  FILE_TOO_LARGE: 'File is too large',
  FILE_INVALID_TYPE: 'Invalid file type',
  FILE_UPLOAD_FAILED: 'File upload failed',
  FILE_ACCESS_DENIED: 'Access denied to file',
  
  // Validation messages
  REQUIRED_FIELD: 'This field is required',
  INVALID_FORMAT: 'Invalid format',
  VALUE_TOO_SHORT: 'Value is too short',
  VALUE_TOO_LONG: 'Value is too long',
  VALUE_OUT_OF_RANGE: 'Value is out of range',
  INVALID_CHOICE: 'Invalid choice',
  
  // Rate limiting messages
  RATE_LIMIT_EXCEEDED: 'Rate limit exceeded. Please try again later',
  TOO_MANY_REQUESTS: 'Too many requests. Please slow down',
  QUOTA_EXCEEDED: 'Quota exceeded for this time period'
} as const;

// User-friendly error descriptions
export const ERROR_DESCRIPTIONS = {
  [APPLICATION_ERROR_CODES.AUTH_INVALID_CREDENTIALS]: 'The username or password you entered is incorrect. Please check your credentials and try again.',
  [APPLICATION_ERROR_CODES.AUTH_TOKEN_EXPIRED]: 'Your login session has expired for security reasons. Please log in again to continue.',
  [APPLICATION_ERROR_CODES.AGENT_OFFLINE]: 'The selected agent is currently offline. Please check the agent status and try again when it comes online.',
  [APPLICATION_ERROR_CODES.COMMAND_TIMEOUT]: 'The command took too long to execute and was automatically stopped. You may want to increase the timeout or check the command.',
  [APPLICATION_ERROR_CODES.FILE_TOO_LARGE]: 'The file you are trying to upload is too large. Please choose a smaller file or compress it.',
  [APPLICATION_ERROR_CODES.RATE_LIMIT_EXCEEDED]: 'You have made too many requests in a short time. Please wait a moment before trying again.'
} as const;

// Error recovery suggestions
export const ERROR_RECOVERY_SUGGESTIONS = {
  [APPLICATION_ERROR_CODES.AUTH_INVALID_CREDENTIALS]: [
    'Check your username and password',
    'Ensure Caps Lock is not enabled',
    'Contact your administrator if you forgot your password'
  ],
  [APPLICATION_ERROR_CODES.AGENT_OFFLINE]: [
    'Check if the agent machine is powered on',
    'Verify network connectivity',
    'Restart the agent service',
    'Contact system administrator'
  ],
  [APPLICATION_ERROR_CODES.COMMAND_TIMEOUT]: [
    'Increase the command timeout value',
    'Simplify the command if possible',
    'Check if the target system is responding',
    'Split complex commands into smaller parts'
  ],
  [APPLICATION_ERROR_CODES.FILE_TOO_LARGE]: [
    'Compress the file before uploading',
    'Split large files into smaller parts',
    'Use a file sharing service for very large files',
    'Contact administrator about file size limits'
  ]
} as const;

// Error logging levels
export const LOG_LEVELS = {
  DEBUG: 'debug',
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
  CRITICAL: 'critical'
} as const;

// Error reporting configuration
export const ERROR_REPORTING = {
  // Errors that should be reported to administrators
  ADMIN_REPORTABLE: [
    APPLICATION_ERROR_CODES.SYSTEM_RESOURCE_EXHAUSTED,
    APPLICATION_ERROR_CODES.DB_CONNECTION_FAILED,
    APPLICATION_ERROR_CODES.SYSTEM_SERVICE_UNAVAILABLE,
    APPLICATION_ERROR_CODES.CONFIG_VALIDATION_FAILED
  ],
  
  // Errors that should trigger alerts
  ALERT_WORTHY: [
    APPLICATION_ERROR_CODES.SYSTEM_DISK_FULL,
    APPLICATION_ERROR_CODES.SYSTEM_MEMORY_EXHAUSTED,
    APPLICATION_ERROR_CODES.DB_CONNECTION_FAILED,
    APPLICATION_ERROR_CODES.NETWORK_CONNECTION_FAILED
  ],
  
  // Errors that should be logged but not reported
  LOG_ONLY: [
    APPLICATION_ERROR_CODES.VALIDATION_REQUIRED_FIELD,
    APPLICATION_ERROR_CODES.AUTH_INVALID_CREDENTIALS,
    APPLICATION_ERROR_CODES.AUTHZ_INSUFFICIENT_PERMISSIONS
  ]
} as const;

// Retry configuration for different error types
export const RETRY_CONFIG = {
  [ERROR_CATEGORIES.NETWORK]: {
    maxAttempts: 3,
    backoffMultiplier: 2,
    initialDelay: 1000
  },
  [ERROR_CATEGORIES.DATABASE]: {
    maxAttempts: 2,
    backoffMultiplier: 1.5,
    initialDelay: 500
  },
  [ERROR_CATEGORIES.AGENT]: {
    maxAttempts: 3,
    backoffMultiplier: 2,
    initialDelay: 2000
  },
  [ERROR_CATEGORIES.COMMAND]: {
    maxAttempts: 1,
    backoffMultiplier: 1,
    initialDelay: 0
  }
} as const;

// Circuit breaker thresholds
export const CIRCUIT_BREAKER = {
  FAILURE_THRESHOLD: 5,
  RECOVERY_TIMEOUT: 60000, // 1 minute
  MONITOR_WINDOW: 300000   // 5 minutes
} as const;