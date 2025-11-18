import { Suspense } from 'react';
import { DashboardContent } from '@/components/dashboard/dashboard-content';
import { LoadingSpinner } from '@/components/ui/loading-spinner';

export default function DashboardPage() {
  return (
    <div className="container py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of your application's performance and data
        </p>
      </div>

      <Suspense fallback={<LoadingSpinner size="xl" />}>
        <DashboardContent />
      </Suspense>
    </div>
  );
}





