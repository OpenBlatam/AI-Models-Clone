/**
 * Unit Tests - Favorites Manager
 */

import { FavoritesManager, getFavoritesManager } from '@/lib/favorites-manager'

describe('FavoritesManager', () => {
  let manager: FavoritesManager

  beforeEach(() => {
    manager = new FavoritesManager()
    // Clear localStorage
    if (typeof window !== 'undefined') {
      localStorage.clear()
    }
  })

  afterEach(() => {
    manager.clear()
  })

  describe('Basic Operations', () => {
    it('should add favorite', () => {
      const model = {
        modelId: 'model-1',
        modelName: 'test-model',
        description: 'test',
        status: 'completed' as const,
        startTime: Date.now(),
        endTime: Date.now(),
      }

      manager.addFavorite(model)
      expect(manager.isFavorite('model-1')).toBe(true)
    })

    it('should remove favorite', () => {
      const model = {
        modelId: 'model-1',
        modelName: 'test-model',
        description: 'test',
        status: 'completed' as const,
        startTime: Date.now(),
        endTime: Date.now(),
      }

      manager.addFavorite(model)
      manager.removeFavorite('model-1')
      expect(manager.isFavorite('model-1')).toBe(false)
    })

    it('should get favorite', () => {
      const model = {
        modelId: 'model-1',
        modelName: 'test-model',
        description: 'test',
        status: 'completed' as const,
        startTime: Date.now(),
        endTime: Date.now(),
      }

      manager.addFavorite(model, 'Test notes', ['tag1', 'tag2'])
      const favorite = manager.getFavorite('model-1')

      expect(favorite).toBeDefined()
      expect(favorite?.notes).toBe('Test notes')
      expect(favorite?.tags).toEqual(['tag1', 'tag2'])
    })

    it('should get all favorites', () => {
      for (let i = 0; i < 5; i++) {
        manager.addFavorite({
          modelId: `model-${i}`,
          modelName: `test-${i}`,
          description: 'test',
          status: 'completed' as const,
          startTime: Date.now(),
          endTime: Date.now(),
        })
      }

      const favorites = manager.getAllFavorites()
      expect(favorites).toHaveLength(5)
    })
  })

  describe('Search', () => {
    it('should search favorites by name', () => {
      manager.addFavorite({
        modelId: 'model-1',
        modelName: 'classification-model',
        description: 'test',
        status: 'completed' as const,
        startTime: Date.now(),
        endTime: Date.now(),
      })

      const results = manager.searchFavorites('classification')
      expect(results.length).toBeGreaterThan(0)
    })

    it('should search favorites by notes', () => {
      manager.addFavorite(
        {
          modelId: 'model-1',
          modelName: 'test-model',
          description: 'test',
          status: 'completed' as const,
          startTime: Date.now(),
          endTime: Date.now(),
        },
        'Important model for production'
      )

      const results = manager.searchFavorites('production')
      expect(results.length).toBeGreaterThan(0)
    })

    it('should search favorites by tags', () => {
      manager.addFavorite(
        {
          modelId: 'model-1',
          modelName: 'test-model',
          description: 'test',
          status: 'completed' as const,
          startTime: Date.now(),
          endTime: Date.now(),
        },
        undefined,
        ['production', 'important']
      )

      const results = manager.searchFavorites('production')
      expect(results.length).toBeGreaterThan(0)
    })
  })

  describe('Update', () => {
    it('should update favorite', () => {
      manager.addFavorite({
        modelId: 'model-1',
        modelName: 'test-model',
        description: 'test',
        status: 'completed' as const,
        startTime: Date.now(),
        endTime: Date.now(),
      })

      const updated = manager.updateFavorite('model-1', {
        notes: 'Updated notes',
      })

      expect(updated?.notes).toBe('Updated notes')
    })
  })

  describe('Tags', () => {
    it('should get favorites by tag', () => {
      manager.addFavorite(
        {
          modelId: 'model-1',
          modelName: 'test-1',
          description: 'test',
          status: 'completed' as const,
          startTime: Date.now(),
          endTime: Date.now(),
        },
        undefined,
        ['production']
      )

      manager.addFavorite(
        {
          modelId: 'model-2',
          modelName: 'test-2',
          description: 'test',
          status: 'completed' as const,
          startTime: Date.now(),
          endTime: Date.now(),
        },
        undefined,
        ['development']
      )

      const production = manager.getFavoritesByTag('production')
      expect(production).toHaveLength(1)
      expect(production[0].modelId).toBe('model-1')
    })

    it('should get all tags', () => {
      manager.addFavorite(
        {
          modelId: 'model-1',
          modelName: 'test-1',
          description: 'test',
          status: 'completed' as const,
          startTime: Date.now(),
          endTime: Date.now(),
        },
        undefined,
        ['tag1', 'tag2']
      )

      const tags = manager.getAllTags()
      expect(tags).toContain('tag1')
      expect(tags).toContain('tag2')
    })
  })

  describe('Statistics', () => {
    it('should calculate statistics', () => {
      manager.addFavorite({
        modelId: 'model-1',
        modelName: 'test-1',
        description: 'test',
        status: 'completed' as const,
        duration: 10000,
        startTime: Date.now(),
        endTime: Date.now(),
      })

      manager.addFavorite({
        modelId: 'model-2',
        modelName: 'test-2',
        description: 'test',
        status: 'failed' as const,
        startTime: Date.now(),
        endTime: Date.now(),
      })

      const stats = manager.getStats()
      expect(stats.total).toBe(2)
      expect(stats.byStatus.completed).toBe(1)
      expect(stats.byStatus.failed).toBe(1)
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const m1 = getFavoritesManager()
      const m2 = getFavoritesManager()
      expect(m1).toBe(m2)
    })
  })
})










