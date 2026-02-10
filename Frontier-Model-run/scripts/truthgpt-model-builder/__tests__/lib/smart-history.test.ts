/**
 * Unit Tests - Smart History
 */

import { SmartHistory, getSmartHistory } from '@/lib/smart-history'

describe('SmartHistory', () => {
  let history: SmartHistory

  beforeEach(() => {
    history = new SmartHistory()
  })

  afterEach(() => {
    history.clear()
  })

  describe('Basic Operations', () => {
    it('should add model to history', () => {
      const model = {
        modelId: 'model-1',
        modelName: 'test-model',
        description: 'test description',
        status: 'completed' as const,
        duration: 5000,
        startTime: Date.now(),
        endTime: Date.now(),
      }

      history.addModel(model)
      expect(history.getAllModels()).toHaveLength(1)
      expect(history.getAllModels()[0].modelId).toBe('model-1')
    })

    it('should search models by query', () => {
      history.addModel({
        modelId: 'model-1',
        modelName: 'test-model',
        description: 'classification model',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      })

      history.addModel({
        modelId: 'model-2',
        modelName: 'another-model',
        description: 'sentiment analysis',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      })

      const results = history.search({ query: 'classification' })
      expect(results).toHaveLength(1)
      expect(results[0].modelId).toBe('model-1')
    })

    it('should filter by status', () => {
      history.addModel({
        modelId: 'model-1',
        modelName: 'test-1',
        description: 'test',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      })

      history.addModel({
        modelId: 'model-2',
        modelName: 'test-2',
        description: 'test',
        status: 'failed',
        startTime: Date.now(),
        endTime: Date.now(),
      })

      const completed = history.search({ status: 'completed' })
      const failed = history.search({ status: 'failed' })

      expect(completed).toHaveLength(1)
      expect(completed[0].status).toBe('completed')
      expect(failed).toHaveLength(1)
      expect(failed[0].status).toBe('failed')
    })

    it('should filter by date range', () => {
      const now = Date.now()
      const yesterday = now - 86400000

      history.addModel({
        modelId: 'model-1',
        modelName: 'test-1',
        description: 'test',
        status: 'completed',
        startTime: yesterday,
        endTime: yesterday,
      })

      history.addModel({
        modelId: 'model-2',
        modelName: 'test-2',
        description: 'test',
        status: 'completed',
        startTime: now,
        endTime: now,
      })

      const recent = history.search({
        dateRange: {
          start: now - 1000,
          end: now + 1000,
        },
      })

      expect(recent).toHaveLength(1)
      expect(recent[0].modelId).toBe('model-2')
    })

    it('should filter by duration', () => {
      history.addModel({
        modelId: 'model-1',
        modelName: 'test-1',
        description: 'test',
        status: 'completed',
        duration: 10000,
        startTime: Date.now(),
        endTime: Date.now(),
      })

      history.addModel({
        modelId: 'model-2',
        modelName: 'test-2',
        description: 'test',
        status: 'completed',
        duration: 50000,
        startTime: Date.now(),
        endTime: Date.now(),
      })

      const fast = history.search({ maxDuration: 20000 })
      expect(fast).toHaveLength(1)
      expect(fast[0].modelId).toBe('model-1')
    })

    it('should sort by date', () => {
      const now = Date.now()
      
      history.addModel({
        modelId: 'model-1',
        modelName: 'test-1',
        description: 'test',
        status: 'completed',
        startTime: now - 1000,
        endTime: now - 1000,
      })

      history.addModel({
        modelId: 'model-2',
        modelName: 'test-2',
        description: 'test',
        status: 'completed',
        startTime: now,
        endTime: now,
      })

      const sorted = history.search({ sortBy: 'date', sortOrder: 'desc' })
      expect(sorted[0].modelId).toBe('model-2')
      expect(sorted[1].modelId).toBe('model-1')
    })

    it('should sort by duration', () => {
      history.addModel({
        modelId: 'model-1',
        modelName: 'test-1',
        description: 'test',
        status: 'completed',
        duration: 50000,
        startTime: Date.now(),
        endTime: Date.now(),
      })

      history.addModel({
        modelId: 'model-2',
        modelName: 'test-2',
        description: 'test',
        status: 'completed',
        duration: 10000,
        startTime: Date.now(),
        endTime: Date.now(),
      })

      const sorted = history.search({ sortBy: 'duration', sortOrder: 'asc' })
      expect(sorted[0].modelId).toBe('model-2')
      expect(sorted[1].modelId).toBe('model-1')
    })
  })

  describe('Grouping', () => {
    it('should group by date', () => {
      const now = Date.now()
      const today = new Date(now).toISOString().split('T')[0]

      history.addModel({
        modelId: 'model-1',
        modelName: 'test-1',
        description: 'test',
        status: 'completed',
        startTime: now,
        endTime: now,
      })

      history.addModel({
        modelId: 'model-2',
        modelName: 'test-2',
        description: 'test',
        status: 'completed',
        startTime: now,
        endTime: now,
      })

      const groups = history.groupByDate(history.getAllModels())
      expect(groups).toHaveLength(1)
      expect(groups[0].date).toBe(today)
      expect(groups[0].count).toBe(2)
    })
  })

  describe('Suggestions', () => {
    it('should generate search suggestions', () => {
      history.addModel({
        modelId: 'model-1',
        modelName: 'classification-model',
        description: 'classifies text into categories',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      })

      const suggestions = history.getSearchSuggestions('class')
      expect(suggestions.length).toBeGreaterThan(0)
      expect(suggestions.some(s => s.includes('class'))).toBe(true)
    })
  })

  describe('Recent Models', () => {
    it('should get recent models', () => {
      for (let i = 0; i < 15; i++) {
        history.addModel({
          modelId: `model-${i}`,
          modelName: `test-${i}`,
          description: 'test',
          status: 'completed',
          startTime: Date.now() - i * 1000,
          endTime: Date.now() - i * 1000,
        })
      }

      const recent = history.getRecentModels(10)
      expect(recent).toHaveLength(10)
      expect(recent[0].modelId).toBe('model-14') // Most recent
    })
  })

  describe('Fastest Models', () => {
    it('should get fastest models', () => {
      history.addModel({
        modelId: 'model-1',
        modelName: 'test-1',
        description: 'test',
        status: 'completed',
        duration: 50000,
        startTime: Date.now(),
        endTime: Date.now(),
      })

      history.addModel({
        modelId: 'model-2',
        modelName: 'test-2',
        description: 'test',
        status: 'completed',
        duration: 10000,
        startTime: Date.now(),
        endTime: Date.now(),
      })

      const fastest = history.getFastestModels(1)
      expect(fastest).toHaveLength(1)
      expect(fastest[0].modelId).toBe('model-2')
    })
  })

  describe('Search Stats', () => {
    it('should calculate search statistics', () => {
      history.addModel({
        modelId: 'model-1',
        modelName: 'test-1',
        description: 'classification',
        status: 'completed',
        duration: 10000,
        startTime: Date.now(),
        endTime: Date.now(),
      })

      history.addModel({
        modelId: 'model-2',
        modelName: 'test-2',
        description: 'classification',
        status: 'failed',
        startTime: Date.now(),
        endTime: Date.now(),
      })

      const stats = history.getSearchStats('classification')
      expect(stats.totalMatches).toBe(2)
      expect(stats.completed).toBe(1)
      expect(stats.failed).toBe(1)
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const h1 = getSmartHistory()
      const h2 = getSmartHistory()
      expect(h1).toBe(h2)
    })
  })
})










