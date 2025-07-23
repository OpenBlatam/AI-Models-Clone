import React, { Suspense } from 'react';

const LazyNonCriticalComponent = React.lazy(() => import('./LazyNonCriticalComponent'));
const AnotherLazyComponent = React.lazy(() => import('./AnotherLazyComponent'));

const ParentComponent: React.FC = () => {
  return (
    <>
      {/* Critical UI here */}
      <Suspense fallback={<></>}>
        <LazyNonCriticalComponent />
      </Suspense>
      <Suspense fallback={<></>}>
        <AnotherLazyComponent />
      </Suspense>
    </>
  );
};

export { ParentComponent };
export default ParentComponent; 