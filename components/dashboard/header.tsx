"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useNotifications } from "@/hooks/use-notifications";
import { Notifications } from "./notifications";

export function DashboardHeader() {
  const pathname = usePathname();
  const { notifications, markAsRead } = useNotifications();

  const navigation = [
    { name: "Dashboard", href: "/dashboard" },
    { name: "Lecciones", href: "/dashboard/lessons" },
    { name: "Ejercicios", href: "/dashboard/exercises" },
    { name: "Logros", href: "/dashboard/achievements" },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <span className="font-bold">AI Learning</span>
          </Link>
          <nav className="flex items-center space-x-6 text-sm font-medium">
            {navigation.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "transition-colors hover:text-foreground/80",
                  pathname === item.href
                    ? "text-foreground"
                    : "text-foreground/60"
                )}
              >
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
        <div className="flex flex-1 items-center justify-end space-x-4">
          <Notifications
            notifications={notifications}
            onMarkAsRead={markAsRead}
          />
        </div>
      </div>
    </header>
  );
}
