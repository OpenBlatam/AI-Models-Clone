'use client';

import Link from 'next/link';
import { Github, Twitter, Heart } from 'lucide-react';

export const Footer = () => {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="w-full border-t border-white/10 bg-background">
            <div className="container mx-auto px-4">
                <div className="py-8">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                        {/* Brand */}
                        <div className="flex items-center gap-2">
                            <span className="text-lg font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                                ShopAI
                            </span>
                            <span className="text-text-muted text-sm">
                                &copy; {currentYear}
                            </span>
                        </div>

                        {/* Links */}
                        <nav className="flex items-center gap-6" aria-label="Footer navigation">
                            <Link
                                href="/about"
                                className="text-sm text-text-muted hover:text-text transition-colors"
                                tabIndex={0}
                            >
                                About
                            </Link>
                            <Link
                                href="/docs"
                                className="text-sm text-text-muted hover:text-text transition-colors"
                                tabIndex={0}
                            >
                                Documentation
                            </Link>
                            <Link
                                href="/api"
                                className="text-sm text-text-muted hover:text-text transition-colors"
                                tabIndex={0}
                            >
                                API
                            </Link>
                        </nav>

                        {/* Social Links */}
                        <div className="flex items-center gap-3">
                            <a
                                href="https://github.com"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="p-2 rounded-lg hover:bg-card text-text-muted hover:text-text transition-colors"
                                aria-label="GitHub"
                                tabIndex={0}
                            >
                                <Github className="w-5 h-5" aria-hidden="true" />
                            </a>
                            <a
                                href="https://twitter.com"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="p-2 rounded-lg hover:bg-card text-text-muted hover:text-text transition-colors"
                                aria-label="Twitter"
                                tabIndex={0}
                            >
                                <Twitter className="w-5 h-5" aria-hidden="true" />
                            </a>
                        </div>
                    </div>

                    {/* Bottom text */}
                    <div className="mt-6 pt-6 border-t border-white/5 text-center">
                        <p className="text-sm text-text-muted flex items-center justify-center gap-1">
                            Built with <Heart className="w-4 h-4 text-accent-error" aria-hidden="true" /> using AI
                        </p>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
