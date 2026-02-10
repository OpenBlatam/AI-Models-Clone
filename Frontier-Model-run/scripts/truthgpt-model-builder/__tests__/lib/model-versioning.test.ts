/**
 * Unit Tests - Model Versioning
 */

import { ModelVersioning, getModelVersioning } from '@/lib/modules/management'

describe('ModelVersioning', () => {
  let versioning: ModelVersioning

  beforeEach(() => {
    versioning = new ModelVersioning()
    if (typeof window !== 'undefined') {
      localStorage.clear()
    }
  })

  afterEach(() => {
    versioning.clear()
  })

  describe('Version Creation', () => {
    it('should create version', () => {
      const version = versioning.createVersion('model-1', {
        modelName: 'test-model',
        description: 'test',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      })

      expect(version).toBeDefined()
      expect(version.version).toBe('1.0.0')
      expect(version.modelId).toBe('model-1')
    })

    it('should increment version', () => {
      versioning.createVersion('model-1', {
        modelName: 'test-model',
        description: 'test',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      })

      const version2 = versioning.createVersion('model-1', {
        modelName: 'test-model',
        description: 'test',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      })

      expect(version2.version).toBe('1.0.1')
    })

    it('should increment minor version', () => {
      const version1 = versioning.createVersion('model-1', {
        modelName: 'test-model',
        description: 'test',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      }, 'minor')

      expect(version1.version).toBe('1.1.0')
    })

    it('should increment major version', () => {
      const version1 = versioning.createVersion('model-1', {
        modelName: 'test-model',
        description: 'test',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      }, 'major')

      expect(version1.version).toBe('2.0.0')
    })
  })

  describe('Version Retrieval', () => {
    it('should get version by ID', () => {
      const version = versioning.createVersion('model-1', {
        modelName: 'test-model',
        description: 'test',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      })

      const retrieved = versioning.getVersion(version.id)
      expect(retrieved).toBeDefined()
      expect(retrieved?.version).toBe('1.0.0')
    })

    it('should get all versions for model', () => {
      versioning.createVersion('model-1', {
        modelName: 'test-model',
        description: 'test',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      })

      versioning.createVersion('model-1', {
        modelName: 'test-model',
        description: 'test',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      })

      const versions = versioning.getVersions('model-1')
      expect(versions.length).toBe(2)
    })

    it('should get latest version', () => {
      versioning.createVersion('model-1', {
        modelName: 'test-model',
        description: 'test',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      })

      versioning.createVersion('model-1', {
        modelName: 'test-model',
        description: 'test',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      })

      const latest = versioning.getLatestVersion('model-1')
      expect(latest).toBeDefined()
      expect(latest?.version).toBe('1.0.1')
    })
  })

  describe('Performance Metadata', () => {
    it('should store performance metadata', () => {
      const version = versioning.createVersion('model-1', {
        modelName: 'test-model',
        description: 'test',
        status: 'completed',
        duration: 5000,
        startTime: Date.now(),
        endTime: Date.now(),
      }, 'patch', {
        accuracy: 0.95,
        loss: 0.05,
      })

      expect(version.metadata).toBeDefined()
      expect(version.metadata.accuracy).toBe(0.95)
      expect(version.metadata.loss).toBe(0.05)
    })
  })

  describe('Comparison', () => {
    it('should compare versions', () => {
      const v1 = versioning.createVersion('model-1', {
        modelName: 'test-model',
        description: 'test',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      }, 'patch', { accuracy: 0.90 })

      const v2 = versioning.createVersion('model-1', {
        modelName: 'test-model',
        description: 'test',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      }, 'patch', { accuracy: 0.95 })

      const comparison = versioning.compareVersions(v1.id, v2.id)
      expect(comparison).toBeDefined()
      expect(comparison.improvements).toBeDefined()
    })
  })

  describe('Statistics', () => {
    it('should calculate version statistics', () => {
      versioning.createVersion('model-1', {
        modelName: 'test-model',
        description: 'test',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      })

      versioning.createVersion('model-1', {
        modelName: 'test-model',
        description: 'test',
        status: 'completed',
        startTime: Date.now(),
        endTime: Date.now(),
      })

      const stats = versioning.getVersionStats('model-1')
      expect(stats.totalVersions).toBe(2)
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const v1 = getModelVersioning()
      const v2 = getModelVersioning()
      expect(v1).toBe(v2)
    })
  })
})










