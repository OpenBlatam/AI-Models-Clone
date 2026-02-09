'use client'

import { Moon, Sun } from 'lucide-react'
import { Button } from './ui/button'
import { usePreferences } from '@/hooks/use-preferences'

export function ThemeToggle() {
  const { preferences, updatePreferences } = usePreferences()
  const isDark = preferences.theme === 'dark'

  const toggleTheme = () => {
    const newTheme = isDark ? 'light' : 'dark'
    updatePreferences({ theme: newTheme })
    document.documentElement.classList.toggle('dark', newTheme === 'dark')
  }

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggleTheme}
      aria-label="Toggle theme"
    >
      {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
    </Button>
  )
}


