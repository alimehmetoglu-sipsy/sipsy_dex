// Command-related types for PowerShell execution

import { UUID, Timestamp, Priority } from './common';

export enum CommandStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  TIMEOUT = 'timeout',
  CANCELLED = 'cancelled'
}

export enum CommandType {
  POWERSHELL = 'powershell',
  CMD = 'cmd',
  BASH = 'bash',
  PYTHON = 'python',
  CUSTOM = 'custom'
}

export enum CommandCategory {
  SYSTEM = 'system',
  NETWORK = 'network',
  SECURITY = 'security',
  MONITORING = 'monitoring',
  MAINTENANCE = 'maintenance',
  TROUBLESHOOTING = 'troubleshooting',
  CUSTOM = 'custom'
}

export interface PowerShellCommand {
  id: UUID;
  name: string;
  command: string;
  description?: string;
  category: CommandCategory;
  type: CommandType;
  parameters?: CommandParameter[];
  timeout: number;
  requiresElevation: boolean;
  tags?: string[];
  isTemplate: boolean;
  createdBy: UUID;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface CommandParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'choice';
  description?: string;
  required: boolean;
  defaultValue?: unknown;
  choices?: string[];
  validation?: {
    pattern?: string;
    min?: number;
    max?: number;
    minLength?: number;
    maxLength?: number;
  };
}

export interface CommandExecution {
  id: UUID;
  commandId?: UUID;
  agentId: UUID;
  command: string;
  parameters?: Record<string, unknown>;
  status: CommandStatus;
  priority: Priority;
  timeout: number;
  startTime?: Timestamp;
  endTime?: Timestamp;
  duration?: number;
  output?: string;
  errorOutput?: string;
  exitCode?: number;
  pid?: number;
  killedByTimeout: boolean;
  retryCount: number;
  maxRetries: number;
  scheduledFor?: Timestamp;
  executedBy: UUID;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface CommandHistory {
  id: UUID;
  executionId: UUID;
  agentId: UUID;
  command: string;
  status: CommandStatus;
  exitCode?: number;
  duration?: number;
  executedBy: UUID;
  executedAt: Timestamp;
}

export interface CommandTemplate {
  id: UUID;
  name: string;
  description: string;
  command: string;
  parameters: CommandParameter[];
  category: CommandCategory;
  tags: string[];
  isPublic: boolean;
  usageCount: number;
  rating?: number;
  createdBy: UUID;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface ScheduledTask {
  id: UUID;
  name: string;
  description?: string;
  commandId: UUID;
  agentIds: UUID[];
  groupIds?: UUID[];
  cronExpression: string;
  timezone: string;
  enabled: boolean;
  parameters?: Record<string, unknown>;
  maxRetries: number;
  retryDelay: number;
  timeout: number;
  nextRunTime?: Timestamp;
  lastRunTime?: Timestamp;
  lastStatus?: CommandStatus;
  createdBy: UUID;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

// Request/Response types
export interface CommandExecutionRequest {
  command: string;
  parameters?: Record<string, unknown>;
  timeout?: number;
  priority?: Priority;
  scheduledFor?: Timestamp;
  maxRetries?: number;
}

export interface BulkCommandExecutionRequest {
  agentIds: UUID[];
  groupIds?: UUID[];
  command: string;
  parameters?: Record<string, unknown>;
  timeout?: number;
  priority?: Priority;
  scheduledFor?: Timestamp;
  maxRetries?: number;
  continueOnError?: boolean;
}

export interface CommandCreateRequest {
  name: string;
  command: string;
  description?: string;
  category: CommandCategory;
  type?: CommandType;
  parameters?: CommandParameter[];
  timeout?: number;
  requiresElevation?: boolean;
  tags?: string[];
  isTemplate?: boolean;
}

export interface CommandUpdateRequest {
  name?: string;
  command?: string;
  description?: string;
  category?: CommandCategory;
  parameters?: CommandParameter[];
  timeout?: number;
  requiresElevation?: boolean;
  tags?: string[];
}

export interface CommandSearchRequest {
  query?: string;
  category?: CommandCategory;
  type?: CommandType;
  tags?: string[];
  isTemplate?: boolean;
  createdBy?: UUID;
  page?: number;
  limit?: number;
}

export interface CommandExecutionListRequest {
  agentId?: UUID;
  status?: CommandStatus;
  priority?: Priority;
  dateFrom?: Timestamp;
  dateTo?: Timestamp;
  executedBy?: UUID;
  page?: number;
  limit?: number;
}

// AI-generated command types
export interface AICommandRequest {
  description: string;
  context?: string;
  platform?: 'windows' | 'linux' | 'macos';
  language?: 'powershell' | 'bash' | 'cmd';
  safetyLevel?: 'safe' | 'moderate' | 'advanced';
}

export interface AICommandResponse {
  command: string;
  explanation: string;
  warnings?: string[];
  category: CommandCategory;
  estimatedRisk: 'low' | 'medium' | 'high';
  requiresElevation: boolean;
  alternativeCommands?: string[];
}