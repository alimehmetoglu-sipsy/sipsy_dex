# @dexagent/shared-types

Shared TypeScript types for the DexAgent monorepo.

## Overview

This package contains all the shared TypeScript type definitions used across the DexAgent platform, including types for agents, commands, WebSocket communication, users, API requests/responses, and system configuration.

## Installation

```bash
npm install @dexagent/shared-types
```

## Usage

```typescript
import { Agent, CommandExecution, WebSocketMessage } from '@dexagent/shared-types';

// Use the types in your code
const agent: Agent = {
  id: 'agent-001',
  name: 'Windows-PC-01',
  hostname: 'DESKTOP-ABC123',
  // ... other properties
};
```

## Type Categories

### Agent Types (`agent.ts`)
- `Agent` - Core agent interface
- `AgentStatus` - Agent status enumeration
- `AgentMetrics` - System metrics from agents
- `AgentGroup` - Agent grouping
- `AgentCapabilities` - Agent feature capabilities

### Command Types (`command.ts`)
- `PowerShellCommand` - Command definitions
- `CommandExecution` - Command execution tracking
- `CommandStatus` - Execution status enumeration
- `CommandParameter` - Command parameter definitions
- `ScheduledTask` - Scheduled command execution

### WebSocket Types (`websocket.ts`)
- `WebSocketMessage` - All WebSocket message types
- `WebSocketMessageType` - Message type enumeration
- Agent communication messages
- Command execution messages
- System notification messages

### User Types (`user.ts`)
- `User` - User account information
- `UserRole` - User role enumeration
- `Permission` - Permission enumeration
- `UserSession` - Session management
- `AuditLog` - User activity tracking

### API Types (`api.ts`)
- `APIResponse` - Standard API response wrapper
- `APIError` - Error response format
- `PaginatedResponse` - Paginated data responses
- File upload and download types
- Batch operation types

### System Types (`system.ts`)
- `SystemInfo` - System information
- `SystemConfiguration` - Application configuration
- `Alert` - System alerts and notifications
- `License` - License management
- `MaintenanceWindow` - Maintenance scheduling

### Common Types (`common.ts`)
- `UUID` - Unique identifier type
- `Timestamp` - ISO 8601 timestamp
- `Status` - General status enumeration
- `Priority` - Priority levels
- `HealthCheck` - Health check interface
- `SystemMetrics` - Performance metrics

## Type Safety

All types are strictly typed with TypeScript and include:
- Required vs optional properties
- Enum constraints
- Generic types for reusability
- Utility types for request/response patterns

## Building

```bash
npm run build
```

This compiles the TypeScript files to JavaScript and generates type declaration files in the `dist/` directory.

## Development

```bash
# Watch mode for development
npm run build:watch

# Type checking
npm run type-check

# Linting
npm run lint
```

## Versioning

This package follows semantic versioning and is versioned together with the main DexAgent application.

## Contributing

When adding new types:
1. Follow existing naming conventions
2. Use descriptive interface names
3. Include JSDoc comments for complex types
4. Export from the main `index.ts` file
5. Update this README if adding new categories

## Dependencies

This package has no runtime dependencies and minimal dev dependencies:
- TypeScript for compilation
- ESLint for code quality
- Jest for testing (if tests are added)

## License

MIT