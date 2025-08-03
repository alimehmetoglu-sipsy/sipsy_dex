// WebSocket message types for real-time communication

import { UUID, Timestamp } from './common';
import { Agent, AgentMetrics, AgentHeartbeat } from './agent';
import { CommandExecution, CommandStatus } from './command';

export enum WebSocketMessageType {
  // Agent messages
  AGENT_REGISTER = 'agent_register',
  AGENT_HEARTBEAT = 'agent_heartbeat',
  AGENT_DISCONNECT = 'agent_disconnect',
  AGENT_STATUS_UPDATE = 'agent_status_update',
  AGENT_METRICS = 'agent_metrics',
  
  // Command messages
  COMMAND_EXECUTE = 'command_execute',
  COMMAND_RESULT = 'command_result',
  COMMAND_STATUS_UPDATE = 'command_status_update',
  COMMAND_CANCEL = 'command_cancel',
  
  // System messages
  SYSTEM_ALERT = 'system_alert',
  SYSTEM_NOTIFICATION = 'system_notification',
  SYSTEM_HEALTH = 'system_health',
  
  // Authentication messages
  AUTH_TOKEN = 'auth_token',
  AUTH_REQUIRED = 'auth_required',
  AUTH_SUCCESS = 'auth_success',
  AUTH_FAILED = 'auth_failed',
  
  // Error messages
  ERROR = 'error',
  VALIDATION_ERROR = 'validation_error',
  
  // Connection messages
  PING = 'ping',
  PONG = 'pong',
  RECONNECT = 'reconnect'
}

export interface BaseWebSocketMessage {
  type: WebSocketMessageType;
  id: UUID;
  timestamp: Timestamp;
  agentId?: UUID;
  userId?: UUID;
}

// Agent WebSocket Messages
export interface AgentRegisterMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.AGENT_REGISTER;
  data: {
    agent: Omit<Agent, 'id' | 'createdAt' | 'updatedAt'>;
    authToken?: string;
  };
}

export interface AgentHeartbeatMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.AGENT_HEARTBEAT;
  data: AgentHeartbeat & {
    metrics?: AgentMetrics;
  };
}

export interface AgentDisconnectMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.AGENT_DISCONNECT;
  data: {
    reason?: string;
  };
}

export interface AgentStatusUpdateMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.AGENT_STATUS_UPDATE;
  data: {
    status: Agent['status'];
    lastHeartbeat: Timestamp;
    error?: string;
  };
}

export interface AgentMetricsMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.AGENT_METRICS;
  data: AgentMetrics;
}

// Command WebSocket Messages
export interface CommandExecuteMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.COMMAND_EXECUTE;
  data: {
    executionId: UUID;
    command: string;
    parameters?: Record<string, unknown>;
    timeout: number;
    workingDirectory?: string;
    environment?: Record<string, string>;
  };
}

export interface CommandResultMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.COMMAND_RESULT;
  data: {
    executionId: UUID;
    status: CommandStatus;
    output?: string;
    errorOutput?: string;
    exitCode?: number;
    duration: number;
    error?: string;
  };
}

export interface CommandStatusUpdateMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.COMMAND_STATUS_UPDATE;
  data: {
    executionId: UUID;
    status: CommandStatus;
    pid?: number;
    progress?: number;
    message?: string;
  };
}

export interface CommandCancelMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.COMMAND_CANCEL;
  data: {
    executionId: UUID;
    reason?: string;
  };
}

// System WebSocket Messages
export interface SystemAlertMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.SYSTEM_ALERT;
  data: {
    level: 'info' | 'warning' | 'error' | 'critical';
    title: string;
    message: string;
    source: string;
    actionRequired?: boolean;
    actions?: Array<{
      label: string;
      action: string;
      data?: Record<string, unknown>;
    }>;
  };
}

export interface SystemNotificationMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.SYSTEM_NOTIFICATION;
  data: {
    title: string;
    message: string;
    type: 'success' | 'info' | 'warning' | 'error';
    persistent?: boolean;
    timeout?: number;
  };
}

export interface SystemHealthMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.SYSTEM_HEALTH;
  data: {
    status: 'healthy' | 'unhealthy' | 'degraded';
    services: Record<string, 'up' | 'down' | 'degraded'>;
    metrics: {
      activeAgents: number;
      totalAgents: number;
      activeConnections: number;
      commandsExecuted: number;
      averageResponseTime: number;
    };
  };
}

// Authentication WebSocket Messages
export interface AuthTokenMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.AUTH_TOKEN;
  data: {
    token: string;
  };
}

export interface AuthRequiredMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.AUTH_REQUIRED;
  data: {
    message: string;
  };
}

export interface AuthSuccessMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.AUTH_SUCCESS;
  data: {
    user: {
      id: UUID;
      username: string;
      role: string;
    };
  };
}

export interface AuthFailedMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.AUTH_FAILED;
  data: {
    message: string;
    code: string;
  };
}

// Error WebSocket Messages
export interface ErrorMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.ERROR;
  data: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

export interface ValidationErrorMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.VALIDATION_ERROR;
  data: {
    field: string;
    message: string;
    value?: unknown;
  };
}

// Connection WebSocket Messages
export interface PingMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.PING;
  data: Record<string, never>;
}

export interface PongMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.PONG;
  data: Record<string, never>;
}

export interface ReconnectMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.RECONNECT;
  data: {
    reason: string;
    delay: number;
  };
}

// Union type for all WebSocket messages
export type WebSocketMessage =
  | AgentRegisterMessage
  | AgentHeartbeatMessage
  | AgentDisconnectMessage
  | AgentStatusUpdateMessage
  | AgentMetricsMessage
  | CommandExecuteMessage
  | CommandResultMessage
  | CommandStatusUpdateMessage
  | CommandCancelMessage
  | SystemAlertMessage
  | SystemNotificationMessage
  | SystemHealthMessage
  | AuthTokenMessage
  | AuthRequiredMessage
  | AuthSuccessMessage
  | AuthFailedMessage
  | ErrorMessage
  | ValidationErrorMessage
  | PingMessage
  | PongMessage
  | ReconnectMessage;

// WebSocket connection state
export interface WebSocketConnectionState {
  connected: boolean;
  connecting: boolean;
  lastPing?: Timestamp;
  lastPong?: Timestamp;
  reconnectAttempts: number;
  maxReconnectAttempts: number;
  reconnectDelay: number;
  error?: string;
}

// WebSocket client configuration
export interface WebSocketClientConfig {
  url: string;
  protocols?: string[];
  heartbeatInterval: number;
  reconnectAttempts: number;
  reconnectDelay: number;
  timeout: number;
  authToken?: string;
  autoReconnect: boolean;
}