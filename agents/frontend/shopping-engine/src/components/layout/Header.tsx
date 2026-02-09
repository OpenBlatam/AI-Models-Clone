'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
    ShoppingCart,
    ScanSearch,
    DollarSign,
    Sparkles,
    FileText,
    Menu,
    X
} from 'lucide-react';
import { useState } from 'react';

interface NavItem {
    label: string;
    href: string;
    icon: React.ReactNode;
}

const navItems: NavItem[] = [
    { label: 'Analyze', href: '/analyze', icon: <ScanSearch className="w-4 h-4" /> },
    { label: 'Purchase', href: '/purchase', icon: <ShoppingCart className="w-4 h-4" /> },
    { label: 'Recommendations', href: '/recommendations', icon: <Sparkles className="w-4 h-4" /> },
    { label: 'Compare', href: '/compare', icon: <DollarSign className="w-4 h-4" /> },
    { label: 'Details', href: '/details', icon: <FileText className="w-4 h-4" /> },
];

export const Header = () => {
    const pathname = usePathname();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    const handleToggleMobileMenu = () => {
        setIsMobileMenuOpen(!isMobileMenuOpen);
    };

    const handleCloseMobileMenu = () => {
        setIsMobileMenuOpen(false);
    };

    return (
        <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-background/80 backdrop-blur-xl">
            <div className="container mx-auto px-4">
                <div className="flex h-16 items-center justify-between">
                    {/* Logo */}
                    <Link
                        href="/"
                        className="flex items-center gap-2 group"
                        tabIndex={0}
                        aria-label="Shopping Engine AI Home"
                    >
                        <motion.div
                            className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center"
                            whileHover={{ scale: 1.05, rotate: 5 }}
                            whileTap={{ scale: 0.95 }}
                        >
                            <ShoppingCart className="w-5 h-5 text-white" aria-hidden="true" />
                        </motion.div>
                        <span className="text-lg font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                            ShopAI
                        </span>
                    </Link>

                    {/* Desktop Navigation */}
                    <nav className="hidden md:flex items-center gap-1" aria-label="Main navigation">
                        {navItems.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={`
                    flex items-center gap-2 px-4 py-2 rounded-lg
                    text-sm font-medium transition-all duration-200
                    ${isActive
                                            ? 'bg-primary/20 text-primary'
                                            : 'text-text-muted hover:text-text hover:bg-card'
                                        }
                  `}
                                    tabIndex={0}
                                    aria-current={isActive ? 'page' : undefined}
                                >
                                    {item.icon}
                                    {item.label}
                                </Link>
                            );
                        })}
                    </nav>

                    {/* Mobile Menu Button */}
                    <button
                        type="button"
                        className="md:hidden p-2 rounded-lg hover:bg-card transition-colors"
                        onClick={handleToggleMobileMenu}
                        aria-expanded={isMobileMenuOpen}
                        aria-controls="mobile-menu"
                        aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
                        tabIndex={0}
                    >
                        {isMobileMenuOpen ? (
                            <X className="w-6 h-6 text-text" aria-hidden="true" />
                        ) : (
                            <Menu className="w-6 h-6 text-text" aria-hidden="true" />
                        )}
                    </button>
                </div>

                {/* Mobile Navigation */}
                <motion.nav
                    id="mobile-menu"
                    className={`md:hidden ${isMobileMenuOpen ? 'block' : 'hidden'}`}
                    initial={false}
                    animate={isMobileMenuOpen ? { height: 'auto', opacity: 1 } : { height: 0, opacity: 0 }}
                    aria-label="Mobile navigation"
                >
                    <div className="py-4 space-y-2 border-t border-white/10">
                        {navItems.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    onClick={handleCloseMobileMenu}
                                    className={`
                    flex items-center gap-3 px-4 py-3 rounded-lg
                    text-base font-medium transition-all duration-200
                    ${isActive
                                            ? 'bg-primary/20 text-primary'
                                            : 'text-text-muted hover:text-text hover:bg-card'
                                        }
                  `}
                                    tabIndex={0}
                                    aria-current={isActive ? 'page' : undefined}
                                >
                                    {item.icon}
                                    {item.label}
                                </Link>
                            );
                        })}
                    </div>
                </motion.nav>
            </div>
        </header>
    );
};

export default Header;
