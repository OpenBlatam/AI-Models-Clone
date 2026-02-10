/**
 * Unit Tests - Enhanced Keyboard Shortcuts
 */

import { EnhancedKeyboardShortcuts, getEnhancedKeyboardShortcuts } from '@/lib/enhanced-keyboard-shortcuts'

describe('EnhancedKeyboardShortcuts', () => {
  let shortcuts: EnhancedKeyboardShortcuts

  beforeEach(() => {
    shortcuts = new EnhancedKeyboardShortcuts()
  })

  afterEach(() => {
    shortcuts.clear()
    shortcuts.destroy()
  })

  describe('Shortcut Registration', () => {
    it('should register shortcut', () => {
      const action = jest.fn()
      shortcuts.registerShortcut({
        id: 'test-shortcut',
        keys: ['Ctrl', 'K'],
        description: 'Test shortcut',
        action,
      })

      const shortcut = shortcuts.getShortcut('test-shortcut')
      expect(shortcut).toBeDefined()
      expect(shortcut?.keys).toEqual(['Ctrl', 'K'])
    })

    it('should unregister shortcut', () => {
      shortcuts.registerShortcut({
        id: 'test-shortcut',
        keys: ['Ctrl', 'K'],
        description: 'Test',
        action: () => {},
      })

      shortcuts.unregisterShortcut('test-shortcut')
      const shortcut = shortcuts.getShortcut('test-shortcut')
      expect(shortcut).toBeUndefined()
    })

    it('should enable/disable shortcut', () => {
      shortcuts.registerShortcut({
        id: 'test-shortcut',
        keys: ['Ctrl', 'K'],
        description: 'Test',
        action: () => {},
      })

      shortcuts.setShortcutEnabled('test-shortcut', false)
      const shortcut = shortcuts.getShortcut('test-shortcut')
      expect(shortcut?.enabled).toBe(false)
    })
  })

  describe('Key Formatting', () => {
    it('should format keys correctly', () => {
      const formatted = shortcuts.formatKeys(['Ctrl', 'K'])
      expect(formatted).toBe('Ctrl + K')
    })

    it('should format space key', () => {
      const formatted = shortcuts.formatKeys(['Ctrl', ' '])
      expect(formatted).toContain('Space')
    })

    it('should uppercase letter keys', () => {
      const formatted = shortcuts.formatKeys(['Ctrl', 'a'])
      expect(formatted).toContain('A')
    })
  })

  describe('Search', () => {
    it('should search shortcuts by description', () => {
      shortcuts.registerShortcut({
        id: 'shortcut1',
        keys: ['Ctrl', 'K'],
        description: 'Open command palette',
        action: () => {},
      })

      shortcuts.registerShortcut({
        id: 'shortcut2',
        keys: ['Ctrl', 'S'],
        description: 'Save file',
        action: () => {},
      })

      const results = shortcuts.searchShortcuts('command')
      expect(results.length).toBeGreaterThan(0)
      expect(results[0].description).toContain('command')
    })

    it('should search shortcuts by keys', () => {
      shortcuts.registerShortcut({
        id: 'shortcut1',
        keys: ['Ctrl', 'K'],
        description: 'Test',
        action: () => {},
      })

      const results = shortcuts.searchShortcuts('Ctrl')
      expect(results.length).toBeGreaterThan(0)
    })
  })

  describe('Categories', () => {
    it('should get shortcuts by category', () => {
      shortcuts.registerShortcut({
        id: 'shortcut1',
        keys: ['Ctrl', 'K'],
        description: 'Test',
        category: 'navigation',
        action: () => {},
      })

      const navShortcuts = shortcuts.getShortcutsByCategory('navigation')
      expect(navShortcuts).toHaveLength(1)
    })

    it('should get all categories', () => {
      shortcuts.registerShortcut({
        id: 'shortcut1',
        keys: ['Ctrl', 'K'],
        description: 'Test',
        category: 'navigation',
        action: () => {},
      })

      const categories = shortcuts.getCategories()
      expect(categories).toContain('navigation')
    })
  })

  describe('Enable/Disable', () => {
    it('should enable/disable all shortcuts', () => {
      shortcuts.setEnabled(false)
      // Should not execute when disabled
      
      shortcuts.setEnabled(true)
      // Should execute when enabled
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const s1 = getEnhancedKeyboardShortcuts()
      const s2 = getEnhancedKeyboardShortcuts()
      expect(s1).toBe(s2)
    })
  })
})










