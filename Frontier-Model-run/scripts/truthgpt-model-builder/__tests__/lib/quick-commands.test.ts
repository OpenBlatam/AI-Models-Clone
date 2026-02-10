/**
 * Unit Tests - Quick Commands
 */

import { QuickCommands, getQuickCommands } from '@/lib/quick-commands'

describe('QuickCommands', () => {
  let commands: QuickCommands

  beforeEach(() => {
    commands = new QuickCommands()
  })

  afterEach(() => {
    commands.clear()
  })

  describe('Command Registration', () => {
    it('should register command', () => {
      const action = jest.fn()
      commands.registerCommand({
        id: 'test-command',
        name: 'Test Command',
        description: 'Test description',
        action,
      })

      const cmd = commands.getCommand('test-command')
      expect(cmd).toBeDefined()
      expect(cmd?.name).toBe('Test Command')
    })

    it('should unregister command', () => {
      commands.registerCommand({
        id: 'test-command',
        name: 'Test Command',
        description: 'Test',
        action: () => {},
      })

      commands.unregisterCommand('test-command')
      const cmd = commands.getCommand('test-command')
      expect(cmd).toBeUndefined()
    })
  })

  describe('Command Execution', () => {
    it('should execute command', async () => {
      const action = jest.fn()
      commands.registerCommand({
        id: 'test-command',
        name: 'Test Command',
        description: 'Test',
        action,
      })

      const result = await commands.executeCommand('test-command')
      
      expect(result).toBe(true)
      expect(action).toHaveBeenCalled()
    })

    it('should return false for non-existent command', async () => {
      const result = await commands.executeCommand('nonexistent')
      expect(result).toBe(false)
    })

    it('should execute command by shortcut', async () => {
      const action = jest.fn()
      commands.registerCommand({
        id: 'test-command',
        name: 'Test Command',
        description: 'Test',
        shortcut: 'Ctrl+T',
        action,
      })

      const result = await commands.executeByShortcut('Ctrl+T')
      
      expect(result).toBe(true)
      expect(action).toHaveBeenCalled()
    })

    it('should handle async actions', async () => {
      const action = jest.fn(async () => {
        await new Promise(resolve => setTimeout(resolve, 10))
      })

      commands.registerCommand({
        id: 'async-command',
        name: 'Async Command',
        description: 'Test',
        action,
      })

      const result = await commands.executeCommand('async-command')
      
      expect(result).toBe(true)
      expect(action).toHaveBeenCalled()
    })

    it('should handle errors in actions', async () => {
      const action = jest.fn(() => {
        throw new Error('Test error')
      })

      commands.registerCommand({
        id: 'error-command',
        name: 'Error Command',
        description: 'Test',
        action,
      })

      const result = await commands.executeCommand('error-command')
      
      expect(result).toBe(false)
      expect(action).toHaveBeenCalled()
    })
  })

  describe('Search', () => {
    it('should search commands by name', () => {
      commands.registerCommand({
        id: 'cmd1',
        name: 'Classification Command',
        description: 'Test',
        action: () => {},
      })

      commands.registerCommand({
        id: 'cmd2',
        name: 'Sentiment Command',
        description: 'Test',
        action: () => {},
      })

      const results = commands.searchCommands('Classification')
      expect(results.length).toBeGreaterThan(0)
      expect(results[0].name).toContain('Classification')
    })

    it('should search commands by description', () => {
      commands.registerCommand({
        id: 'cmd1',
        name: 'Test Command',
        description: 'Handles classification tasks',
        action: () => {},
      })

      const results = commands.searchCommands('classification')
      expect(results.length).toBeGreaterThan(0)
    })

    it('should search commands by tags', () => {
      commands.registerCommand({
        id: 'cmd1',
        name: 'Test Command',
        description: 'Test',
        tags: ['classification', 'nlp'],
        action: () => {},
      })

      const results = commands.searchCommands('nlp')
      expect(results.length).toBeGreaterThan(0)
    })
  })

  describe('Categories', () => {
    it('should get commands by category', () => {
      commands.registerCommand({
        id: 'cmd1',
        name: 'Command 1',
        description: 'Test',
        category: 'build',
        action: () => {},
      })

      commands.registerCommand({
        id: 'cmd2',
        name: 'Command 2',
        description: 'Test',
        category: 'view',
        action: () => {},
      })

      const buildCommands = commands.getCommandsByCategory('build')
      expect(buildCommands).toHaveLength(1)
      expect(buildCommands[0].category).toBe('build')
    })

    it('should get all categories', () => {
      commands.registerCommand({
        id: 'cmd1',
        name: 'Command 1',
        description: 'Test',
        category: 'build',
        action: () => {},
      })

      commands.registerCommand({
        id: 'cmd2',
        name: 'Command 2',
        description: 'Test',
        category: 'view',
        action: () => {},
      })

      const categories = commands.getCategories()
      expect(categories).toContain('build')
      expect(categories).toContain('view')
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const c1 = getQuickCommands()
      const c2 = getQuickCommands()
      expect(c1).toBe(c2)
    })
  })
})










