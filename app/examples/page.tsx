import { Suspense } from 'react';
import { ExamplesContent } from '@/components/examples/examples-content';
import { LoadingSpinner } from '@/components/ui/loading-spinner';

export default function ExamplesPage() {
  return (
    <div className="container py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Advanced Examples</h1>
        <p className="text-muted-foreground">
          Explore advanced patterns and hooks in action
        </p>
      </div>

      <Suspense fallback={<LoadingSpinner size="xl" />}>
        <ExamplesContent />
      </Suspense>
    </div>
  );
}





