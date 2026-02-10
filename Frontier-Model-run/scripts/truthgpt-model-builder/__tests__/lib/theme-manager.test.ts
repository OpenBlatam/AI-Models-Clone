/**
 * Unit Tests - Theme Manager
 */

import { ThemeManager, getThemeManager } from '@/lib/theme-manager'

describe('ThemeManager', () => {
  let themeManager: ThemeManager

  beforeEach(() => {
    themeManager = new ThemeManager()
    if (typeof window !== 'undefined') {
      localStorage.clear()
    }
  })

  afterEach(() => {
    themeManager.clear()
  })

  describe('Theme Management', () => {
    it('should set theme', () => {
      themeManager.setTheme('dark')
      expect(themeManager.getTheme()).toBe('dark')
    })

    it('should get current theme', () => {
      themeManager.setTheme('light')
      expect(themeManager.getTheme()).toBe('light')
    })

    it('should toggle theme', () => {
      themeManager.setTheme('dark')
      themeManager.toggleTheme()
      expect(themeManager.getTheme()).toBe('light')

      themeManager.toggleTheme()
      expect(themeManager.getTheme()).toBe('dark')
    })

    it('should support auto theme', () => {
      themeManager.setTheme('auto')
      expect(themeManager.getTheme()).toBe('auto')
    })
  })

  describe('System Preference Detection', () => {
    it('should detect system preference', () => {
      // Mock matchMedia
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => ({
          matches: query.includes('dark'),
          media: query,
          onchange: null,
          addListener: jest.fn(),
          removeListener: jest.fn(),
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          dispatchEvent: jest.fn(),
        })),
      })

      const systemPreference = themeManager.getSystemPreference()
      expect(['light', 'dark']).toContain(systemPreference)
    })

    it('should apply system theme when auto', () => {
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => ({
          matches: query.includes('dark'),
          media: query,
          onchange: null,
          addListener: jest.fn(),
          removeListener: jest.fn(),
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          dispatchEvent: jest.fn(),
        })),
      })

      themeManager.setTheme('auto')
      const appliedTheme = themeManager.getAppliedTheme()
      expect(['light', 'dark']).toContain(appliedTheme)
    })
  })

  describe('Persistence', () => {
    it('should persist theme to localStorage', () => {
      themeManager.setTheme('dark')
      
      // Create new instance (should load from localStorage)
      const newThemeManager = new ThemeManager()
      expect(newThemeManager.getTheme()).toBe('dark')
    })

    it('should load theme from localStorage on init', () => {
      if (typeof window !== 'undefined') {
        localStorage.setItem('theme', 'light')
      }

      const newThemeManager = new ThemeManager()
      expect(newThemeManager.getTheme()).toBe('light')
    })
  })

  describe('Theme Change Listeners', () => {
    it('should notify listeners on theme change', () => {
      const listener = jest.fn()
      themeManager.onThemeChange(listener)

      themeManager.setTheme('dark')
      expect(listener).toHaveBeenCalledWith('dark')
    })

    it('should remove listener', () => {
      const listener = jest.fn()
      const removeListener = themeManager.onThemeChange(listener)

      themeManager.setTheme('dark')
      expect(listener).toHaveBeenCalledTimes(1)

      removeListener()
      themeManager.setTheme('light')
      expect(listener).toHaveBeenCalledTimes(1) // Not called again
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const t1 = getThemeManager()
      const t2 = getThemeManager()
      expect(t1).toBe(t2)
    })
  })
})










