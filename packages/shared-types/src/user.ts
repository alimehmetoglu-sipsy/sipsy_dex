// User and authentication types

import { UUID, Timestamp, Status } from './common';

export enum UserRole {
  ADMIN = 'admin',
  OPERATOR = 'operator',
  VIEWER = 'viewer',
  AGENT = 'agent'
}

export enum Permission {
  // Agent permissions
  AGENT_VIEW = 'agent:view',
  AGENT_CREATE = 'agent:create',
  AGENT_UPDATE = 'agent:update',
  AGENT_DELETE = 'agent:delete',
  AGENT_EXECUTE = 'agent:execute',
  
  // Command permissions
  COMMAND_VIEW = 'command:view',
  COMMAND_CREATE = 'command:create',
  COMMAND_UPDATE = 'command:update',
  COMMAND_DELETE = 'command:delete',
  COMMAND_EXECUTE = 'command:execute',
  COMMAND_SCHEDULE = 'command:schedule',
  
  // User permissions
  USER_VIEW = 'user:view',
  USER_CREATE = 'user:create',
  USER_UPDATE = 'user:update',
  USER_DELETE = 'user:delete',
  
  // System permissions
  SYSTEM_VIEW = 'system:view',
  SYSTEM_CONFIGURE = 'system:configure',
  SYSTEM_ADMIN = 'system:admin',
  
  // Audit permissions
  AUDIT_VIEW = 'audit:view',
  AUDIT_EXPORT = 'audit:export'
}

export interface User {
  id: UUID;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  role: UserRole;
  permissions: Permission[];
  status: Status;
  isActive: boolean;
  lastLogin?: Timestamp;
  lastLoginIp?: string;
  emailVerified: boolean;
  twoFactorEnabled: boolean;
  preferences: UserPreferences;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  timezone: string;
  dateFormat: string;
  timeFormat: '12h' | '24h';
  notifications: {
    email: boolean;
    browser: boolean;
    agentOffline: boolean;
    commandFailed: boolean;
    systemAlerts: boolean;
  };
  dashboard: {
    defaultView: 'agents' | 'commands' | 'metrics';
    refreshInterval: number;
    showMetrics: boolean;
  };
}

export interface UserSession {
  id: UUID;
  userId: UUID;
  token: string;
  refreshToken: string;
  expiresAt: Timestamp;
  ipAddress: string;
  userAgent: string;
  isActive: boolean;
  lastActivity: Timestamp;
  createdAt: Timestamp;
}

export interface AuditLog {
  id: UUID;
  userId?: UUID;
  agentId?: UUID;
  action: string;
  resource: string;
  resourceId?: UUID;
  details: Record<string, unknown>;
  ipAddress: string;
  userAgent: string;
  success: boolean;
  error?: string;
  duration?: number;
  createdAt: Timestamp;
}

// Authentication types
export interface LoginRequest {
  username: string;
  password: string;
  rememberMe?: boolean;
  twoFactorCode?: string;
}

export interface LoginResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  tokenType: string;
}

export interface RefreshTokenRequest {
  refreshToken: string;
}

export interface RefreshTokenResponse {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
}

export interface ResetPasswordRequest {
  email: string;
}

export interface ResetPasswordConfirmRequest {
  token: string;
  newPassword: string;
}

export interface TwoFactorSetupRequest {
  password: string;
}

export interface TwoFactorSetupResponse {
  qrCode: string;
  backupCodes: string[];
  secret: string;
}

export interface TwoFactorVerifyRequest {
  code: string;
}

// User management types
export interface UserCreateRequest {
  username: string;
  email: string;
  password: string;
  firstName?: string;
  lastName?: string;
  role: UserRole;
  sendWelcomeEmail?: boolean;
}

export interface UserUpdateRequest {
  email?: string;
  firstName?: string;
  lastName?: string;
  role?: UserRole;
  status?: Status;
  permissions?: Permission[];
}

export interface UserListRequest {
  role?: UserRole;
  status?: Status;
  search?: string;
  page?: number;
  limit?: number;
}

export interface UserPreferencesUpdateRequest {
  theme?: UserPreferences['theme'];
  language?: string;
  timezone?: string;
  dateFormat?: string;
  timeFormat?: UserPreferences['timeFormat'];
  notifications?: Partial<UserPreferences['notifications']>;
  dashboard?: Partial<UserPreferences['dashboard']>;
}

// Role and permission types
export interface Role {
  id: UUID;
  name: string;
  description: string;
  permissions: Permission[];
  isSystem: boolean;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface RoleCreateRequest {
  name: string;
  description: string;
  permissions: Permission[];
}

export interface RoleUpdateRequest {
  name?: string;
  description?: string;
  permissions?: Permission[];
}

// Activity tracking
export interface UserActivity {
  id: UUID;
  userId: UUID;
  action: string;
  resource?: string;
  resourceId?: UUID;
  metadata?: Record<string, unknown>;
  ipAddress: string;
  userAgent: string;
  createdAt: Timestamp;
}

// JWT token payload
export interface JWTPayload {
  sub: UUID; // User ID
  username: string;
  role: UserRole;
  permissions: Permission[];
  iat: number;
  exp: number;
  jti: UUID; // JWT ID
}

// API key for programmatic access
export interface APIKey {
  id: UUID;
  name: string;
  keyHash: string;
  userId: UUID;
  permissions: Permission[];
  expiresAt?: Timestamp;
  lastUsed?: Timestamp;
  isActive: boolean;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface APIKeyCreateRequest {
  name: string;
  permissions: Permission[];
  expiresAt?: Timestamp;
}

export interface APIKeyCreateResponse {
  apiKey: APIKey;
  key: string; // Only returned once during creation
}