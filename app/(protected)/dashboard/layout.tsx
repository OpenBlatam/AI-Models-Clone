import { DashboardNav } from "@/components/dashboard/dashboard-nav";
import MobileBottomNavWrapper from "@/components/MobileBottomNavWrapper";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col space-y-6">
      <header className="sticky top-0 z-40 border-b bg-background">
        <div className="container flex h-16 items-center justify-between py-4">
          <DashboardNav />
        </div>
      </header>
      <div className="container flex-1">
        {children}
      </div>
      <MobileBottomNavWrapper />
    </div>
  );
} 