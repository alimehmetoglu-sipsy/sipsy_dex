// Validation-related constants

// Regular expression patterns
export const VALIDATION_PATTERNS = {
  // Email validation
  EMAIL: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  
  // Password validation (at least 8 chars, 1 uppercase, 1 lowercase, 1 number)
  PASSWORD: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/,
  
  // Username validation (alphanumeric and underscore, 3-50 chars)
  USERNAME: /^[a-zA-Z0-9_]{3,50}$/,
  
  // Agent name validation (alphanumeric, spaces, hyphens, underscores)
  AGENT_NAME: /^[a-zA-Z0-9\s\-_]{1,100}$/,
  
  // Command name validation
  COMMAND_NAME: /^[a-zA-Z0-9\s\-_()]{1,100}$/,
  
  // IP address validation
  IP_ADDRESS: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
  
  // Port validation
  PORT: /^([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$/,
  
  // URL validation
  URL: /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/,
  
  // Hostname validation
  HOSTNAME: /^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$/,
  
  // Version number validation (semantic versioning)
  VERSION: /^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-(?:(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?:[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$/,
  
  // UUID validation
  UUID: /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i,
  
  // JWT token validation
  JWT: /^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$/,
  
  // PowerShell command validation (basic)
  POWERSHELL_COMMAND: /^[^<>&|;`$]*$/,
  
  // File path validation (Windows)
  WINDOWS_PATH: /^[a-zA-Z]:\\(?:[^<>:"/\\|?*]+\\)*[^<>:"/\\|?*]*$/,
  
  // File extension validation
  FILE_EXTENSION: /^\.[a-zA-Z0-9]+$/,
  
  // Hexadecimal color validation
  HEX_COLOR: /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/,
  
  // Base64 validation
  BASE64: /^[A-Za-z0-9+/]*={0,2}$/,
  
  // MAC address validation
  MAC_ADDRESS: /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/,
  
  // Windows service name validation
  WINDOWS_SERVICE: /^[a-zA-Z0-9_\-\s]{1,256}$/,
  
  // Registry key validation
  REGISTRY_KEY: /^HKEY_(CLASSES_ROOT|CURRENT_USER|LOCAL_MACHINE|USERS|CURRENT_CONFIG)\\.*$/,
  
  // Process name validation
  PROCESS_NAME: /^[a-zA-Z0-9_\-\.]{1,255}$/,
  
  // SQL injection prevention (basic)
  NO_SQL_INJECTION: /^[^';\\x00-\\x1f\\x7f"]*$/
} as const;

// Field length limits
export const FIELD_LIMITS = {
  // User fields
  USERNAME_MIN: 3,
  USERNAME_MAX: 50,
  PASSWORD_MIN: 8,
  PASSWORD_MAX: 128,
  EMAIL_MAX: 254,
  FIRST_NAME_MAX: 50,
  LAST_NAME_MAX: 50,
  
  // Agent fields
  AGENT_NAME_MIN: 1,
  AGENT_NAME_MAX: 100,
  AGENT_DESCRIPTION_MAX: 500,
  AGENT_VERSION_MAX: 20,
  AGENT_OS_MAX: 50,
  
  // Command fields
  COMMAND_NAME_MIN: 1,
  COMMAND_NAME_MAX: 100,
  COMMAND_MIN: 1,
  COMMAND_MAX: 5000,
  COMMAND_DESCRIPTION_MAX: 500,
  COMMAND_TIMEOUT_MIN: 1,
  COMMAND_TIMEOUT_MAX: 3600,
  
  // System fields
  HOSTNAME_MAX: 253,
  IP_ADDRESS_MAX: 45, // IPv6
  PORT_MIN: 1,
  PORT_MAX: 65535,
  
  // File fields
  FILENAME_MAX: 255,
  FILE_PATH_MAX: 4096,
  FILE_SIZE_MAX: 10 * 1024 * 1024, // 10MB
  
  // Generic fields
  TITLE_MAX: 100,
  DESCRIPTION_MAX: 1000,
  COMMENT_MAX: 2000,
  TAG_MAX: 50,
  URL_MAX: 2000,
  
  // API fields
  API_KEY_LENGTH: 64,
  REQUEST_ID_LENGTH: 36,
  SESSION_ID_LENGTH: 64,
  
  // Settings fields
  SETTING_KEY_MAX: 100,
  SETTING_VALUE_MAX: 1000,
  
  // Search fields
  SEARCH_QUERY_MAX: 500,
  SEARCH_FILTER_MAX: 100
} as const;

// Numeric validation ranges
export const NUMERIC_RANGES = {
  // Pagination
  PAGE_MIN: 1,
  PAGE_MAX: 999999,
  LIMIT_MIN: 1,
  LIMIT_MAX: 100,
  
  // Timeouts
  TIMEOUT_MIN: 1,
  TIMEOUT_MAX: 3600,
  
  // Intervals
  INTERVAL_MIN: 1,
  INTERVAL_MAX: 86400, // 24 hours
  
  // Retry attempts
  RETRY_MIN: 0,
  RETRY_MAX: 10,
  
  // Priority levels
  PRIORITY_MIN: 1,
  PRIORITY_MAX: 5,
  
  // Percentage values
  PERCENTAGE_MIN: 0,
  PERCENTAGE_MAX: 100,
  
  // Memory values (in bytes)
  MEMORY_MIN: 0,
  MEMORY_MAX: Number.MAX_SAFE_INTEGER,
  
  // CPU values (percentage)
  CPU_MIN: 0,
  CPU_MAX: 100,
  
  // Disk space (in bytes)
  DISK_MIN: 0,
  DISK_MAX: Number.MAX_SAFE_INTEGER,
  
  // Network ports
  PORT_MIN: 1,
  PORT_MAX: 65535,
  
  // File sizes
  FILE_SIZE_MIN: 0,
  FILE_SIZE_MAX: 10 * 1024 * 1024 * 1024, // 10GB
  
  // Age in days
  AGE_MIN: 0,
  AGE_MAX: 365 * 10, // 10 years
  
  // Rate limits
  RATE_LIMIT_MIN: 1,
  RATE_LIMIT_MAX: 10000
} as const;

// Validation messages
export const VALIDATION_MESSAGES = {
  // Required fields
  REQUIRED: 'This field is required',
  
  // String validations
  TOO_SHORT: 'This field is too short',
  TOO_LONG: 'This field is too long',
  INVALID_FORMAT: 'Invalid format',
  INVALID_CHARACTERS: 'Contains invalid characters',
  
  // Numeric validations
  NOT_A_NUMBER: 'Must be a number',
  OUT_OF_RANGE: 'Value is out of allowed range',
  NOT_INTEGER: 'Must be an integer',
  NOT_POSITIVE: 'Must be a positive number',
  
  // Email validation
  INVALID_EMAIL: 'Invalid email address',
  
  // Password validation
  PASSWORD_TOO_WEAK: 'Password must contain at least 8 characters, including uppercase, lowercase, and numbers',
  PASSWORDS_DO_NOT_MATCH: 'Passwords do not match',
  
  // URL validation
  INVALID_URL: 'Invalid URL format',
  
  // IP address validation
  INVALID_IP: 'Invalid IP address',
  
  // Port validation
  INVALID_PORT: 'Invalid port number (1-65535)',
  
  // Hostname validation
  INVALID_HOSTNAME: 'Invalid hostname',
  
  // Command validation
  INVALID_COMMAND: 'Invalid command format',
  COMMAND_TOO_LONG: 'Command is too long',
  POTENTIALLY_DANGEROUS: 'Command contains potentially dangerous operations',
  
  // File validation
  INVALID_FILE_TYPE: 'Invalid file type',
  FILE_TOO_LARGE: 'File is too large',
  INVALID_FILE_NAME: 'Invalid file name',
  
  // Agent validation
  AGENT_NAME_INVALID: 'Agent name contains invalid characters',
  AGENT_ALREADY_EXISTS: 'Agent with this name already exists',
  
  // User validation
  USERNAME_TAKEN: 'Username is already taken',
  EMAIL_TAKEN: 'Email is already registered',
  INVALID_USERNAME: 'Username can only contain letters, numbers, and underscores',
  
  // Date validation
  INVALID_DATE: 'Invalid date',
  DATE_IN_FUTURE: 'Date cannot be in the future',
  DATE_IN_PAST: 'Date cannot be in the past',
  
  // Generic validation
  FIELD_REQUIRED: (field: string) => `${field} is required`,
  FIELD_TOO_SHORT: (field: string, min: number) => `${field} must be at least ${min} characters`,
  FIELD_TOO_LONG: (field: string, max: number) => `${field} must be no more than ${max} characters`,
  VALUE_OUT_OF_RANGE: (min: number, max: number) => `Value must be between ${min} and ${max}`,
  INVALID_CHOICE: (choices: string[]) => `Must be one of: ${choices.join(', ')}`
} as const;

// File type validations
export const FILE_TYPES = {
  // Allowed file extensions
  EXECUTABLES: ['.exe', '.msi', '.bat', '.cmd', '.ps1'],
  ARCHIVES: ['.zip', '.rar', '.7z', '.tar', '.gz'],
  DOCUMENTS: ['.txt', '.log', '.csv', '.json', '.xml', '.yaml', '.yml'],
  IMAGES: ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg'],
  
  // MIME types
  MIME_TYPES: {
    'application/octet-stream': ['.exe', '.msi'],
    'application/zip': ['.zip'],
    'text/plain': ['.txt', '.log'],
    'application/json': ['.json'],
    'image/png': ['.png'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'text/csv': ['.csv']
  }
} as const;

// Command risk levels
export const COMMAND_RISK_LEVELS = {
  LOW: 1,
  MEDIUM: 2,
  HIGH: 3,
  CRITICAL: 4
} as const;

// Validation states
export const VALIDATION_STATES = {
  PRISTINE: 'pristine',
  VALIDATING: 'validating',
  VALID: 'valid',
  INVALID: 'invalid',
  ERROR: 'error'
} as const;

// Input sanitization
export const SANITIZATION = {
  // Characters to escape in HTML
  HTML_ESCAPE_MAP: {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;'
  },
  
  // Characters to remove from file names
  FILENAME_INVALID_CHARS: /[<>:"/\\|?*\x00-\x1f]/g,
  
  // SQL injection patterns to block
  SQL_INJECTION_PATTERNS: [
    /(\%27)|(\')|(\-\-)|(\%23)|(#)/i,
    /((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))/i,
    /\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))/i,
    /((\%27)|(\'))union/i
  ]
} as const;

// Rate limiting validation
export const RATE_LIMITING = {
  // Requests per time window
  MAX_REQUESTS_PER_MINUTE: 60,
  MAX_REQUESTS_PER_HOUR: 1000,
  MAX_REQUESTS_PER_DAY: 10000,
  
  // Login attempt limits
  MAX_LOGIN_ATTEMPTS: 5,
  LOGIN_LOCKOUT_DURATION: 15 * 60, // 15 minutes in seconds
  
  // Command execution limits
  MAX_CONCURRENT_COMMANDS: 10,
  MAX_COMMANDS_PER_MINUTE: 30,
  
  // File upload limits
  MAX_UPLOADS_PER_HOUR: 10,
  MAX_UPLOAD_SIZE: 10 * 1024 * 1024 // 10MB
} as const;