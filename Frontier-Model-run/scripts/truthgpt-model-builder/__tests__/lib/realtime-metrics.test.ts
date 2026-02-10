/**
 * Unit Tests - Real-time Metrics
 */

import { RealTimeMetrics, getRealTimeMetrics } from '@/lib/realtime-metrics'

describe('RealTimeMetrics', () => {
  let metrics: RealTimeMetrics

  beforeEach(() => {
    metrics = new RealTimeMetrics()
  })

  afterEach(() => {
    metrics.clear()
    metrics.stopAutoUpdate()
  })

  describe('Metric Registration', () => {
    it('should register metric', () => {
      const metric = metrics.registerMetric('test-metric', 'Test Metric', 'units')
      
      expect(metric).toBeDefined()
      expect(metric.id).toBe('test-metric')
      expect(metric.name).toBe('Test Metric')
      expect(metric.unit).toBe('units')
    })

    it('should get registered metric', () => {
      metrics.registerMetric('test-metric', 'Test Metric')
      const metric = metrics.getMetric('test-metric')
      
      expect(metric).toBeDefined()
      expect(metric?.name).toBe('Test Metric')
    })
  })

  describe('Metric Updates', () => {
    it('should update metric value', () => {
      metrics.registerMetric('test-metric', 'Test Metric')
      metrics.updateMetric('test-metric', 100)
      
      const metric = metrics.getMetric('test-metric')
      expect(metric?.currentValue).toBe(100)
      expect(metric?.data).toHaveLength(1)
    })

    it('should calculate statistics', () => {
      metrics.registerMetric('test-metric', 'Test Metric')
      
      metrics.updateMetric('test-metric', 10)
      metrics.updateMetric('test-metric', 20)
      metrics.updateMetric('test-metric', 30)
      
      const metric = metrics.getMetric('test-metric')
      expect(metric?.minValue).toBe(10)
      expect(metric?.maxValue).toBe(30)
      expect(metric?.avgValue).toBe(20)
    })

    it('should limit data points', () => {
      metrics.registerMetric('test-metric', 'Test Metric')
      
      for (let i = 0; i < 150; i++) {
        metrics.updateMetric('test-metric', i)
      }
      
      const metric = metrics.getMetric('test-metric')
      expect(metric?.data.length).toBeLessThanOrEqual(100)
    })
  })

  describe('Trends', () => {
    it('should detect upward trend', () => {
      metrics.registerMetric('test-metric', 'Test Metric')
      
      // Older values
      for (let i = 0; i < 5; i++) {
        metrics.updateMetric('test-metric', 10)
      }
      
      // Recent values (higher)
      for (let i = 0; i < 5; i++) {
        metrics.updateMetric('test-metric', 20)
      }
      
      const metric = metrics.getMetric('test-metric')
      expect(metric?.trend).toBe('up')
    })

    it('should detect downward trend', () => {
      metrics.registerMetric('test-metric', 'Test Metric')
      
      // Older values
      for (let i = 0; i < 5; i++) {
        metrics.updateMetric('test-metric', 20)
      }
      
      // Recent values (lower)
      for (let i = 0; i < 5; i++) {
        metrics.updateMetric('test-metric', 10)
      }
      
      const metric = metrics.getMetric('test-metric')
      expect(metric?.trend).toBe('down')
    })

    it('should detect stable trend', () => {
      metrics.registerMetric('test-metric', 'Test Metric')
      
      for (let i = 0; i < 10; i++) {
        metrics.updateMetric('test-metric', 15)
      }
      
      const metric = metrics.getMetric('test-metric')
      expect(metric?.trend).toBe('stable')
    })
  })

  describe('Subscriptions', () => {
    it('should notify subscribers on update', (done) => {
      metrics.registerMetric('test-metric', 'Test Metric')
      
      const callback = jest.fn((metric) => {
        expect(metric.currentValue).toBe(100)
        done()
      })
      
      metrics.subscribe('test-metric', callback)
      metrics.updateMetric('test-metric', 100)
    })

    it('should allow unsubscribing', () => {
      metrics.registerMetric('test-metric', 'Test Metric')
      
      const callback = jest.fn()
      const unsubscribe = metrics.subscribe('test-metric', callback)
      
      unsubscribe()
      metrics.updateMetric('test-metric', 100)
      
      expect(callback).not.toHaveBeenCalled()
    })
  })

  describe('Model Metrics', () => {
    it('should calculate builds per minute', () => {
      const now = Date.now()
      const models = [
        {
          modelId: 'model-1',
          modelName: 'test-1',
          description: 'test',
          status: 'completed' as const,
          startTime: now - 30000,
          endTime: now - 30000,
        },
        {
          modelId: 'model-2',
          modelName: 'test-2',
          description: 'test',
          status: 'completed' as const,
          startTime: now - 20000,
          endTime: now - 20000,
        },
      ]
      
      const result = metrics.calculateModelMetrics(models)
      expect(result.buildsPerMinute).toBe(2)
    })

    it('should calculate success rate', () => {
      const now = Date.now()
      const models = [
        {
          modelId: 'model-1',
          modelName: 'test-1',
          description: 'test',
          status: 'completed' as const,
          startTime: now,
          endTime: now,
        },
        {
          modelId: 'model-2',
          modelName: 'test-2',
          description: 'test',
          status: 'failed' as const,
          startTime: now,
          endTime: now,
        },
      ]
      
      const result = metrics.calculateModelMetrics(models)
      expect(result.successRate).toBe(0.5)
    })

    it('should calculate average duration', () => {
      const now = Date.now()
      const models = [
        {
          modelId: 'model-1',
          modelName: 'test-1',
          description: 'test',
          status: 'completed' as const,
          duration: 10000,
          startTime: now,
          endTime: now,
        },
        {
          modelId: 'model-2',
          modelName: 'test-2',
          description: 'test',
          status: 'completed' as const,
          duration: 20000,
          startTime: now,
          endTime: now,
        },
      ]
      
      const result = metrics.calculateModelMetrics(models)
      expect(result.avgDuration).toBe(15000)
    })
  })

  describe('Auto Update', () => {
    it('should start and stop auto update', () => {
      const updateFn = jest.fn()
      
      metrics.startAutoUpdate(updateFn)
      expect(metrics).toBeDefined()
      
      metrics.stopAutoUpdate()
      // Update function should not be called after stop
    })
  })

  describe('Export', () => {
    it('should export metrics as JSON', () => {
      metrics.registerMetric('test-metric', 'Test Metric')
      metrics.updateMetric('test-metric', 100)
      
      const exported = metrics.exportMetrics()
      const parsed = JSON.parse(exported)
      
      expect(parsed).toBeInstanceOf(Array)
      expect(parsed.length).toBeGreaterThan(0)
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const m1 = getRealTimeMetrics()
      const m2 = getRealTimeMetrics()
      expect(m1).toBe(m2)
    })
  })
})










