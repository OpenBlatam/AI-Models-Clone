import { DashboardNav } from "@/components/dashboard/dashboard-nav";
import MobileBottomNavWrapper from "@/components/MobileBottomNavWrapper";
import { Suspense } from "react";
import { Skeleton } from "@/components/ui/skeleton";

function DashboardNavSkeleton() {
  return (
    <div className="flex items-center space-x-4">
      <Skeleton className="h-8 w-24" />
      <Skeleton className="h-8 w-24" />
      <Skeleton className="h-8 w-24" />
    </div>
  );
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col space-y-6">
      <header className="sticky top-0 z-40 border-b bg-background">
        <div className="container flex h-16 items-center justify-between py-4">
          <Suspense fallback={<DashboardNavSkeleton />}>
            <DashboardNav />
          </Suspense>
        </div>
      </header>
      <div className="container flex-1">
        <Suspense fallback={<div className="animate-pulse">Loading...</div>}>
          {children}
        </Suspense>
      </div>
      <MobileBottomNavWrapper />
    </div>
  );
} 