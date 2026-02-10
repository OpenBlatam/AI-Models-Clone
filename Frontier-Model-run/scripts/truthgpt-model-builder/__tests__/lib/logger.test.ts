/**
 * Unit Tests - Logger
 */

import { Logger, getLogger } from '@/lib/logger'

describe('Logger', () => {
  let logger: Logger
  let consoleSpy: jest.SpyInstance

  beforeEach(() => {
    logger = new Logger()
    consoleSpy = jest.spyOn(console, 'log').mockImplementation()
  })

  afterEach(() => {
    consoleSpy.mockRestore()
    logger.clear()
  })

  describe('Logging Levels', () => {
    it('should log info messages', () => {
      logger.info('Test info message')
      const logs = logger.getLogs()
      expect(logs.length).toBe(1)
      expect(logs[0].level).toBe('info')
      expect(logs[0].message).toBe('Test info message')
    })

    it('should log warning messages', () => {
      logger.warn('Test warning message')
      const logs = logger.getLogs()
      expect(logs[0].level).toBe('warn')
    })

    it('should log error messages', () => {
      logger.error('Test error message')
      const logs = logger.getLogs()
      expect(logs[0].level).toBe('error')
    })

    it('should log debug messages', () => {
      logger.debug('Test debug message')
      const logs = logger.getLogs()
      expect(logs[0].level).toBe('debug')
    })
  })

  describe('Log Context', () => {
    it('should include context in logs', () => {
      logger.info('Test message', { userId: '123', action: 'create' })
      const logs = logger.getLogs()
      expect(logs[0].context).toEqual({ userId: '123', action: 'create' })
    })
  })

  describe('Log Filtering', () => {
    it('should filter logs by level', () => {
      logger.info('Info message')
      logger.warn('Warning message')
      logger.error('Error message')

      const errors = logger.getLogs('error')
      expect(errors.length).toBe(1)
      expect(errors[0].level).toBe('error')
    })

    it('should filter logs by time range', async () => {
      const now = Date.now()
      logger.info('Message 1')
      
      await new Promise(resolve => setTimeout(resolve, 100))
      
      logger.info('Message 2')

      const recent = logger.getLogs('info', now)
      expect(recent.length).toBeGreaterThan(0)
    })
  })

  describe('Log Limits', () => {
    it('should limit log history', () => {
      for (let i = 0; i < 200; i++) {
        logger.info(`Message ${i}`)
      }

      const logs = logger.getLogs()
      expect(logs.length).toBeLessThanOrEqual(100)
    })
  })

  describe('Log Export', () => {
    it('should export logs', () => {
      logger.info('Message 1')
      logger.warn('Message 2')

      const exported = logger.exportLogs()
      const parsed = JSON.parse(exported)
      expect(parsed).toHaveLength(2)
    })

    it('should export filtered logs', () => {
      logger.info('Info message')
      logger.error('Error message')

      const exported = logger.exportLogs('error')
      const parsed = JSON.parse(exported)
      expect(parsed).toHaveLength(1)
      expect(parsed[0].level).toBe('error')
    })
  })

  describe('Log Clearing', () => {
    it('should clear all logs', () => {
      logger.info('Message 1')
      logger.warn('Message 2')
      
      logger.clear()
      const logs = logger.getLogs()
      expect(logs.length).toBe(0)
    })
  })

  describe('Log Statistics', () => {
    it('should calculate log statistics', () => {
      logger.info('Info 1')
      logger.info('Info 2')
      logger.warn('Warning 1')
      logger.error('Error 1')

      const stats = logger.getStatistics()
      expect(stats.total).toBe(4)
      expect(stats.byLevel.info).toBe(2)
      expect(stats.byLevel.warn).toBe(1)
      expect(stats.byLevel.error).toBe(1)
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const l1 = getLogger()
      const l2 = getLogger()
      expect(l1).toBe(l2)
    })
  })
})


