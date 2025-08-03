// Agent-related types for DexAgent system

import { UUID, Timestamp, Status, SystemMetrics } from './common';

export enum AgentStatus {
  ONLINE = 'online',
  OFFLINE = 'offline',
  CONNECTING = 'connecting',
  DISCONNECTED = 'disconnected',
  ERROR = 'error',
  UNKNOWN = 'unknown'
}

export enum AgentType {
  WINDOWS = 'windows',
  LINUX = 'linux',
  MACOS = 'macos'
}

export interface Agent {
  id: UUID;
  name: string;
  hostname: string;
  ipAddress: string;
  port: number;
  status: AgentStatus;
  type: AgentType;
  version: string;
  groupId?: UUID;
  lastHeartbeat: Timestamp;
  connectionTime?: Timestamp;
  disconnectionTime?: Timestamp;
  metadata?: Record<string, unknown>;
  tags?: string[];
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface AgentGroup {
  id: UUID;
  name: string;
  description?: string;
  color?: string;
  agentCount: number;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface AgentMetrics extends SystemMetrics {
  agentId: UUID;
  processes?: ProcessInfo[];
  services?: ServiceInfo[];
  uptime: number;
}

export interface ProcessInfo {
  pid: number;
  name: string;
  cpuPercent: number;
  memoryPercent: number;
  status: string;
  startTime: Timestamp;
}

export interface ServiceInfo {
  name: string;
  displayName: string;
  status: 'running' | 'stopped' | 'paused' | 'unknown';
  startType: 'automatic' | 'manual' | 'disabled';
  description?: string;
}

export interface AgentCapabilities {
  supportedCommands: string[];
  maxConcurrentCommands: number;
  timeout: {
    default: number;
    maximum: number;
  };
  features: {
    fileTransfer: boolean;
    systemMonitoring: boolean;
    processManagement: boolean;
    serviceManagement: boolean;
    registryAccess: boolean;
    eventLogAccess: boolean;
  };
}

export interface AgentConfiguration {
  agentId: UUID;
  serverUrl: string;
  heartbeatInterval: number;
  reconnectAttempts: number;
  reconnectDelay: number;
  commandTimeout: number;
  logLevel: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';
  enableMetrics: boolean;
  metricsInterval: number;
  settings: Record<string, unknown>;
}

export interface AgentInstallation {
  id: UUID;
  agentId?: UUID;
  hostname: string;
  ipAddress: string;
  installerVersion: string;
  installationStatus: 'pending' | 'installing' | 'completed' | 'failed';
  installationMethod: 'manual' | 'remote' | 'script';
  downloadUrl?: string;
  installationLog?: string[];
  error?: string;
  createdAt: Timestamp;
  completedAt?: Timestamp;
}

// Request/Response types
export interface AgentRegistrationRequest {
  name: string;
  hostname: string;
  ipAddress: string;
  port: number;
  type: AgentType;
  version: string;
  capabilities: AgentCapabilities;
  metadata?: Record<string, unknown>;
  groupId?: UUID;
}

export interface AgentUpdateRequest {
  name?: string;
  groupId?: UUID;
  metadata?: Record<string, unknown>;
  tags?: string[];
}

export interface AgentListRequest {
  status?: AgentStatus;
  type?: AgentType;
  groupId?: UUID;
  search?: string;
  tags?: string[];
  page?: number;
  limit?: number;
}

export interface AgentHeartbeat {
  agentId: UUID;
  timestamp: Timestamp;
  status: AgentStatus;
  metrics?: SystemMetrics;
  error?: string;
}