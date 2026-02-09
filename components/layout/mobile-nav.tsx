'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { X } from 'lucide-react';

interface NavigationItem {
  name: string;
  href: string;
}

interface MobileNavProps {
  isOpen: boolean;
  onClose: () => void;
  navigation: NavigationItem[];
  pathname: string;
}

export function MobileNav({ isOpen, onClose, navigation, pathname }: MobileNavProps) {
  // Close mobile menu on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when mobile menu is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  // Close mobile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (isOpen && !target.closest('[data-mobile-nav]')) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Mobile Navigation */}
      <div
        data-mobile-nav
        className={cn(
          'fixed inset-y-0 right-0 z-50 w-full max-w-sm bg-background border-l shadow-xl transition-transform duration-300 ease-in-out',
          isOpen ? 'translate-x-0' : 'translate-x-full'
        )}
      >
        <div className="flex h-16 items-center justify-between border-b px-6">
          <h2 className="text-lg font-semibold">Menu</h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            aria-label="Close mobile menu"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        <nav className="flex flex-col space-y-1 p-6">
          {navigation.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              onClick={onClose}
              className={cn(
                'flex items-center px-3 py-2 text-base font-medium rounded-md transition-colors',
                pathname === item.href
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent'
              )}
            >
              {item.name}
            </Link>
          ))}
        </nav>

        {/* Mobile CTA */}
        <div className="absolute bottom-6 left-6 right-6">
          <Button asChild className="w-full" size="lg">
            <Link href="/get-started" onClick={onClose}>
              Get Started
            </Link>
          </Button>
        </div>
      </div>
    </>
  );
}
