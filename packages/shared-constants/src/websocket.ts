// WebSocket-related constants

import { WebSocketMessageType } from '@dexagent/shared-types';

// WebSocket message types
export const WS_MESSAGE_TYPES = {
  // Agent messages
  AGENT_REGISTER: 'agent_register' as WebSocketMessageType,
  AGENT_HEARTBEAT: 'agent_heartbeat' as WebSocketMessageType,
  AGENT_DISCONNECT: 'agent_disconnect' as WebSocketMessageType,
  AGENT_STATUS_UPDATE: 'agent_status_update' as WebSocketMessageType,
  AGENT_METRICS: 'agent_metrics' as WebSocketMessageType,
  
  // Command messages
  COMMAND_EXECUTE: 'command_execute' as WebSocketMessageType,
  COMMAND_RESULT: 'command_result' as WebSocketMessageType,
  COMMAND_STATUS_UPDATE: 'command_status_update' as WebSocketMessageType,
  COMMAND_CANCEL: 'command_cancel' as WebSocketMessageType,
  
  // System messages
  SYSTEM_ALERT: 'system_alert' as WebSocketMessageType,
  SYSTEM_NOTIFICATION: 'system_notification' as WebSocketMessageType,
  SYSTEM_HEALTH: 'system_health' as WebSocketMessageType,
  
  // Authentication messages
  AUTH_TOKEN: 'auth_token' as WebSocketMessageType,
  AUTH_REQUIRED: 'auth_required' as WebSocketMessageType,
  AUTH_SUCCESS: 'auth_success' as WebSocketMessageType,
  AUTH_FAILED: 'auth_failed' as WebSocketMessageType,
  
  // Error messages
  ERROR: 'error' as WebSocketMessageType,
  VALIDATION_ERROR: 'validation_error' as WebSocketMessageType,
  
  // Connection messages
  PING: 'ping' as WebSocketMessageType,
  PONG: 'pong' as WebSocketMessageType,
  RECONNECT: 'reconnect' as WebSocketMessageType
} as const;

// WebSocket connection states
export const WS_CONNECTION_STATES = {
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3
} as const;

// WebSocket ready states
export const WS_READY_STATES = {
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  DISCONNECTING: 'disconnecting',
  DISCONNECTED: 'disconnected',
  ERROR: 'error'
} as const;

// WebSocket configuration
export const WS_CONFIG = {
  // Connection timeouts (milliseconds)
  CONNECTION_TIMEOUT: 10000, // 10 seconds
  PING_INTERVAL: 30000, // 30 seconds
  PONG_TIMEOUT: 5000, // 5 seconds
  
  // Reconnection settings
  RECONNECT_DELAY_BASE: 1000, // 1 second
  RECONNECT_DELAY_MAX: 30000, // 30 seconds
  RECONNECT_DELAY_MULTIPLIER: 1.5,
  MAX_RECONNECT_ATTEMPTS: 10,
  
  // Message handling
  MAX_MESSAGE_SIZE: 1024 * 1024, // 1MB
  MESSAGE_QUEUE_SIZE: 1000,
  
  // Agent specific
  AGENT_HEARTBEAT_INTERVAL: 30000, // 30 seconds
  AGENT_HEARTBEAT_TIMEOUT: 90000, // 90 seconds (3 missed heartbeats)
  
  // Dashboard specific
  DASHBOARD_UPDATE_INTERVAL: 5000, // 5 seconds
  DASHBOARD_METRICS_INTERVAL: 60000 // 1 minute
} as const;

// WebSocket error codes
export const WS_ERROR_CODES = {
  // Standard WebSocket close codes
  NORMAL_CLOSURE: 1000,
  GOING_AWAY: 1001,
  PROTOCOL_ERROR: 1002,
  UNSUPPORTED_DATA: 1003,
  NO_STATUS_RECEIVED: 1005,
  ABNORMAL_CLOSURE: 1006,
  INVALID_FRAME_PAYLOAD_DATA: 1007,
  POLICY_VIOLATION: 1008,
  MESSAGE_TOO_BIG: 1009,
  MANDATORY_EXTENSION: 1010,
  INTERNAL_ERROR: 1011,
  SERVICE_RESTART: 1012,
  TRY_AGAIN_LATER: 1013,
  BAD_GATEWAY: 1014,
  TLS_HANDSHAKE: 1015,
  
  // Custom application codes
  AUTHENTICATION_FAILED: 4001,
  AUTHORIZATION_FAILED: 4002,
  INVALID_MESSAGE_FORMAT: 4003,
  RATE_LIMIT_EXCEEDED: 4004,
  AGENT_ALREADY_CONNECTED: 4005,
  INVALID_AGENT_ID: 4006,
  COMMAND_EXECUTION_FAILED: 4007,
  SYSTEM_OVERLOADED: 4008
} as const;

// WebSocket endpoints
export const WS_ENDPOINTS = {
  AGENT: '/api/v1/ws/agent',
  DASHBOARD: '/api/v1/ws/dashboard',
  ADMIN: '/api/v1/ws/admin'
} as const;

// Message priorities for queue processing
export const MESSAGE_PRIORITIES = {
  CRITICAL: 1,    // PING, PONG, AUTH
  HIGH: 2,        // Errors, Alerts
  NORMAL: 3,      // Commands, Status updates
  LOW: 4          // Metrics, Notifications
} as const;

// WebSocket event names
export const WS_EVENTS = {
  // Connection events
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  DISCONNECTED: 'disconnected',
  RECONNECTING: 'reconnecting',
  ERROR: 'error',
  
  // Message events
  MESSAGE: 'message',
  MESSAGE_SENT: 'message_sent',
  MESSAGE_FAILED: 'message_failed',
  
  // Agent events
  AGENT_CONNECTED: 'agent_connected',
  AGENT_DISCONNECTED: 'agent_disconnected',
  AGENT_HEARTBEAT: 'agent_heartbeat',
  
  // Command events
  COMMAND_STARTED: 'command_started',
  COMMAND_COMPLETED: 'command_completed',
  COMMAND_FAILED: 'command_failed',
  
  // System events
  SYSTEM_ALERT: 'system_alert',
  HEALTH_CHECK: 'health_check'
} as const;

// Authentication token types
export const AUTH_TOKEN_TYPES = {
  JWT: 'jwt',
  API_KEY: 'api_key',
  SESSION: 'session'
} as const;

// Message validation rules
export const MESSAGE_VALIDATION = {
  MAX_MESSAGE_SIZE: 1024 * 1024, // 1MB
  REQUIRED_FIELDS: ['type', 'id', 'timestamp'],
  MAX_FIELD_LENGTH: {
    type: 50,
    id: 100,
    agentId: 100,
    userId: 100
  }
} as const;

// Connection limits
export const CONNECTION_LIMITS = {
  MAX_CONNECTIONS_PER_IP: 10,
  MAX_AGENT_CONNECTIONS: 1000,
  MAX_DASHBOARD_CONNECTIONS: 100,
  MAX_ADMIN_CONNECTIONS: 10,
  CONNECTION_RATE_LIMIT: 5 // connections per minute per IP
} as const;