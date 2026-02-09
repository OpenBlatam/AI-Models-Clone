import { ReactNode, Suspense } from 'react';
import { LoadingSpinner } from './loading-spinner';

interface SuspenseBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  message?: string;
}

export function SuspenseBoundary({
  children,
  fallback,
  message = 'Loading...',
}: SuspenseBoundaryProps) {
  if (fallback) {
    return <Suspense fallback={fallback}>{children}</Suspense>;
  }

  return (
    <Suspense fallback={<LoadingSpinner fullScreen message={message} />}>
      {children}
    </Suspense>
  );
}


