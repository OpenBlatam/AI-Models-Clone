'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Store, MessageSquare, LayoutDashboard, Home } from 'lucide-react'
import { ThemeToggle } from './theme-toggle'
import { NotificationCenter } from './notification-center'
import { ShortcutHint } from './shortcut-hint'
import { cn } from '@/lib/utils'

const navItems = [
  { href: '/', label: 'Inicio', icon: Home },
  { href: '/chat', label: 'Chat', icon: MessageSquare },
  { href: '/design', label: 'Crear Diseño', icon: Store },
  { href: '/designs', label: 'Mis Diseños', icon: Store },
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
]

export function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="border-b bg-white">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="text-xl font-bold text-blue-600">
            Store Designer AI
          </Link>
          <div className="flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Link>
              )
            })}
            <NotificationCenter />
            <ShortcutHint />
            <ThemeToggle />
          </div>
        </div>
      </div>
    </nav>
  )
}

