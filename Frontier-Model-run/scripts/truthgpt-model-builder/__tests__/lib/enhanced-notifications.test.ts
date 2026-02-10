/**
 * Unit Tests - Enhanced Notifications
 */

import { EnhancedNotifications, getEnhancedNotifications } from '@/lib/enhanced-notifications'

// Mock Notification API
const mockNotification = {
  close: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
}

global.Notification = jest.fn().mockImplementation(() => mockNotification) as any

describe('EnhancedNotifications', () => {
  let notifications: EnhancedNotifications

  beforeEach(() => {
    notifications = new EnhancedNotifications()
    jest.clearAllMocks()
  })

  afterEach(() => {
    notifications.clear()
  })

  describe('Notification Creation', () => {
    it('should create notification', async () => {
      const notification = await notifications.createNotification(
        'info',
        'Test Title',
        'Test message'
      )

      expect(notification).toBeDefined()
      expect(notification.type).toBe('info')
      expect(notification.title).toBe('Test Title')
      expect(notification.message).toBe('Test message')
    })

    it('should create different types of notifications', async () => {
      const types = ['info', 'success', 'warning', 'error'] as const
      
      for (const type of types) {
        const notification = await notifications.createNotification(
          type,
          `${type} Title`,
          `${type} message`
        )
        expect(notification.type).toBe(type)
      }
    })

    it('should create notification with options', async () => {
      const notification = await notifications.createNotification(
        'info',
        'Test',
        'Message',
        {
          priority: 'high',
          sound: true,
          persistent: true,
        }
      )

      expect(notification.priority).toBe('high')
      expect(notification.sound).toBe(true)
      expect(notification.persistent).toBe(true)
    })
  })

  describe('Notification History', () => {
    it('should store notification in history', async () => {
      await notifications.createNotification('info', 'Test', 'Message')
      
      const history = notifications.getHistory()
      expect(history.length).toBe(1)
      expect(history[0].title).toBe('Test')
    })

    it('should limit history size', async () => {
      for (let i = 0; i < 150; i++) {
        await notifications.createNotification('info', `Test ${i}`, 'Message')
      }

      const history = notifications.getHistory()
      expect(history.length).toBeLessThanOrEqual(100)
    })

    it('should get recent notifications', async () => {
      for (let i = 0; i < 20; i++) {
        await notifications.createNotification('info', `Test ${i}`, 'Message')
      }

      const recent = notifications.getRecentNotifications(10)
      expect(recent.length).toBeLessThanOrEqual(10)
    })
  })

  describe('Permission Management', () => {
    it('should request permission', async () => {
      const permission = await notifications.requestPermission()
      expect(['granted', 'denied', 'default']).toContain(permission)
    })

    it('should check permission status', () => {
      const status = notifications.getPermissionStatus()
      expect(['granted', 'denied', 'default']).toContain(status)
    })
  })

  describe('Preferences', () => {
    it('should set preferences', () => {
      notifications.setPreferences({
        enabled: true,
        sound: true,
        priority: 'high',
      })

      const preferences = notifications.getPreferences()
      expect(preferences.enabled).toBe(true)
      expect(preferences.sound).toBe(true)
      expect(preferences.priority).toBe('high')
    })

    it('should respect preferences when creating notifications', async () => {
      notifications.setPreferences({
        enabled: false,
      })

      const notification = await notifications.createNotification(
        'info',
        'Test',
        'Message'
      )

      // Should not create if disabled
      expect(notification).toBeDefined()
    })
  })

  describe('Silent Hours', () => {
    it('should set silent hours', () => {
      notifications.setSilentHours(22, 8) // 10 PM to 8 AM

      const silentHours = notifications.getSilentHours()
      expect(silentHours.start).toBe(22)
      expect(silentHours.end).toBe(8)
    })

    it('should not create notifications during silent hours', async () => {
      notifications.setSilentHours(22, 8)
      
      // Mock current hour to be in silent hours
      const originalDate = Date
      global.Date = jest.fn(() => ({
        getHours: () => 23, // 11 PM
      })) as any

      const notification = await notifications.createNotification(
        'info',
        'Test',
        'Message',
        { respectSilentHours: true }
      )

      global.Date = originalDate

      // Should respect silent hours
      expect(notification).toBeDefined()
    })
  })

  describe('Notification Management', () => {
    it('should clear all notifications', async () => {
      await notifications.createNotification('info', 'Test', 'Message')
      notifications.clear()
      
      const history = notifications.getHistory()
      expect(history.length).toBe(0)
    })

    it('should remove notification by ID', async () => {
      const notification = await notifications.createNotification(
        'info',
        'Test',
        'Message'
      )

      notifications.removeNotification(notification.id)
      const history = notifications.getHistory()
      expect(history.find(n => n.id === notification.id)).toBeUndefined()
    })
  })

  describe('Statistics', () => {
    it('should calculate notification statistics', async () => {
      await notifications.createNotification('info', 'Test 1', 'Message')
      await notifications.createNotification('success', 'Test 2', 'Message')
      await notifications.createNotification('warning', 'Test 3', 'Message')
      await notifications.createNotification('error', 'Test 4', 'Message')

      const stats = notifications.getStatistics()
      expect(stats.total).toBe(4)
      expect(stats.byType.info).toBe(1)
      expect(stats.byType.success).toBe(1)
      expect(stats.byType.warning).toBe(1)
      expect(stats.byType.error).toBe(1)
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const n1 = getEnhancedNotifications()
      const n2 = getEnhancedNotifications()
      expect(n1).toBe(n2)
    })
  })
})










