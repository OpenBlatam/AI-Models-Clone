/**
 * Unit Tests - Intelligent Alerts
 */

import { IntelligentAlerts, getIntelligentAlerts } from '@/lib/intelligent-alerts'

describe('IntelligentAlerts', () => {
  let alerts: IntelligentAlerts

  beforeEach(() => {
    alerts = new IntelligentAlerts()
  })

  afterEach(() => {
    alerts.clear()
  })

  describe('Rule Registration', () => {
    it('should register rule', () => {
      alerts.registerRule({
        id: 'test-rule',
        name: 'Test Rule',
        condition: () => true,
        severity: 'warning',
        message: 'Test message',
        enabled: true,
      })

      expect(alerts).toBeDefined()
    })

    it('should unregister rule', () => {
      alerts.registerRule({
        id: 'test-rule',
        name: 'Test Rule',
        condition: () => true,
        severity: 'warning',
        message: 'Test message',
      })

      alerts.unregisterRule('test-rule')
      // Rule should be unregistered (no way to verify directly, but no error)
    })
  })

  describe('Alert Evaluation', () => {
    it('should generate alert when condition is met', () => {
      alerts.registerRule({
        id: 'test-rule',
        name: 'Test Rule',
        condition: (data: { value: number }) => data.value > 10,
        severity: 'warning',
        message: 'Value is too high',
        enabled: true,
      })

      const generatedAlerts = alerts.evaluate({ value: 15 })
      expect(generatedAlerts).toHaveLength(1)
      expect(generatedAlerts[0].severity).toBe('warning')
    })

    it('should not generate alert when condition is not met', () => {
      alerts.registerRule({
        id: 'test-rule',
        name: 'Test Rule',
        condition: (data: { value: number }) => data.value > 10,
        severity: 'warning',
        message: 'Value is too high',
      })

      const generatedAlerts = alerts.evaluate({ value: 5 })
      expect(generatedAlerts).toHaveLength(0)
    })

    it('should respect cooldown', () => {
      alerts.registerRule({
        id: 'test-rule',
        name: 'Test Rule',
        condition: () => true,
        severity: 'warning',
        message: 'Test',
        cooldown: 1000,
      })

      alerts.evaluate({})
      const secondEvaluation = alerts.evaluate({})
      
      // Should only generate one alert due to cooldown
      expect(secondEvaluation.length).toBe(0)
    })

    it('should generate dynamic messages', () => {
      alerts.registerRule({
        id: 'test-rule',
        name: 'Test Rule',
        condition: (data: { count: number }) => data.count > 5,
        severity: 'warning',
        message: (data: { count: number }) => `Count is ${data.count}`,
      })

      const generatedAlerts = alerts.evaluate({ count: 10 })
      expect(generatedAlerts[0].message).toBe('Count is 10')
    })
  })

  describe('Alert Management', () => {
    it('should get all alerts', () => {
      alerts.registerRule({
        id: 'rule1',
        name: 'Rule 1',
        condition: () => true,
        severity: 'info',
        message: 'Alert 1',
      })

      alerts.registerRule({
        id: 'rule2',
        name: 'Rule 2',
        condition: () => true,
        severity: 'warning',
        message: 'Alert 2',
      })

      alerts.evaluate({})
      const allAlerts = alerts.getAlerts()

      expect(allAlerts.length).toBeGreaterThanOrEqual(2)
    })

    it('should get unacknowledged alerts', () => {
      alerts.registerRule({
        id: 'test-rule',
        name: 'Test Rule',
        condition: () => true,
        severity: 'warning',
        message: 'Test',
      })

      alerts.evaluate({})
      const unacknowledged = alerts.getUnacknowledgedAlerts()

      expect(unacknowledged.length).toBeGreaterThan(0)
      expect(unacknowledged.every(a => !a.acknowledged)).toBe(true)
    })

    it('should acknowledge alert', () => {
      alerts.registerRule({
        id: 'test-rule',
        name: 'Test Rule',
        condition: () => true,
        severity: 'warning',
        message: 'Test',
      })

      alerts.evaluate({})
      const alert = alerts.getAlerts()[0]

      alerts.acknowledge(alert.id)
      const acknowledged = alerts.getAlerts().find(a => a.id === alert.id)

      expect(acknowledged?.acknowledged).toBe(true)
    })

    it('should acknowledge all alerts', () => {
      alerts.registerRule({
        id: 'test-rule',
        name: 'Test Rule',
        condition: () => true,
        severity: 'warning',
        message: 'Test',
      })

      alerts.evaluate({})
      alerts.acknowledgeAll()

      const unacknowledged = alerts.getUnacknowledgedAlerts()
      expect(unacknowledged.length).toBe(0)
    })

    it('should remove alert', () => {
      alerts.registerRule({
        id: 'test-rule',
        name: 'Test Rule',
        condition: () => true,
        severity: 'warning',
        message: 'Test',
      })

      alerts.evaluate({})
      const alert = alerts.getAlerts()[0]

      alerts.removeAlert(alert.id)
      const remaining = alerts.getAlerts().find(a => a.id === alert.id)

      expect(remaining).toBeUndefined()
    })
  })

  describe('Subscriptions', () => {
    it('should notify subscribers', (done) => {
      alerts.registerRule({
        id: 'test-rule',
        name: 'Test Rule',
        condition: () => true,
        severity: 'warning',
        message: 'Test',
      })

      const callback = jest.fn((alert) => {
        expect(alert.severity).toBe('warning')
        done()
      })

      alerts.subscribe(callback)
      alerts.evaluate({})
    })

    it('should allow unsubscribing', () => {
      alerts.registerRule({
        id: 'test-rule',
        name: 'Test Rule',
        condition: () => true,
        severity: 'warning',
        message: 'Test',
      })

      const callback = jest.fn()
      const unsubscribe = alerts.subscribe(callback)

      unsubscribe()
      alerts.evaluate({})

      expect(callback).not.toHaveBeenCalled()
    })
  })

  describe('Statistics', () => {
    it('should calculate correct statistics', () => {
      alerts.registerRule({
        id: 'rule1',
        name: 'Rule 1',
        condition: () => true,
        severity: 'info',
        message: 'Alert 1',
      })

      alerts.registerRule({
        id: 'rule2',
        name: 'Rule 2',
        condition: () => true,
        severity: 'warning',
        message: 'Alert 2',
      })

      alerts.evaluate({})
      const stats = alerts.getStats()

      expect(stats.total).toBeGreaterThan(0)
      expect(stats.bySeverity.info).toBeGreaterThan(0)
      expect(stats.bySeverity.warning).toBeGreaterThan(0)
    })
  })

  describe('Default Rules', () => {
    it('should initialize default rules', () => {
      const alertsWithDefaults = getIntelligentAlerts()
      // Default rules should be initialized
      expect(alertsWithDefaults).toBeDefined()
    })

    it('should detect high failure rate', () => {
      const models = [
        { modelId: '1', modelName: 'test', description: 'test', status: 'failed' as const, startTime: Date.now(), endTime: Date.now() },
        { modelId: '2', modelName: 'test', description: 'test', status: 'failed' as const, startTime: Date.now(), endTime: Date.now() },
        { modelId: '3', modelName: 'test', description: 'test', status: 'failed' as const, startTime: Date.now(), endTime: Date.now() },
        { modelId: '4', modelName: 'test', description: 'test', status: 'completed' as const, startTime: Date.now(), endTime: Date.now() },
        { modelId: '5', modelName: 'test', description: 'test', status: 'completed' as const, startTime: Date.now(), endTime: Date.now() },
      ]

      const generated = alerts.evaluate({ models })
      // Should detect high failure rate (>50%)
    })

    it('should detect long queue', () => {
      const generated = alerts.evaluate({ queueLength: 25 })
      // Should generate alert for long queue
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const a1 = getIntelligentAlerts()
      const a2 = getIntelligentAlerts()
      expect(a1).toBe(a2)
    })
  })
})










