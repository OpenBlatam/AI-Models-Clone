import React, { Suspense, lazy } from 'react';

const RadialTextChart = lazy(() => import('../charts/radial-text-chart'));

const LoadingSpinner = () => (
  <div className="flex items-center justify-center p-4">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
  </div>
);

export default function LazyRadialTextChart(props: any) {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <RadialTextChart {...props} />
    </Suspense>
  );
} 