// Configuration-related constants

// Environment configuration
export const ENVIRONMENT_CONFIG = {
  DEVELOPMENT: {
    name: 'development',
    debug: true,
    logLevel: 'debug',
    strictMode: false,
    mockServices: true,
    hotReload: true
  },
  STAGING: {
    name: 'staging',
    debug: true,
    logLevel: 'info',
    strictMode: true,
    mockServices: false,
    hotReload: false
  },
  PRODUCTION: {
    name: 'production',
    debug: false,
    logLevel: 'error',
    strictMode: true,
    mockServices: false,
    hotReload: false
  },
  TEST: {
    name: 'test',
    debug: true,
    logLevel: 'debug',
    strictMode: true,
    mockServices: true,
    hotReload: false
  }
} as const;

// Default application configuration
export const DEFAULT_APP_CONFIG = {
  // Server configuration
  server: {
    host: '0.0.0.0',
    port: 8000,
    workers: 1,
    keepAlive: 65,
    maxRequestSize: 10 * 1024 * 1024, // 10MB
    requestTimeout: 30000,
    gracefulTimeout: 30000
  },
  
  // Database configuration
  database: {
    host: 'localhost',
    port: 5432,
    name: 'dexagent',
    username: 'postgres',
    password: 'postgres123',
    poolSize: 10,
    poolTimeout: 5000,
    connectionTimeout: 5000,
    queryTimeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000,
    ssl: false,
    logging: false
  },
  
  // Authentication configuration
  auth: {
    jwtSecret: 'your-secret-key-here',
    jwtAlgorithm: 'HS256',
    accessTokenExpiry: 24 * 60 * 60, // 24 hours in seconds
    refreshTokenExpiry: 7 * 24 * 60 * 60, // 7 days in seconds
    passwordHashRounds: 12,
    sessionTimeout: 24 * 60 * 60, // 24 hours
    maxLoginAttempts: 5,
    lockoutDuration: 15 * 60, // 15 minutes
    twoFactorEnabled: false,
    passwordExpiryDays: 90
  },
  
  // WebSocket configuration
  websocket: {
    port: 8001,
    pingInterval: 30000,
    pongTimeout: 5000,
    maxConnections: 1000,
    maxMessageSize: 1024 * 1024, // 1MB
    compressionEnabled: true,
    heartbeatInterval: 30000,
    reconnectDelay: 5000,
    maxReconnectAttempts: 5
  },
  
  // Redis configuration
  redis: {
    host: 'localhost',
    port: 6379,
    password: null,
    database: 0,
    maxRetries: 3,
    retryDelay: 1000,
    connectionTimeout: 5000,
    commandTimeout: 5000,
    keyPrefix: 'dexagent:',
    enableReadyCheck: true
  },
  
  // File upload configuration
  upload: {
    maxFileSize: 10 * 1024 * 1024, // 10MB
    allowedExtensions: ['.exe', '.msi', '.zip', '.ps1', '.bat', '.cmd', '.txt', '.log'],
    uploadPath: './uploads',
    tempPath: './temp',
    chunkSize: 1024 * 1024, // 1MB
    maxConcurrentUploads: 3,
    cleanupInterval: 60 * 60 * 1000, // 1 hour
    tempFileExpiry: 24 * 60 * 60 * 1000 // 24 hours
  },
  
  // Logging configuration
  logging: {
    level: 'info',
    format: 'json',
    console: true,
    file: true,
    filePath: './logs/app.log',
    maxFileSize: 10 * 1024 * 1024, // 10MB
    maxFiles: 5,
    datePattern: 'YYYY-MM-DD',
    errorLogPath: './logs/error.log',
    auditLogPath: './logs/audit.log',
    retention: 30 // days
  },
  
  // Rate limiting configuration
  rateLimit: {
    windowMs: 60 * 1000, // 1 minute
    maxRequests: 100,
    skipSuccessfulRequests: false,
    skipFailedRequests: false,
    keyGenerator: 'ip', // 'ip', 'user', 'custom'
    message: 'Too many requests, please try again later',
    headers: true,
    standardHeaders: true,
    legacyHeaders: false
  },
  
  // Security configuration
  security: {
    corsEnabled: true,
    corsOrigins: ['http://localhost:3000'],
    corsCredentials: true,
    helmetEnabled: true,
    csrfEnabled: true,
    rateLimitEnabled: true,
    encryptionKey: 'your-encryption-key-here',
    encryptionAlgorithm: 'aes-256-gcm',
    hashingSalt: 'your-salt-here',
    secureHeaders: true,
    contentTypeValidation: true
  },
  
  // Monitoring configuration
  monitoring: {
    enabled: true,
    metricsInterval: 60000, // 1 minute
    healthCheckInterval: 30000, // 30 seconds
    performanceTracking: true,
    errorTracking: true,
    uptime: true,
    memoryUsage: true,
    cpuUsage: true,
    diskUsage: true,
    networkUsage: true,
    databaseMetrics: true,
    customMetrics: true
  },
  
  // Email configuration
  email: {
    enabled: false,
    provider: 'smtp',
    smtp: {
      host: 'smtp.gmail.com',
      port: 587,
      secure: false,
      auth: {
        user: 'your-email@gmail.com',
        pass: 'your-password'
      }
    },
    from: 'noreply@dexagent.com',
    templates: {
      passwordReset: './templates/password-reset.html',
      welcome: './templates/welcome.html',
      alert: './templates/alert.html'
    }
  },
  
  // Notification configuration
  notifications: {
    enabled: true,
    channels: ['email', 'webhook', 'sms'],
    defaultChannel: 'email',
    retryAttempts: 3,
    retryDelay: 5000,
    batchSize: 10,
    batchInterval: 30000,
    templates: './templates/notifications'
  },
  
  // AI configuration
  ai: {
    enabled: false,
    provider: 'openai',
    openai: {
      apiKey: null,
      model: 'gpt-3.5-turbo',
      maxTokens: 2000,
      temperature: 0.7,
      timeout: 30000
    },
    features: {
      commandGeneration: true,
      anomalyDetection: false,
      predictiveAnalysis: false,
      naturalLanguageQuery: false
    }
  },
  
  // Backup configuration
  backup: {
    enabled: false,
    schedule: '0 2 * * *', // Daily at 2 AM
    retention: 7, // days
    compression: true,
    encryption: true,
    location: './backups',
    includeFiles: false,
    excludePatterns: ['*.log', '*.tmp', 'temp/*']
  },
  
  // Cache configuration
  cache: {
    enabled: true,
    provider: 'redis',
    ttl: 3600, // 1 hour
    maxKeys: 10000,
    compression: true,
    serialization: 'json',
    keyPrefix: 'cache:',
    invalidationStrategy: 'ttl'
  },
  
  // Agent configuration
  agent: {
    defaultTimeout: 30,
    maxConcurrentCommands: 5,
    heartbeatInterval: 30,
    heartbeatTimeout: 90,
    reconnectInterval: 5,
    maxReconnectAttempts: 10,
    commandQueueSize: 100,
    metricCollectionInterval: 60,
    autoUpdate: false,
    encryptCommunication: true
  }
} as const;

// Feature toggles/flags
export const FEATURE_TOGGLES = {
  // Core features
  USER_REGISTRATION: true,
  TWO_FACTOR_AUTHENTICATION: false,
  SOCIAL_LOGIN: false,
  GUEST_ACCESS: false,
  
  // Agent features
  AGENT_GROUPS: true,
  AGENT_AUTO_DISCOVERY: false,
  AGENT_REMOTE_INSTALLATION: true,
  AGENT_BULK_OPERATIONS: true,
  
  // Command features
  COMMAND_SCHEDULING: true,
  COMMAND_TEMPLATES: true,
  COMMAND_HISTORY: true,
  COMMAND_APPROVAL_WORKFLOW: false,
  
  // AI features
  AI_COMMAND_GENERATION: false,
  AI_ANOMALY_DETECTION: false,
  AI_PREDICTIVE_ANALYSIS: false,
  AI_CHATBOT: false,
  
  // Monitoring features
  REAL_TIME_MONITORING: true,
  ADVANCED_ANALYTICS: false,
  CUSTOM_DASHBOARDS: true,
  ALERTING: true,
  
  // Integration features
  WEBHOOK_SUPPORT: true,
  API_RATE_LIMITING: true,
  THIRD_PARTY_INTEGRATIONS: false,
  EXPORT_FUNCTIONALITY: true,
  
  // UI features
  DARK_MODE: true,
  MOBILE_APP: false,
  DESKTOP_APP: false,
  BROWSER_NOTIFICATIONS: true,
  
  // Security features
  AUDIT_LOGGING: true,
  ENCRYPTION_AT_REST: false,
  VPN_INTEGRATION: false,
  SSO_INTEGRATION: false,
  
  // Performance features
  CACHING: true,
  CDN_SUPPORT: false,
  LOAD_BALANCING: false,
  AUTO_SCALING: false
} as const;

// Performance configuration
export const PERFORMANCE_CONFIG = {
  // Database query optimization
  database: {
    connectionPoolSize: 20,
    queryTimeout: 30000,
    slowQueryThreshold: 1000,
    indexOptimization: true,
    queryCache: true,
    preparedStatements: true
  },
  
  // API response optimization
  api: {
    responseCompression: true,
    cacheHeaders: true,
    etagSupport: true,
    pagination: true,
    fieldSelection: true,
    rateLimiting: true
  },
  
  // Frontend optimization
  frontend: {
    bundleOptimization: true,
    codesplitting: true,
    lazyLoading: true,
    imageLazyLoading: true,
    serviceWorker: true,
    clientSideCache: true
  },
  
  // Memory management
  memory: {
    maxHeapSize: '1g',
    gcOptimization: true,
    memoryLeakDetection: true,
    objectPooling: false
  }
} as const;

// Security configuration presets
export const SECURITY_PRESETS = {
  MINIMAL: {
    corsEnabled: true,
    helmetEnabled: true,
    rateLimitEnabled: false,
    csrfEnabled: false,
    encryptionEnabled: false
  },
  
  STANDARD: {
    corsEnabled: true,
    helmetEnabled: true,
    rateLimitEnabled: true,
    csrfEnabled: true,
    encryptionEnabled: true
  },
  
  STRICT: {
    corsEnabled: true,
    helmetEnabled: true,
    rateLimitEnabled: true,
    csrfEnabled: true,
    encryptionEnabled: true,
    twoFactorRequired: true,
    auditLogging: true,
    sessionTimeout: 30 * 60 // 30 minutes
  },
  
  PARANOID: {
    corsEnabled: true,
    helmetEnabled: true,
    rateLimitEnabled: true,
    csrfEnabled: true,
    encryptionEnabled: true,
    twoFactorRequired: true,
    auditLogging: true,
    sessionTimeout: 15 * 60, // 15 minutes
    passwordComplexity: 'high',
    ipWhitelisting: true,
    certificatePinning: true
  }
} as const;

// Deployment configuration
export const DEPLOYMENT_CONFIG = {
  // Docker configuration
  docker: {
    baseImage: 'python:3.11-slim',
    workdir: '/app',
    exposedPorts: [8000, 8001],
    healthCheck: {
      test: ['CMD', 'curl', '-f', 'http://localhost:8000/health'],
      interval: '30s',
      timeout: '10s',
      retries: 3
    },
    resources: {
      cpuLimit: '1',
      memoryLimit: '1g',
      cpuReservation: '0.5',
      memoryReservation: '512m'
    }
  },
  
  // Kubernetes configuration
  kubernetes: {
    namespace: 'dexagent',
    replicas: 3,
    strategy: 'RollingUpdate',
    maxUnavailable: 1,
    maxSurge: 1,
    resources: {
      requests: {
        cpu: '100m',
        memory: '256Mi'
      },
      limits: {
        cpu: '500m',
        memory: '512Mi'
      }
    },
    probes: {
      liveness: {
        httpGet: {
          path: '/health',
          port: 8000
        },
        initialDelaySeconds: 30,
        periodSeconds: 10
      },
      readiness: {
        httpGet: {
          path: '/ready',
          port: 8000
        },
        initialDelaySeconds: 5,
        periodSeconds: 5
      }
    }
  }
} as const;