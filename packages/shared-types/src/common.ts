// Common types used across the DexAgent application

export type UUID = string;
export type Timestamp = string; // ISO 8601 format
export type JSONValue = string | number | boolean | null | JSONObject | JSONArray;
export interface JSONObject {
  [key: string]: JSONValue;
}
export type JSONArray = JSONValue[];

// Pagination
export interface PaginationParams {
  page?: number;
  limit?: number;
  offset?: number;
}

export interface PaginationMeta {
  total: number;
  page: number;
  limit: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: PaginationMeta;
}

// Status enums
export enum Status {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  PENDING = 'pending',
  SUSPENDED = 'suspended',
  DELETED = 'deleted'
}

export enum Priority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum Environment {
  DEVELOPMENT = 'development',
  STAGING = 'staging',
  PRODUCTION = 'production',
  TEST = 'test'
}

// Error types
export interface ErrorDetails {
  code: string;
  message: string;
  field?: string;
  value?: unknown;
}

export interface APIError {
  error: {
    code: string;
    message: string;
    details?: ErrorDetails[];
  };
  timestamp: Timestamp;
  requestId?: string;
}

// Success response wrapper
export interface APIResponse<T = unknown> {
  data?: T;
  message?: string;
  success: boolean;
  timestamp: Timestamp;
  requestId?: string;
}

// Health check
export interface HealthCheck {
  status: 'healthy' | 'unhealthy' | 'degraded';
  timestamp: Timestamp;
  version: string;
  uptime: number;
  services: Record<string, 'up' | 'down' | 'degraded'>;
}

// Metrics
export interface SystemMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network?: {
    bytesIn: number;
    bytesOut: number;
  };
  processes?: number;
  timestamp: Timestamp;
}

// Configuration
export interface AppConfig {
  name: string;
  version: string;
  environment: Environment;
  debug: boolean;
  apiUrl: string;
  wsUrl: string;
  features: Record<string, boolean>;
}