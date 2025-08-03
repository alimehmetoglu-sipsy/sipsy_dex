// Application-wide constants

export const APP_NAME = 'DexAgent';
export const APP_DESCRIPTION = 'Modern Windows Endpoint Management Platform';
export const APP_VERSION = '3.3.0';

// Default configuration values
export const DEFAULT_CONFIG = {
  // Pagination
  DEFAULT_PAGE_SIZE: 25,
  MAX_PAGE_SIZE: 100,
  
  // Timeouts (in seconds)
  DEFAULT_COMMAND_TIMEOUT: 30,
  MAX_COMMAND_TIMEOUT: 3600,
  DEFAULT_CONNECTION_TIMEOUT: 10,
  
  // Intervals (in seconds)
  HEARTBEAT_INTERVAL: 30,
  METRICS_COLLECTION_INTERVAL: 60,
  HEALTH_CHECK_INTERVAL: 30,
  
  // Retry settings
  DEFAULT_RETRY_ATTEMPTS: 3,
  RETRY_DELAY_BASE: 1000,
  RETRY_DELAY_MAX: 10000,
  
  // File upload
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_FILE_TYPES: ['.exe', '.msi', '.zip', '.ps1', '.bat', '.cmd'],
  
  // Rate limiting
  RATE_LIMIT_WINDOW: 60, // seconds
  RATE_LIMIT_MAX_REQUESTS: 100,
  
  // Session
  SESSION_TIMEOUT: 24 * 60 * 60, // 24 hours in seconds
  
  // Database
  DB_CONNECTION_POOL_SIZE: 10,
  DB_CONNECTION_TIMEOUT: 5000,
  
  // WebSocket
  WS_PING_INTERVAL: 30000, // 30 seconds
  WS_RECONNECT_DELAY: 5000, // 5 seconds
  WS_MAX_RECONNECT_ATTEMPTS: 5,
  
  // Monitoring
  METRICS_RETENTION_DAYS: 30,
  LOG_RETENTION_DAYS: 7,
  ALERT_COOLDOWN_MINUTES: 5
} as const;

// Environment types
export const ENVIRONMENTS = {
  DEVELOPMENT: 'development',
  STAGING: 'staging',
  PRODUCTION: 'production',
  TEST: 'test'
} as const;

// Feature flags
export const FEATURE_FLAGS = {
  AI_COMMANDS: 'ai_commands',
  BULK_OPERATIONS: 'bulk_operations',
  ADVANCED_MONITORING: 'advanced_monitoring',
  AGENT_GROUPS: 'agent_groups',
  SCHEDULED_TASKS: 'scheduled_tasks',
  API_WEBHOOKS: 'api_webhooks',
  AUDIT_LOGGING: 'audit_logging',
  TWO_FACTOR_AUTH: 'two_factor_auth',
  DARK_MODE: 'dark_mode',
  REAL_TIME_DASHBOARD: 'real_time_dashboard'
} as const;

// Application limits
export const LIMITS = {
  MAX_AGENTS: 1000,
  MAX_CONCURRENT_COMMANDS: 50,
  MAX_COMMAND_HISTORY: 10000,
  MAX_SAVED_COMMANDS: 500,
  MAX_USERS: 100,
  MAX_GROUPS: 50,
  MAX_ALERT_RULES: 100,
  MAX_WEBHOOK_ENDPOINTS: 20,
  
  // String lengths
  MAX_AGENT_NAME_LENGTH: 100,
  MAX_COMMAND_NAME_LENGTH: 100,
  MAX_COMMAND_LENGTH: 5000,
  MAX_DESCRIPTION_LENGTH: 500,
  MAX_USERNAME_LENGTH: 50,
  MAX_EMAIL_LENGTH: 254,
  
  // Numeric limits
  MIN_PORT: 1,
  MAX_PORT: 65535,
  MIN_TIMEOUT: 1,
  MAX_TIMEOUT: 3600,
  MIN_PAGE_SIZE: 1,
  MAX_PAGE_SIZE: 100
} as const;

// Cache keys
export const CACHE_KEYS = {
  AGENT_STATUS: 'agent:status',
  SYSTEM_HEALTH: 'system:health',
  USER_PERMISSIONS: 'user:permissions',
  COMMAND_TEMPLATES: 'command:templates',
  SETTINGS: 'system:settings',
  METRICS: 'system:metrics'
} as const;

// Cache TTL (in seconds)
export const CACHE_TTL = {
  AGENT_STATUS: 30,
  SYSTEM_HEALTH: 60,
  USER_PERMISSIONS: 300, // 5 minutes
  COMMAND_TEMPLATES: 600, // 10 minutes
  SETTINGS: 3600, // 1 hour
  METRICS: 60
} as const;