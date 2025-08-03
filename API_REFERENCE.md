# API_REFERENCE.md

## Base Configuration

- **Base URL**: `http://localhost:8080/api/v1`
- **Content-Type**: `application/json`
- **Authentication**: Bearer JWT token (except for `/health` and `/auth/login`)

## Authentication

### POST /auth/login
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### GET /auth/me
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z"
}
```

## Agent Management

### GET /agents
List all registered agents.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Items per page (default: 50)
- `status` (string, optional): Filter by status (`online`, `offline`, `unknown`)

**Response:**
```json
{
  "agents": [
    {
      "id": "agent-001",
      "name": "Windows-PC-01",
      "hostname": "DESKTOP-ABC123",
      "ip_address": "192.168.1.100",
      "port": 8080,
      "status": "online",
      "last_heartbeat": "2025-01-01T12:00:00Z",
      "group_id": 1,
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 50
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8080/api/v1/agents?status=online" \
  -H "Authorization: Bearer <token>"
```

### POST /agents/register
Register a new agent (typically called by agent).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Windows-PC-02",
  "hostname": "DESKTOP-XYZ789",
  "ip_address": "192.168.1.101",
  "port": 8080,
  "group_id": 1
}
```

**Response:**
```json
{
  "id": "agent-002",
  "name": "Windows-PC-02",
  "hostname": "DESKTOP-XYZ789",
  "ip_address": "192.168.1.101",
  "port": 8080,
  "status": "online",
  "group_id": 1,
  "created_at": "2025-01-01T12:30:00Z"
}
```

### GET /agents/{id}
Get specific agent details.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `id` (string): Agent ID

**Response:**
```json
{
  "id": "agent-001",
  "name": "Windows-PC-01",
  "hostname": "DESKTOP-ABC123",
  "ip_address": "192.168.1.100",
  "port": 8080,
  "status": "online",
  "last_heartbeat": "2025-01-01T12:00:00Z",
  "group_id": 1,
  "metrics": {
    "cpu_usage": 25.5,
    "memory_usage": 60.2,
    "disk_usage": 45.8
  },
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

### PUT /agents/{id}
Update agent information.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `id` (string): Agent ID

**Request Body:**
```json
{
  "name": "Windows-PC-01-Updated",
  "group_id": 2
}
```

**Response:**
```json
{
  "id": "agent-001",
  "name": "Windows-PC-01-Updated",
  "hostname": "DESKTOP-ABC123",
  "ip_address": "192.168.1.100",
  "port": 8080,
  "status": "online",
  "group_id": 2,
  "updated_at": "2025-01-01T12:30:00Z"
}
```

### DELETE /agents/{id}
Remove agent from system.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `id` (string): Agent ID

**Response:**
```json
{
  "message": "Agent removed successfully",
  "id": "agent-001"
}
```

## PowerShell Commands

### GET /commands/saved
List saved PowerShell commands.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `category` (string, optional): Filter by category
- `search` (string, optional): Search in name/description

**Response:**
```json
{
  "commands": [
    {
      "id": 1,
      "name": "Get System Info",
      "command": "Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory",
      "description": "Retrieve basic system information",
      "category": "system",
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

### POST /commands/saved
Create new saved command.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Get Disk Usage",
  "command": "Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace",
  "description": "Check disk usage for all drives",
  "category": "system"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "Get Disk Usage",
  "command": "Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace",
  "description": "Check disk usage for all drives",
  "category": "system",
  "created_at": "2025-01-01T12:00:00Z"
}
```

### PUT /commands/saved/{id}
Update saved command.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `id` (int): Command ID

**Request Body:**
```json
{
  "name": "Get Disk Usage (Updated)",
  "description": "Check disk usage for all drives with percentage"
}
```

### DELETE /commands/saved/{id}
Delete saved command.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `id` (int): Command ID

**Response:**
```json
{
  "message": "Command deleted successfully",
  "id": 2
}
```

### POST /commands/agent/{agent_id}/execute
Execute command on specific agent.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `agent_id` (string): Target agent ID

**Request Body:**
```json
{
  "command": "Get-Process | Where-Object {$_.ProcessName -eq 'notepad'}",
  "timeout": 30
}
```

**Response:**
```json
{
  "execution_id": "exec-001",
  "agent_id": "agent-001",
  "command": "Get-Process | Where-Object {$_.ProcessName -eq 'notepad'}",
  "status": "pending",
  "created_at": "2025-01-01T12:00:00Z"
}
```

## AI Features

### GET /commands/ai/status
Check AI service availability.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "available": true,
  "provider": "openai",
  "model": "gpt-3.5-turbo",
  "configured": true
}
```

### POST /ai/generate-command
Generate PowerShell command using AI.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "description": "List all running services that start with 'Windows'",
  "context": "Windows Server 2019"
}
```

**Response:**
```json
{
  "command": "Get-Service | Where-Object {$_.Name -like 'Windows*' -and $_.Status -eq 'Running'}",
  "explanation": "This command retrieves all services where the name starts with 'Windows' and the service is currently running.",
  "category": "services"
}
```

## System Endpoints

### GET /system/health
System health check (no authentication required).

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00Z",
  "version": "3.3.0",
  "database": "connected",
  "services": {
    "api": "running",
    "websocket": "running",
    "ai": "available"
  }
}
```

### GET /system/info
Get system information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "version": "3.3.0",
  "uptime": "2 days, 4 hours",
  "agents_online": 5,
  "agents_total": 8,
  "commands_executed_today": 142,
  "database_size": "45.2 MB",
  "memory_usage": "512 MB"
}
```

### GET /system/metrics
Get system metrics.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "timestamp": "2025-01-01T12:00:00Z",
  "agents": {
    "total": 8,
    "online": 5,
    "offline": 3
  },
  "commands": {
    "executed_today": 142,
    "total_saved": 25,
    "success_rate": 98.5
  },
  "performance": {
    "avg_response_time": 150,
    "requests_per_minute": 45
  }
}
```

## Settings

### GET /settings
Get system settings.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "chatgpt_api_key": "sk-****",
  "chatgpt_model": "gpt-3.5-turbo",
  "system_name": "DexAgent",
  "max_agents": 100,
  "command_timeout": 300,
  "updated_at": "2025-01-01T10:00:00Z"
}
```

### POST /settings
Update system settings.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "chatgpt_api_key": "sk-new-api-key",
  "chatgpt_model": "gpt-4",
  "max_agents": 150,
  "command_timeout": 600
}
```

**Response:**
```json
{
  "id": 1,
  "chatgpt_api_key": "sk-****",
  "chatgpt_model": "gpt-4",
  "system_name": "DexAgent",
  "max_agents": 150,
  "command_timeout": 600,
  "updated_at": "2025-01-01T12:30:00Z"
}
```

## WebSocket Endpoints

### /api/v1/ws/agent/{agent_id}
Agent communication WebSocket.

**Authentication:** JWT token in query parameter `?token=<jwt_token>`

**Message Types:**

#### Agent Registration
```json
{
  "type": "register",
  "data": {
    "agent_id": "agent-001",
    "hostname": "DESKTOP-ABC123",
    "ip_address": "192.168.1.100"
  }
}
```

#### Command Execution
```json
{
  "type": "execute_command",
  "data": {
    "command_id": "cmd-001",
    "command": "Get-Process",
    "timeout": 30
  }
}
```

#### Command Result
```json
{
  "type": "command_result",
  "data": {
    "command_id": "cmd-001",
    "output": "ProcessName     Id  CPU\n----------     --  ---\nchrome       1234  25.5",
    "exit_code": 0,
    "execution_time": 1.5,
    "error": null
  }
}
```

#### Heartbeat
```json
{
  "type": "heartbeat",
  "data": {
    "timestamp": "2025-01-01T12:00:00Z",
    "metrics": {
      "cpu_usage": 25.5,
      "memory_usage": 60.2,
      "disk_usage": 45.8
    }
  }
}
```

### /api/v1/ws/dashboard
Dashboard real-time updates WebSocket.

**Authentication:** JWT token in query parameter `?token=<jwt_token>`

**Message Types:**

#### Agent Status Update
```json
{
  "type": "agent_status",
  "data": {
    "agent_id": "agent-001",
    "status": "online",
    "last_heartbeat": "2025-01-01T12:00:00Z"
  }
}
```

#### Command Execution Update
```json
{
  "type": "command_execution",
  "data": {
    "execution_id": "exec-001",
    "agent_id": "agent-001",
    "status": "completed",
    "output": "Command executed successfully"
  }
}
```

#### System Alert
```json
{
  "type": "system_alert",
  "data": {
    "level": "warning",
    "message": "Agent agent-002 has been offline for 5 minutes",
    "timestamp": "2025-01-01T12:00:00Z"
  }
}
```

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "username",
        "message": "Username is required"
      }
    ]
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| **200** | Success |
| **201** | Created |
| **400** | Bad Request - Invalid input |
| **401** | Unauthorized - Invalid or missing token |
| **403** | Forbidden - Insufficient permissions |
| **404** | Not Found - Resource not found |
| **422** | Unprocessable Entity - Validation error |
| **500** | Internal Server Error |
| **503** | Service Unavailable |

### Common Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `AUTHENTICATION_ERROR` | Invalid credentials |
| `AUTHORIZATION_ERROR` | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `AGENT_OFFLINE` | Target agent is not online |
| `COMMAND_TIMEOUT` | Command execution timed out |
| `AI_SERVICE_ERROR` | AI service unavailable |
| `DATABASE_ERROR` | Database operation failed |

## Rate Limiting

- **Authentication endpoints**: 5 requests per minute per IP
- **API endpoints**: 100 requests per minute per user
- **WebSocket connections**: 10 connections per user

## API Versioning

Current API version: `v1`

Version is specified in the URL path: `/api/v1/`

---

**API Version**: 3.3 - Optimized for Claude Code integration

For additional information, see:
- [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md) - Project overview
- [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md) - System architecture
- [DEVELOPMENT_SETUP.md](./DEVELOPMENT_SETUP.md) - Development setup