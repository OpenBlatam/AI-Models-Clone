/**
 * Unit Tests - Advanced Statistics
 */

import { AdvancedStatistics, getAdvancedStatistics } from '@/lib/advanced-statistics'

describe('AdvancedStatistics', () => {
  let stats: AdvancedStatistics

  const mockModels = [
    {
      modelId: 'model-1',
      modelName: 'test-1',
      description: 'test',
      status: 'completed' as const,
      duration: 10000,
      startTime: Date.now() - 60000,
      endTime: Date.now() - 60000,
    },
    {
      modelId: 'model-2',
      modelName: 'test-2',
      description: 'test',
      status: 'completed' as const,
      duration: 20000,
      startTime: Date.now() - 30000,
      endTime: Date.now() - 30000,
    },
    {
      modelId: 'model-3',
      modelName: 'test-3',
      description: 'test',
      status: 'failed' as const,
      error: 'Test error',
      startTime: Date.now() - 10000,
      endTime: Date.now() - 10000,
    },
  ]

  beforeEach(() => {
    stats = new AdvancedStatistics()
  })

  describe('Overview Calculation', () => {
    it('should calculate overview statistics', () => {
      const result = stats.calculateAdvancedStats(mockModels)

      expect(result.overview.totalModels).toBe(3)
      expect(result.overview.successful).toBe(2)
      expect(result.overview.failed).toBe(1)
      expect(result.overview.successRate).toBeCloseTo(2 / 3)
    })

    it('should calculate average duration', () => {
      const result = stats.calculateAdvancedStats(mockModels)

      expect(result.overview.avgDuration).toBeGreaterThan(0)
      expect(result.overview.medianDuration).toBeGreaterThan(0)
    })
  })

  describe('Trends', () => {
    it('should calculate daily trends', () => {
      const result = stats.calculateAdvancedStats(mockModels)

      expect(result.trends.daily).toBeDefined()
      expect(Array.isArray(result.trends.daily)).toBe(true)
    })

    it('should calculate weekly trends', () => {
      const result = stats.calculateAdvancedStats(mockModels)

      expect(result.trends.weekly).toBeDefined()
      expect(Array.isArray(result.trends.weekly)).toBe(true)
    })

    it('should calculate monthly trends', () => {
      const result = stats.calculateAdvancedStats(mockModels)

      expect(result.trends.monthly).toBeDefined()
      expect(Array.isArray(result.trends.monthly)).toBe(true)
    })
  })

  describe('Performance', () => {
    it('should calculate performance metrics', () => {
      const result = stats.calculateAdvancedStats(mockModels)

      expect(result.performance).toBeDefined()
      expect(result.performance.fastest).toBeDefined()
      expect(result.performance.slowest).toBeDefined()
      expect(result.performance.average).toBeGreaterThan(0)
    })

    it('should calculate percentiles', () => {
      const result = stats.calculateAdvancedStats(mockModels)

      expect(result.performance.percentile25).toBeGreaterThanOrEqual(0)
      expect(result.performance.percentile50).toBeGreaterThanOrEqual(0)
      expect(result.performance.percentile75).toBeGreaterThanOrEqual(0)
      expect(result.performance.percentile95).toBeGreaterThanOrEqual(0)
    })
  })

  describe('Patterns', () => {
    it('should detect best time of day', () => {
      const result = stats.calculateAdvancedStats(mockModels)

      expect(result.patterns.bestTimeOfDay).toBeDefined()
      expect(result.patterns.bestTimeOfDay).toMatch(/\d{1,2}:\d{2}/)
    })

    it('should detect best day of week', () => {
      const result = stats.calculateAdvancedStats(mockModels)

      expect(result.patterns.bestDayOfWeek).toBeDefined()
      expect(typeof result.patterns.bestDayOfWeek).toBe('string')
    })

    it('should identify common errors', () => {
      const result = stats.calculateAdvancedStats(mockModels)

      expect(result.patterns.commonErrors).toBeDefined()
      expect(Array.isArray(result.patterns.commonErrors)).toBe(true)
    })
  })

  describe('Predictions', () => {
    it('should make predictions', () => {
      const result = stats.calculateAdvancedStats(mockModels)

      expect(result.predictions).toBeDefined()
      expect(result.predictions.nextBuildEstimate).toBeGreaterThanOrEqual(0)
      expect(result.predictions.successProbability).toBeGreaterThanOrEqual(0)
      expect(result.predictions.successProbability).toBeLessThanOrEqual(1)
      expect(result.predictions.recommendedBatchSize).toBeGreaterThan(0)
    })
  })

  describe('Export', () => {
    it('should export statistics as JSON', () => {
      const result = stats.calculateAdvancedStats(mockModels)
      const exported = stats.exportStats(result)

      expect(typeof exported).toBe('string')
      const parsed = JSON.parse(exported)
      expect(parsed).toBeDefined()
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty models array', () => {
      const result = stats.calculateAdvancedStats([])

      expect(result.overview.totalModels).toBe(0)
      expect(result.overview.successRate).toBe(0)
    })

    it('should handle models without duration', () => {
      const modelsWithoutDuration = [
        {
          modelId: 'model-1',
          modelName: 'test-1',
          description: 'test',
          status: 'completed' as const,
          startTime: Date.now(),
          endTime: Date.now(),
        },
      ]

      const result = stats.calculateAdvancedStats(modelsWithoutDuration)
      expect(result).toBeDefined()
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const s1 = getAdvancedStatistics()
      const s2 = getAdvancedStatistics()
      expect(s1).toBe(s2)
    })
  })
})










