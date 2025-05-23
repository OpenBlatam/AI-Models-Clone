'use client';

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Home, BookOpen, Target, LineChart, Trophy } from "lucide-react";
import { motion } from "framer-motion";

const navItems = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: Home,
  },
  {
    title: "Lecciones",
    href: "/dashboard/lessons",
    icon: BookOpen,
  },
  {
    title: "Academy",
    href: "/dashboard/academy",
    icon: Target,
  },
  {
    title: "Ejercicios",
    href: "/dashboard/exercises",
    icon: LineChart,
  },
  {
    title: "Logros",
    href: "/dashboard/achievements",
    icon: Trophy,
  },
];

export function DashboardNav() {
  const pathname = usePathname();

  return (
    <nav className="flex items-center space-x-4 lg:space-x-6">
      {navItems.map((item) => {
        const isActive = pathname === item.href;
        const Icon = item.icon;

        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center text-sm font-medium transition-colors hover:text-primary",
              isActive ? "text-primary" : "text-muted-foreground"
            )}
          >
            <motion.div
              className="flex items-center gap-2"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Icon className="h-4 w-4" />
              <span>{item.title}</span>
            </motion.div>
          </Link>
        );
      })}
    </nav>
  );
} 