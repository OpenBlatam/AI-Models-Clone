import { ComponentType, lazy, LazyExoticComponent } from 'react';

/**
 * Helper function for lazy loading components with better TypeScript support
 */
export function lazyLoad<T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>
): LazyExoticComponent<T> {
  return lazy(importFunc);
}

/**
 * Preload a lazy component
 */
export async function preloadLazyComponent<T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>
): Promise<void> {
  await importFunc();
}


