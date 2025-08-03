# @dexagent/shared-utils

Shared utility functions for the DexAgent monorepo.

## Overview

This package contains common utility functions used across the DexAgent platform, including utilities for date/time handling, string manipulation, validation, ID generation, command parsing, WebSocket operations, formatting, error handling, data manipulation, and basic cryptographic operations.

## Installation

```bash
npm install @dexagent/shared-utils
```

## Usage

```typescript
import { 
  formatTimestamp, 
  generateRequestId, 
  validateAgentId,
  parseCommandOutput 
} from '@dexagent/shared-utils';

// Format current timestamp
const now = formatTimestamp();

// Generate unique request ID
const requestId = generateRequestId();

// Validate agent ID format
const isValid = validateAgentId('agent-001');

// Parse PowerShell command output
const parsed = parseCommandOutput(commandOutput);
```

## Utility Categories

### DateTime Utilities (`datetime.ts`)
- `formatTimestamp()` - Convert Date to ISO 8601 string
- `parseTimestamp()` - Parse ISO 8601 string to Date
- `getCurrentTimestamp()` - Get current timestamp
- `getDurationInSeconds()` - Calculate duration between timestamps
- `formatDuration()` - Format seconds as human-readable duration
- `getRelativeTime()` - Get relative time string ("2 minutes ago")
- `addTime()` - Add time to timestamp

### ID Generation (`id.ts`)
- `generateRequestId()` - Generate UUID v4
- `generateCommandId()` - Generate unique command ID
- `generateSessionId()` - Generate session ID
- `generateExecutionId()` - Generate execution ID
- `generateRandomString()` - Generate random string
- `isValidUUID()` - Validate UUID format
- `generateAgentId()` - Generate agent ID with hostname

### String Utilities (`string.ts`)
- `capitalize()` - Capitalize first letter
- `toCamelCase()` - Convert to camelCase
- `toPascalCase()` - Convert to PascalCase
- `toKebabCase()` - Convert to kebab-case
- `toSnakeCase()` - Convert to snake_case
- `truncate()` - Truncate with suffix
- `slugify()` - Create URL-friendly slug
- `maskString()` - Mask sensitive data
- `getInitials()` - Extract initials from name

### Validation (`validation.ts`)
- `validateAgentId()` - Validate agent ID format
- `validateEmail()` - Email validation
- `validateHostname()` - Hostname validation
- `validateIPAddress()` - IP address validation (IPv4/IPv6)
- `validatePort()` - Port number validation
- `validateUsername()` - Username format validation
- `validatePasswordStrength()` - Password strength check
- `validateURL()` - URL validation
- `sanitizeString()` - Sanitize for safe display

### Command Utilities (`command.ts`)
- `parseCommandOutput()` - Parse PowerShell output into structured data
- `validateCommand()` - Validate command safety and risk level
- `sanitizeCommandParameters()` - Sanitize command parameters
- `validateCommandParameters()` - Validate against parameter definitions
- `estimateExecutionTime()` - Estimate command execution time

### WebSocket Utilities (`websocket.ts`)
- `createWebSocketMessage()` - Create properly formatted WS message
- `validateWebSocketMessage()` - Validate message format
- `parseWebSocketMessage()` - Parse message from string
- `createHeartbeatMessage()` - Create agent heartbeat
- `createCommandExecuteMessage()` - Create command execution message
- `createSystemAlertMessage()` - Create system alert
- `requiresAuthentication()` - Check if message needs auth

### Formatting (`format.ts`)
- `formatBytes()` - Format bytes to human-readable (KB, MB, GB)
- `formatNumber()` - Add thousand separators
- `formatPercentage()` - Format as percentage
- `formatCurrency()` - Format currency with locale
- `formatPhoneNumber()` - Format phone numbers
- `formatCommand()` - Format command for display
- `formatList()` - Format array with proper grammar
- `formatCode()` - Format code preserving structure

### Error Handling (`error.ts`)
- `createAPIError()` - Create standardized API error
- `createValidationError()` - Create validation error
- `createAuthError()` - Create authentication error
- `createNotFoundError()` - Create not found error
- `extractErrorMessage()` - Extract message from any error type
- `safeAsync()` - Safe async execution with error handling
- `retryAsync()` - Retry with exponential backoff
- `createCircuitBreaker()` - Circuit breaker pattern

### Data Utilities (`data.ts`)
- `deepClone()` - Deep clone objects/arrays
- `deepMerge()` - Deep merge objects
- `removeEmpty()` - Remove null/undefined values
- `groupBy()` - Group array by key function
- `unique()` - Remove duplicates
- `chunk()` - Split array into chunks
- `sortBy()` - Multi-criteria sorting
- `paginate()` - Paginate array data
- `pick()` - Pick object properties
- `omit()` - Omit object properties
- `get()` - Get nested value with dot notation
- `set()` - Set nested value with dot notation

### Crypto Utilities (`crypto.ts`)
- `simpleHash()` - Generate hash using djb2 algorithm
- `encodeBase64()` / `decodeBase64()` - Base64 encoding/decoding
- `xorCipher()` - Simple XOR cipher (not secure!)
- `checksum()` - Generate checksum for integrity
- `constantTimeCompare()` - Prevent timing attacks
- `sanitizeForLogging()` - Remove sensitive data from logs
- `generateSalt()` - Generate random salt
- `maskSensitiveData()` - Mask data for display

## Examples

### Working with Timestamps
```typescript
import { formatTimestamp, getRelativeTime, formatDuration } from '@dexagent/shared-utils';

const now = formatTimestamp();
const oneHourAgo = addTime(now, -1, 'hours');
const relative = getRelativeTime(oneHourAgo); // "1 hour ago"
const duration = formatDuration(3661); // "1h 1m 1s"
```

### Command Validation
```typescript
import { validateCommand, parseCommandOutput } from '@dexagent/shared-utils';

const validation = validateCommand('Get-Process');
// { isValid: true, issues: [], riskLevel: 'low' }

const output = parseCommandOutput(commandResult);
// { lines: [...], tables: [...], errors: [...], warnings: [...] }
```

### WebSocket Message Creation
```typescript
import { createHeartbeatMessage, createCommandExecuteMessage } from '@dexagent/shared-utils';

const heartbeat = createHeartbeatMessage('agent-001', { cpu: 25.5 });
const command = createCommandExecuteMessage('agent-001', 'exec-123', 'Get-Date');
```

### Data Manipulation
```typescript
import { groupBy, sortBy, paginate } from '@dexagent/shared-utils';

const agents = [...];
const byStatus = groupBy(agents, agent => agent.status);
const sorted = sortBy(agents, { key: a => a.name, direction: 'asc' });
const page = paginate(agents, 1, 10);
```

### Error Handling
```typescript
import { safeAsync, retryAsync, createAPIError } from '@dexagent/shared-utils';

const result = await safeAsync(() => riskyOperation());
if (!result.success) {
  console.error(result.error);
}

const retried = await retryAsync(() => networkCall(), { maxAttempts: 3 });
```

## Type Safety

All utilities are fully typed with TypeScript and work seamlessly with types from `@dexagent/shared-types`.

## Building

```bash
npm run build
```

## Testing

```bash
npm test
npm run test:watch
npm run test:coverage
```

## Dependencies

- `@dexagent/shared-types` - Shared type definitions

## Contributing

When adding new utilities:
1. Follow existing patterns and naming conventions
2. Include proper TypeScript types
3. Add JSDoc comments for complex functions
4. Export from the main `index.ts` file
5. Update this README with examples
6. Add unit tests for new functionality

## License

MIT