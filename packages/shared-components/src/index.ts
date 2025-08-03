// DexAgent Shared Components
// Placeholder for future React component sharing

// Note: This package is currently a placeholder for future component sharing
// between frontend applications in the DexAgent monorepo.

// When components are added, they should be exported here:
// export { Button } from './Button';
// export { Card } from './Card';
// export { Modal } from './Modal';
// export type { ButtonProps, CardProps, ModalProps } from './types';

// For now, we export a simple placeholder
export const SHARED_COMPONENTS_VERSION = '3.3.0';

export interface SharedComponentsInfo {
  version: string;
  description: string;
  status: 'placeholder' | 'active';
}

export const getSharedComponentsInfo = (): SharedComponentsInfo => ({
  version: SHARED_COMPONENTS_VERSION,
  description: 'Shared React components for DexAgent monorepo',
  status: 'placeholder'
});