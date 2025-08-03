// UI-related constants

// Theme colors
export const THEME_COLORS = {
  PRIMARY: '#2563eb',
  SECONDARY: '#64748b',
  SUCCESS: '#16a34a',
  WARNING: '#d97706',
  ERROR: '#dc2626',
  INFO: '#0ea5e9',
  
  // Background colors
  BACKGROUND: {
    PRIMARY: '#ffffff',
    SECONDARY: '#f8fafc',
    TERTIARY: '#f1f5f9'
  },
  
  // Text colors
  TEXT: {
    PRIMARY: '#0f172a',
    SECONDARY: '#475569',
    MUTED: '#94a3b8',
    INVERSE: '#ffffff'
  },
  
  // Border colors
  BORDER: {
    DEFAULT: '#e2e8f0',
    MUTED: '#f1f5f9',
    STRONG: '#cbd5e1'
  }
} as const;

// Dark theme colors
export const DARK_THEME_COLORS = {
  PRIMARY: '#3b82f6',
  SECONDARY: '#64748b',
  SUCCESS: '#22c55e',
  WARNING: '#f59e0b',
  ERROR: '#ef4444',
  INFO: '#06b6d4',
  
  // Background colors
  BACKGROUND: {
    PRIMARY: '#0f172a',
    SECONDARY: '#1e293b',
    TERTIARY: '#334155'
  },
  
  // Text colors
  TEXT: {
    PRIMARY: '#f8fafc',
    SECONDARY: '#cbd5e1',
    MUTED: '#94a3b8',
    INVERSE: '#0f172a'
  },
  
  // Border colors
  BORDER: {
    DEFAULT: '#334155',
    MUTED: '#1e293b',
    STRONG: '#475569'
  }
} as const;

// Status colors
export const STATUS_COLORS = {
  ONLINE: '#22c55e',
  OFFLINE: '#ef4444',
  CONNECTING: '#f59e0b',
  IDLE: '#64748b',
  BUSY: '#f97316',
  ERROR: '#dc2626',
  UNKNOWN: '#6b7280'
} as const;

// Component sizes
export const COMPONENT_SIZES = {
  AVATAR: {
    SM: '32px',
    MD: '40px',
    LG: '48px',
    XL: '64px'
  },
  
  BUTTON: {
    SM: {
      height: '32px',
      padding: '8px 12px',
      fontSize: '14px'
    },
    MD: {
      height: '40px',
      padding: '10px 16px',
      fontSize: '16px'
    },
    LG: {
      height: '48px',
      padding: '12px 20px',
      fontSize: '18px'
    }
  },
  
  INPUT: {
    SM: {
      height: '32px',
      padding: '8px 12px',
      fontSize: '14px'
    },
    MD: {
      height: '40px',
      padding: '10px 12px',
      fontSize: '16px'
    },
    LG: {
      height: '48px',
      padding: '12px 16px',
      fontSize: '18px'
    }
  }
} as const;

// Spacing scale
export const SPACING = {
  XS: '4px',
  SM: '8px',
  MD: '16px',
  LG: '24px',
  XL: '32px',
  XXL: '48px',
  XXXL: '64px'
} as const;

// Border radius
export const BORDER_RADIUS = {
  NONE: '0',
  SM: '4px',
  MD: '8px',
  LG: '12px',
  XL: '16px',
  FULL: '9999px'
} as const;

// Font weights
export const FONT_WEIGHTS = {
  LIGHT: 300,
  NORMAL: 400,
  MEDIUM: 500,
  SEMIBOLD: 600,
  BOLD: 700
} as const;

// Font sizes
export const FONT_SIZES = {
  XS: '12px',
  SM: '14px',
  MD: '16px',
  LG: '18px',
  XL: '20px',
  XXL: '24px',
  XXXL: '32px'
} as const;

// Z-index layers
export const Z_INDEX = {
  DROPDOWN: 1000,
  STICKY: 1020,
  FIXED: 1030,
  MODAL_BACKDROP: 1040,
  MODAL: 1050,
  POPOVER: 1060,
  TOOLTIP: 1070,
  TOAST: 1080
} as const;

// Animation durations
export const ANIMATIONS = {
  FAST: '150ms',
  NORMAL: '300ms',
  SLOW: '500ms',
  
  // Easing functions
  EASE_IN: 'cubic-bezier(0.4, 0, 1, 1)',
  EASE_OUT: 'cubic-bezier(0, 0, 0.2, 1)',
  EASE_IN_OUT: 'cubic-bezier(0.4, 0, 0.2, 1)'
} as const;

// Breakpoints for responsive design
export const BREAKPOINTS = {
  SM: '640px',
  MD: '768px',
  LG: '1024px',
  XL: '1280px',
  XXL: '1536px'
} as const;

// Icon sizes
export const ICON_SIZES = {
  XS: '12px',
  SM: '16px',
  MD: '20px',
  LG: '24px',
  XL: '32px',
  XXL: '48px'
} as const;

// Table constants
export const TABLE_CONSTANTS = {
  ROW_HEIGHT: {
    COMPACT: '32px',
    NORMAL: '48px',
    COMFORTABLE: '56px'
  },
  
  HEADER_HEIGHT: '48px',
  
  CELL_PADDING: {
    COMPACT: '8px',
    NORMAL: '12px',
    COMFORTABLE: '16px'
  }
} as const;

// Loading states
export const LOADING_STATES = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error'
} as const;

// Notification types
export const NOTIFICATION_TYPES = {
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error'
} as const;

// Navigation constants
export const NAVIGATION = {
  SIDEBAR_WIDTH: '280px',
  SIDEBAR_COLLAPSED_WIDTH: '64px',
  HEADER_HEIGHT: '64px',
  FOOTER_HEIGHT: '48px'
} as const;

// Form validation states
export const FORM_STATES = {
  DEFAULT: 'default',
  VALID: 'valid',
  INVALID: 'invalid',
  PENDING: 'pending'
} as const;

// Modal sizes
export const MODAL_SIZES = {
  SM: '400px',
  MD: '600px',
  LG: '800px',
  XL: '1200px',
  FULL: '100vw'
} as const;

// Dashboard grid
export const DASHBOARD_GRID = {
  COLUMNS: 12,
  GUTTER: '16px',
  CARD_MIN_HEIGHT: '200px',
  WIDGET_ASPECT_RATIOS: {
    SQUARE: '1:1',
    LANDSCAPE: '16:9',
    PORTRAIT: '9:16'
  }
} as const;

// Chart colors
export const CHART_COLORS = [
  '#3b82f6', // Blue
  '#ef4444', // Red
  '#22c55e', // Green
  '#f59e0b', // Yellow
  '#8b5cf6', // Purple
  '#06b6d4', // Cyan
  '#f97316', // Orange
  '#ec4899', // Pink
  '#84cc16', // Lime
  '#6366f1'  // Indigo
] as const;

// Command execution status colors
export const COMMAND_STATUS_COLORS = {
  pending: '#f59e0b',     // Yellow
  running: '#3b82f6',     // Blue
  completed: '#22c55e',   // Green
  failed: '#ef4444',      // Red
  timeout: '#f97316',     // Orange
  cancelled: '#6b7280'    // Gray
} as const;

// Agent status colors
export const AGENT_STATUS_COLORS = {
  online: '#22c55e',      // Green
  offline: '#ef4444',     // Red
  connecting: '#f59e0b',  // Yellow
  idle: '#64748b',        // Slate
  busy: '#f97316',        // Orange
  error: '#dc2626',       // Red
  unknown: '#6b7280'      // Gray
} as const;

// Priority colors
export const PRIORITY_COLORS = {
  low: '#64748b',         // Slate
  medium: '#f59e0b',      // Yellow
  high: '#f97316',        // Orange
  critical: '#ef4444'     // Red
} as const;