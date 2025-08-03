# @dexagent/shared-components

Shared React components for the DexAgent monorepo.

## Status: Placeholder

This package is currently a placeholder for future React component sharing between frontend applications in the DexAgent monorepo.

## Future Plans

When this package is developed, it will contain:

### UI Components
- **Button** - Standardized button component with variants
- **Card** - Container component for content sections
- **Modal** - Dialog and modal components
- **Table** - Data table with sorting and pagination
- **Form** - Form components with validation
- **Input** - Various input field components
- **Loading** - Loading spinners and skeletons

### Layout Components
- **Header** - Application header
- **Sidebar** - Navigation sidebar
- **Layout** - Page layout wrapper
- **Grid** - Responsive grid system

### Domain-Specific Components
- **AgentCard** - Display agent information
- **CommandOutput** - Display command execution results
- **StatusBadge** - Show status with appropriate styling
- **MetricsChart** - Display system metrics
- **LogViewer** - Log file viewer component

### Utility Components
- **ErrorBoundary** - Error handling wrapper
- **ProtectedRoute** - Authentication wrapper
- **ThemeProvider** - Theme context provider

## Installation

```bash
npm install @dexagent/shared-components
```

## Usage (Future)

```tsx
import { Button, Card, AgentCard } from '@dexagent/shared-components';

function MyComponent() {
  return (
    <Card>
      <AgentCard agent={agent} />
      <Button variant="primary" onClick={handleClick}>
        Execute Command
      </Button>
    </Card>
  );
}
```

## Development Setup (Future)

### Storybook
Components will be documented and developed using Storybook:

```bash
npm run storybook
```

### Testing
Components will be tested with Jest and React Testing Library:

```bash
npm test
npm run test:watch
```

## Design System

The shared components will follow these principles:

### Theme
- Consistent color palette
- Typography scale
- Spacing system
- Responsive breakpoints

### Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- Focus management

### Performance
- Lazy loading for heavy components
- Bundle size optimization
- Tree shaking support

## Technology Stack

- **React** 18+ with TypeScript
- **Styled Components** or **Emotion** for styling
- **Storybook** for component documentation
- **Jest** + **React Testing Library** for testing
- **ESLint** + **Prettier** for code quality

## Contributing

When this package becomes active:

1. Follow the established design system
2. Include Storybook stories for all components
3. Write comprehensive tests
4. Document props and usage examples
5. Consider accessibility in all components
6. Follow semantic versioning for breaking changes

## Dependencies

This package will depend on:
- `@dexagent/shared-types` - Type definitions
- `@dexagent/shared-utils` - Utility functions
- `react` and `react-dom` (peer dependencies)

## License

MIT