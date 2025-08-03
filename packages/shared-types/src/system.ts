// System-related types for configuration and monitoring

import { UUID, Timestamp, Environment, HealthCheck, SystemMetrics } from './common';

export interface SystemInfo {
  name: string;
  version: string;
  environment: Environment;
  buildNumber: string;
  buildDate: Timestamp;
  uptime: number;
  startTime: Timestamp;
  nodeVersion: string;
  platform: string;
  architecture: string;
  totalMemory: number;
  freeMemory: number;
  cpuCount: number;
  loadAverage: number[];
}

export interface SystemSettings {
  id: UUID;
  name: string;
  description?: string;
  category: string;
  value: unknown;
  type: 'string' | 'number' | 'boolean' | 'json' | 'encrypted';
  isPublic: boolean;
  isRequired: boolean;
  defaultValue?: unknown;
  validation?: {
    pattern?: string;
    min?: number;
    max?: number;
    enum?: unknown[];
  };
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface SystemConfiguration {
  // Database settings
  database: {
    host: string;
    port: number;
    name: string;
    poolSize: number;
    connectionTimeout: number;
    queryTimeout: number;
  };
  
  // Redis settings
  redis: {
    host: string;
    port: number;
    database: number;
    password?: string;
    keyPrefix: string;
  };
  
  // Authentication settings
  auth: {
    jwtSecret: string;
    tokenExpiration: number;
    refreshTokenExpiration: number;
    bcryptRounds: number;
    maxLoginAttempts: number;
    lockoutDuration: number;
  };
  
  // Agent settings
  agent: {
    heartbeatInterval: number;
    connectionTimeout: number;
    maxConcurrentCommands: number;
    defaultCommandTimeout: number;
    maxCommandTimeout: number;
    keepAliveInterval: number;
  };
  
  // WebSocket settings
  websocket: {
    port: number;
    maxConnections: number;
    pingInterval: number;
    pongTimeout: number;
    compressionEnabled: boolean;
  };
  
  // File upload settings
  fileUpload: {
    maxFileSize: number;
    allowedTypes: string[];
    uploadPath: string;
    cleanupInterval: number;
    retentionDays: number;
  };
  
  // Email settings
  email: {
    enabled: boolean;
    smtp: {
      host: string;
      port: number;
      secure: boolean;
      username: string;
      password: string;
    };
    from: {
      name: string;
      address: string;
    };
    templates: {
      welcome: string;
      passwordReset: string;
      systemAlert: string;
    };
  };
  
  // Logging settings
  logging: {
    level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';
    format: 'json' | 'text';
    maxFileSize: number;
    maxFiles: number;
    enableConsole: boolean;
    enableFile: boolean;
    enableDatabase: boolean;
  };
  
  // Security settings
  security: {
    enableRateLimit: boolean;
    rateLimitWindow: number;
    rateLimitMax: number;
    enableCors: boolean;
    corsOrigins: string[];
    enableCSP: boolean;
    cspDirectives: Record<string, string[]>;
  };
  
  // Monitoring settings
  monitoring: {
    enableMetrics: boolean;
    metricsInterval: number;
    enableHealthCheck: boolean;
    healthCheckInterval: number;
    enableAlerting: boolean;
    alertThresholds: {
      cpuUsage: number;
      memoryUsage: number;
      diskUsage: number;
      responseTime: number;
    };
  };
  
  // AI settings
  ai: {
    enabled: boolean;
    provider: 'openai' | 'anthropic' | 'azure' | 'local';
    apiKey: string;
    model: string;
    maxTokens: number;
    temperature: number;
    timeout: number;
    safetyMode: boolean;
  };
  
  // Backup settings
  backup: {
    enabled: boolean;
    schedule: string;
    retentionDays: number;
    storageType: 'local' | 's3' | 'azure' | 'gcp';
    storageConfig: Record<string, unknown>;
    encryptionEnabled: boolean;
    compressionEnabled: boolean;
  };
}

export interface Alert {
  id: UUID;
  type: 'system' | 'agent' | 'command' | 'security' | 'performance';
  severity: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  message: string;
  source: string;
  agentId?: UUID;
  userId?: UUID;
  metadata?: Record<string, unknown>;
  acknowledged: boolean;
  acknowledgedBy?: UUID;
  acknowledgedAt?: Timestamp;
  resolved: boolean;
  resolvedBy?: UUID;
  resolvedAt?: Timestamp;
  resolutionNote?: string;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface NotificationChannel {
  id: UUID;
  name: string;
  type: 'email' | 'slack' | 'teams' | 'webhook' | 'sms';
  configuration: Record<string, unknown>;
  enabled: boolean;
  filters: {
    severity?: Alert['severity'][];
    types?: Alert['type'][];
    sources?: string[];
  };
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface SystemMetricsHistory {
  id: UUID;
  timestamp: Timestamp;
  metrics: SystemMetrics;
  agentMetrics: Record<UUID, SystemMetrics>;
  performanceMetrics: {
    apiResponseTime: number;
    databaseResponseTime: number;
    activeConnections: number;
    commandsExecuted: number;
    errorsCount: number;
  };
}

export interface License {
  id: UUID;
  type: 'trial' | 'standard' | 'premium' | 'enterprise';
  maxAgents: number;
  maxUsers: number;
  features: string[];
  issuedTo: string;
  issuedBy: string;
  issueDate: Timestamp;
  expirationDate: Timestamp;
  status: 'active' | 'expired' | 'suspended' | 'revoked';
  licenseKey: string;
  activationDate?: Timestamp;
  lastValidation: Timestamp;
}

export interface MaintenanceWindow {
  id: UUID;
  title: string;
  description: string;
  startTime: Timestamp;
  endTime: Timestamp;
  type: 'scheduled' | 'emergency';
  impact: 'none' | 'minimal' | 'partial' | 'full';
  affectedServices: string[];
  notificationSent: boolean;
  status: 'planned' | 'active' | 'completed' | 'cancelled';
  createdBy: UUID;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

// Request/Response types
export interface SystemSettingsUpdateRequest {
  settings: Array<{
    name: string;
    value: unknown;
  }>;
}

export interface AlertCreateRequest {
  type: Alert['type'];
  severity: Alert['severity'];
  title: string;
  message: string;
  source: string;
  agentId?: UUID;
  metadata?: Record<string, unknown>;
}

export interface AlertUpdateRequest {
  acknowledged?: boolean;
  resolved?: boolean;
  resolutionNote?: string;
}

export interface NotificationChannelCreateRequest {
  name: string;
  type: NotificationChannel['type'];
  configuration: Record<string, unknown>;
  enabled?: boolean;
  filters?: NotificationChannel['filters'];
}

export interface NotificationChannelUpdateRequest {
  name?: string;
  configuration?: Record<string, unknown>;
  enabled?: boolean;
  filters?: NotificationChannel['filters'];
}

export interface MaintenanceWindowCreateRequest {
  title: string;
  description: string;
  startTime: Timestamp;
  endTime: Timestamp;
  type: MaintenanceWindow['type'];
  impact: MaintenanceWindow['impact'];
  affectedServices: string[];
}

export interface SystemHealthReport {
  overall: HealthCheck;
  components: Record<string, HealthCheck>;
  metrics: SystemMetrics;
  alerts: Alert[];
  uptime: {
    current: number;
    last24h: number;
    last7d: number;
    last30d: number;
  };
  performance: {
    averageResponseTime: number;
    successRate: number;
    errorRate: number;
    throughput: number;
  };
}

export interface BackupInfo {
  id: UUID;
  filename: string;
  size: number;
  type: 'full' | 'incremental' | 'differential';
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  startTime: Timestamp;
  endTime?: Timestamp;
  duration?: number;
  error?: string;
  checksum: string;
  location: string;
  createdAt: Timestamp;
}

export interface RestoreRequest {
  backupId: UUID;
  type: 'full' | 'partial';
  tables?: string[];
  confirmDataLoss: boolean;
}

export interface RestoreInfo {
  id: UUID;
  backupId: UUID;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  startTime: Timestamp;
  endTime?: Timestamp;
  duration?: number;
  error?: string;
  createdAt: Timestamp;
}