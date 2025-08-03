# @dexagent/shared-constants

Shared constants and configuration values for the DexAgent monorepo.

## Overview

This package provides centralized constants, configuration presets, and shared values used across all DexAgent applications. It ensures consistency and maintainability by having a single source of truth for application-wide constants.

## Installation

```bash
# In a workspace package
npm install @dexagent/shared-constants

# Or in the root
npm install --workspace packages/shared-constants
```

## Usage

```typescript
import {
  APP_NAME,
  API_PATHS,
  HTTP_STATUS,
  WS_MESSAGE_TYPES,
  VALIDATION_PATTERNS,
  ERROR_CODES,
  THEME_COLORS
} from '@dexagent/shared-constants';

// Use application constants
console.log(APP_NAME); // 'DexAgent'

// Use API paths
const endpoint = `${API_PATHS.BASE}${API_PATHS.AGENTS}`;

// Use HTTP status codes
if (response.status === HTTP_STATUS.OK) {
  // Handle success
}

// Use WebSocket message types
websocket.send({
  type: WS_MESSAGE_TYPES.AGENT_REGISTER,
  payload: agentData
});

// Use validation patterns
if (VALIDATION_PATTERNS.EMAIL.test(email)) {
  // Valid email
}

// Use error codes
throw new Error({
  code: ERROR_CODES.AGENT_NOT_FOUND,
  message: 'Agent not found'
});

// Use UI constants
const primaryColor = THEME_COLORS.PRIMARY;
```

## Package Structure

```
src/
├── index.ts              # Main entry point
├── app.ts               # Application-wide constants
├── api.ts               # API-related constants
├── commands.ts          # Command-related constants
├── websocket.ts         # WebSocket constants
├── ui.ts                # UI/Theme constants
├── validation.ts        # Validation patterns and rules
├── errors.ts            # Error codes and messages
└── config.ts            # Configuration presets
```

## Categories

### Application Constants (`app.ts`)
- Application metadata (name, version, description)
- Default configuration values
- Environment settings
- Feature flags
- Application limits
- Cache configuration

### API Constants (`api.ts`)
- API base paths and endpoints
- HTTP status codes and methods
- Content types and headers
- Error codes and timeouts
- Pagination defaults
- File upload constraints

### Command Constants (`commands.ts`)
- Command categories and types
- Default command templates
- Command execution limits
- Validation patterns for commands
- Risk assessment patterns
- Parameter types and templates

### WebSocket Constants (`websocket.ts`)
- Message types and events
- Connection states and configurations
- Error codes and endpoints
- Authentication token types
- Message validation rules
- Connection limits

### UI Constants (`ui.ts`)
- Theme colors (light and dark)
- Component sizes and spacing
- Typography settings
- Animation configurations
- Breakpoints and layout
- Status and priority colors

### Validation Constants (`validation.ts`)
- Regular expression patterns
- Field length limits
- Numeric ranges
- Validation messages
- File type validations
- Sanitization rules

### Error Constants (`errors.ts`)
- Error categories and severity levels
- Application-specific error codes
- User-friendly error messages
- Recovery suggestions
- Logging and reporting configuration
- Retry and circuit breaker settings

### Configuration Constants (`config.ts`)
- Environment-specific configurations
- Default application settings
- Feature toggles and flags
- Performance configurations
- Security presets
- Deployment configurations

## Key Features

### Type Safety
All constants are strongly typed and use TypeScript's `as const` assertions for literal type inference.

### Categorization
Constants are logically grouped into separate modules for better organization and tree-shaking.

### Comprehensive Coverage
Covers all aspects of the application from UI themes to database configurations.

### Environment Support
Provides different configuration presets for development, staging, and production environments.

### Validation Support
Includes comprehensive validation patterns, limits, and error messages.

### Internationalization Ready
Error messages and user-facing strings are centralized for easy localization.

## Examples

### Using API Constants
```typescript
import { API_PATHS, HTTP_STATUS, API_HEADERS } from '@dexagent/shared-constants';

// Build API endpoint
const agentsEndpoint = `${API_PATHS.BASE}${API_PATHS.AGENTS}`;

// Check response status
if (response.status === HTTP_STATUS.OK) {
  // Handle success
} else if (response.status === HTTP_STATUS.UNAUTHORIZED) {
  // Handle authentication error
}

// Set headers
const headers = {
  [API_HEADERS.CONTENT_TYPE]: 'application/json',
  [API_HEADERS.AUTHORIZATION]: `Bearer ${token}`
};
```

### Using Validation Constants
```typescript
import { 
  VALIDATION_PATTERNS, 
  FIELD_LIMITS, 
  VALIDATION_MESSAGES 
} from '@dexagent/shared-constants';

// Validate email
function validateEmail(email: string): { valid: boolean; message?: string } {
  if (!email) {
    return { valid: false, message: VALIDATION_MESSAGES.REQUIRED };
  }
  
  if (email.length > FIELD_LIMITS.EMAIL_MAX) {
    return { valid: false, message: VALIDATION_MESSAGES.TOO_LONG };
  }
  
  if (!VALIDATION_PATTERNS.EMAIL.test(email)) {
    return { valid: false, message: VALIDATION_MESSAGES.INVALID_EMAIL };
  }
  
  return { valid: true };
}
```

### Using UI Constants
```typescript
import { 
  THEME_COLORS, 
  COMPONENT_SIZES, 
  SPACING,
  STATUS_COLORS 
} from '@dexagent/shared-constants';

// Apply theme colors
const buttonStyle = {
  backgroundColor: THEME_COLORS.PRIMARY,
  color: THEME_COLORS.TEXT.INVERSE,
  padding: SPACING.MD,
  height: COMPONENT_SIZES.BUTTON.MD.height
};

// Status indicator
const getStatusColor = (status: string) => {
  return STATUS_COLORS[status] || STATUS_COLORS.UNKNOWN;
};
```

### Using Error Constants
```typescript
import { 
  APPLICATION_ERROR_CODES, 
  ERROR_MESSAGES,
  ERROR_DESCRIPTIONS 
} from '@dexagent/shared-constants';

// Throw application error
throw new ApplicationError({
  code: APPLICATION_ERROR_CODES.AGENT_NOT_FOUND,
  message: ERROR_MESSAGES.AGENT_NOT_FOUND,
  description: ERROR_DESCRIPTIONS[APPLICATION_ERROR_CODES.AGENT_NOT_FOUND]
});
```

## Dependencies

- `@dexagent/shared-types`: TypeScript type definitions
- `typescript`: TypeScript compiler

## Development

```bash
# Build the package
npm run build

# Watch for changes
npm run build:watch

# Run type checking
npm run type-check

# Run linting
npm run lint

# Clean build artifacts
npm run clean
```

## Contributing

When adding new constants:

1. Choose the appropriate category file
2. Use descriptive names with proper prefixes
3. Add TypeScript types where applicable
4. Use `as const` for literal types
5. Document complex constants with comments
6. Update this README if adding new categories

## License

MIT