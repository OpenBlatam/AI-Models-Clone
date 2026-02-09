"use client";

import { type FC } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { NAV_ITEMS } from "@/constants";
import { HealthIndicator } from "./HealthIndicator";

export const Header: FC = () => {
    const pathname = usePathname();

    return (
        <motion.header
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="sticky top-0 z-50 w-full backdrop-blur-xl bg-slate-900/80 border-b border-slate-800"
        >
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link
                        href="/"
                        className="flex items-center gap-3 group"
                        aria-label="Prompt Compiler Home"
                    >
                        <motion.div
                            whileHover={{ scale: 1.05, rotate: 5 }}
                            whileTap={{ scale: 0.95 }}
                            className="relative w-10 h-10 flex items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 shadow-lg shadow-violet-500/30 group-hover:shadow-violet-500/50 transition-shadow"
                        >
                            <span className="text-xl">🚀</span>
                        </motion.div>
                        <div>
                            <h1 className="text-lg font-bold bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">
                                Prompt Compiler
                            </h1>
                            <p className="text-xs text-slate-500">AI SAM3</p>
                        </div>
                    </Link>

                    {/* Navigation */}
                    <nav className="flex items-center gap-1" aria-label="Main navigation">
                        {NAV_ITEMS.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={`
                    relative flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all
                    ${isActive
                                            ? "text-violet-300"
                                            : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                                        }
                  `}
                                    aria-current={isActive ? "page" : undefined}
                                >
                                    <span aria-hidden="true">{item.icon}</span>
                                    <span className="hidden sm:inline">{item.label}</span>

                                    {/* Active indicator */}
                                    {isActive && (
                                        <motion.div
                                            layoutId="activeNav"
                                            className="absolute inset-0 rounded-lg bg-violet-500/20 border border-violet-500/30 -z-10"
                                            transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                        />
                                    )}
                                </Link>
                            );
                        })}
                    </nav>

                    {/* Health Indicator */}
                    <HealthIndicator />
                </div>
            </div>
        </motion.header>
    );
};

export default Header;
