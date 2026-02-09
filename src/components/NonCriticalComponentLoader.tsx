import React, { Suspense } from 'react';

const NonCriticalComponent = React.lazy(() => import('./NonCriticalComponent'));

export function NonCriticalComponentLoader(): JSX.Element {
  return (
    <Suspense fallback={null}>
      <NonCriticalComponent />
    </Suspense>
  );
} 