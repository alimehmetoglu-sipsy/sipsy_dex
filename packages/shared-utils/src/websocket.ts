// WebSocket utility functions

import { WebSocketMessage, WebSocketMessageType } from '@dexagent/shared-types';
import { generateRequestId, getCurrentTimestamp } from './index';

/**
 * Creates a WebSocket message with proper formatting
 */
export function createWebSocketMessage<T extends WebSocketMessage>(
  type: WebSocketMessageType,
  data: T['data'],
  options: {
    agentId?: string;
    userId?: string;
  } = {}
): T {
  return {
    type,
    id: generateRequestId(),
    timestamp: getCurrentTimestamp(),
    agentId: options.agentId,
    userId: options.userId,
    data
  } as T;
}

/**
 * Validates WebSocket message format
 */
export function validateWebSocketMessage(message: unknown): message is WebSocketMessage {
  if (!message || typeof message !== 'object') {
    return false;
  }
  
  const msg = message as Record<string, unknown>;
  
  return (
    typeof msg.type === 'string' &&
    typeof msg.id === 'string' &&
    typeof msg.timestamp === 'string' &&
    msg.data !== undefined &&
    Object.values(WebSocketMessageType).includes(msg.type as WebSocketMessageType)
  );
}

/**
 * Parses WebSocket message from string
 */
export function parseWebSocketMessage(data: string): WebSocketMessage | null {
  try {
    const parsed = JSON.parse(data);
    return validateWebSocketMessage(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

/**
 * Serializes WebSocket message to string
 */
export function serializeWebSocketMessage(message: WebSocketMessage): string {
  return JSON.stringify(message);
}

/**
 * Creates a heartbeat message
 */
export function createHeartbeatMessage(agentId: string, metrics?: any) {
  return createWebSocketMessage(
    WebSocketMessageType.AGENT_HEARTBEAT,
    {
      agentId,
      timestamp: getCurrentTimestamp(),
      status: 'online' as const,
      metrics
    },
    { agentId }
  );
}

/**
 * Creates a command execution message
 */
export function createCommandExecuteMessage(
  agentId: string,
  executionId: string,
  command: string,
  options: {
    parameters?: Record<string, unknown>;
    timeout?: number;
    workingDirectory?: string;
    environment?: Record<string, string>;
  } = {}
) {
  return createWebSocketMessage(
    WebSocketMessageType.COMMAND_EXECUTE,
    {
      executionId,
      command,
      timeout: options.timeout || 30,
      ...options
    },
    { agentId }
  );
}

/**
 * Creates a command result message
 */
export function createCommandResultMessage(
  agentId: string,
  executionId: string,
  result: {
    status: 'completed' | 'failed' | 'timeout' | 'cancelled';
    output?: string;
    errorOutput?: string;
    exitCode?: number;
    duration: number;
    error?: string;
  }
) {
  return createWebSocketMessage(
    WebSocketMessageType.COMMAND_RESULT,
    {
      executionId,
      ...result
    },
    { agentId }
  );
}

/**
 * Creates a system alert message
 */
export function createSystemAlertMessage(
  alert: {
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
  }
) {
  return createWebSocketMessage(
    WebSocketMessageType.SYSTEM_ALERT,
    alert
  );
}

/**
 * Creates an error message
 */
export function createErrorMessage(
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  },
  options: { agentId?: string; userId?: string } = {}
) {
  return createWebSocketMessage(
    WebSocketMessageType.ERROR,
    error,
    options
  );
}

/**
 * Creates a ping message
 */
export function createPingMessage(agentId?: string) {
  return createWebSocketMessage(
    WebSocketMessageType.PING,
    {},
    { agentId }
  );
}

/**
 * Creates a pong message
 */
export function createPongMessage(agentId?: string) {
  return createWebSocketMessage(
    WebSocketMessageType.PONG,
    {},
    { agentId }
  );
}

/**
 * Determines if a message requires authentication
 */
export function requiresAuthentication(messageType: WebSocketMessageType): boolean {
  const publicMessageTypes = [
    WebSocketMessageType.PING,
    WebSocketMessageType.PONG,
    WebSocketMessageType.AUTH_TOKEN,
    WebSocketMessageType.AUTH_REQUIRED
  ];
  
  return !publicMessageTypes.includes(messageType);
}

/**
 * Gets message priority for queue processing
 */
export function getMessagePriority(messageType: WebSocketMessageType): number {
  const priorityMap: Record<WebSocketMessageType, number> = {
    [WebSocketMessageType.PING]: 1,
    [WebSocketMessageType.PONG]: 1,
    [WebSocketMessageType.AUTH_TOKEN]: 2,
    [WebSocketMessageType.AUTH_REQUIRED]: 2,
    [WebSocketMessageType.AUTH_SUCCESS]: 2,
    [WebSocketMessageType.AUTH_FAILED]: 2,
    [WebSocketMessageType.ERROR]: 3,
    [WebSocketMessageType.VALIDATION_ERROR]: 3,
    [WebSocketMessageType.SYSTEM_ALERT]: 4,
    [WebSocketMessageType.COMMAND_CANCEL]: 5,
    [WebSocketMessageType.COMMAND_EXECUTE]: 6,
    [WebSocketMessageType.COMMAND_RESULT]: 7,
    [WebSocketMessageType.COMMAND_STATUS_UPDATE]: 8,
    [WebSocketMessageType.AGENT_REGISTER]: 9,
    [WebSocketMessageType.AGENT_DISCONNECT]: 9,
    [WebSocketMessageType.AGENT_STATUS_UPDATE]: 10,
    [WebSocketMessageType.AGENT_HEARTBEAT]: 11,
    [WebSocketMessageType.AGENT_METRICS]: 12,
    [WebSocketMessageType.SYSTEM_NOTIFICATION]: 13,
    [WebSocketMessageType.SYSTEM_HEALTH]: 14,
    [WebSocketMessageType.RECONNECT]: 15
  };
  
  return priorityMap[messageType] || 10;
}

/**
 * Checks if message is a response to another message
 */
export function isResponseMessage(messageType: WebSocketMessageType): boolean {
  const responseTypes = [
    WebSocketMessageType.PONG,
    WebSocketMessageType.AUTH_SUCCESS,
    WebSocketMessageType.AUTH_FAILED,
    WebSocketMessageType.COMMAND_RESULT,
    WebSocketMessageType.ERROR,
    WebSocketMessageType.VALIDATION_ERROR
  ];
  
  return responseTypes.includes(messageType);
}

/**
 * Gets the expected response type for a message
 */
export function getExpectedResponseType(messageType: WebSocketMessageType): WebSocketMessageType | null {
  const responseMap: Partial<Record<WebSocketMessageType, WebSocketMessageType>> = {
    [WebSocketMessageType.PING]: WebSocketMessageType.PONG,
    [WebSocketMessageType.AUTH_TOKEN]: WebSocketMessageType.AUTH_SUCCESS,
    [WebSocketMessageType.COMMAND_EXECUTE]: WebSocketMessageType.COMMAND_RESULT,
  };
  
  return responseMap[messageType] || null;
}

/**
 * Calculates message size in bytes
 */
export function calculateMessageSize(message: WebSocketMessage): number {
  return new Blob([serializeWebSocketMessage(message)]).size;
}

/**
 * Compresses message data if beneficial
 */
export function compressMessage(message: WebSocketMessage): WebSocketMessage {
  // Simple compression by removing unnecessary whitespace from JSON strings
  if (typeof message.data === 'object' && message.data !== null) {
    const compressed = JSON.parse(JSON.stringify(message.data));
    return { ...message, data: compressed };
  }
  
  return message;
}