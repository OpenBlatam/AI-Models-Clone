// Lazy loading utilities
export { 
  withLazyLoading, 
  preloadComponent, 
  useLazyComponent,
  LazyErrorBoundary,
  LoadingSpinner 
} from './LazyComponents';

// Dashboard lazy components
export { 
  LazyDashboardContainer,
  LazyOnScroll 
} from './LazyDashboard';

// Academy lazy components
export { 
  LazyAcademyContainer,
  LazyAcademyRoute,
  preloadAcademyComponents,
  usePriorityLazyLoading 
} from './LazyAcademy';

// Chat lazy components
export { 
  LazyChatContainer,
  LazyVirtualChat,
  ProgressiveChat,
  NetworkAwareChat 
} from './LazyChat';

// Games lazy components
export { 
  LazyGameContainer,
  LazyGameWithState,
  PerformanceAwareGame,
  InteractionTriggeredGame 
} from './LazyGames';

// Default exports for convenience
export { default as LazyComponents } from './LazyComponents';
export { default as LazyDashboard } from './LazyDashboard';
export { default as LazyAcademy } from './LazyAcademy';
export { default as LazyChat } from './LazyChat';
export { default as LazyGames } from './LazyGames'; 