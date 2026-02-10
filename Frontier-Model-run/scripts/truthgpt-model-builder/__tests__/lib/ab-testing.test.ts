/**
 * Unit Tests - A/B Testing
 */

import { ABTesting, getABTesting } from '@/lib/ab-testing'

describe('ABTesting', () => {
  let abTesting: ABTesting

  beforeEach(() => {
    abTesting = new ABTesting()
  })

  afterEach(() => {
    abTesting.clear()
  })

  describe('Test Creation', () => {
    it('should create A/B test', () => {
      const testId = abTesting.createTest({
        name: 'Test Model Config',
        variants: [
          { id: 'variant-a', name: 'Variant A', config: { learningRate: 0.001 } },
          { id: 'variant-b', name: 'Variant B', config: { learningRate: 0.002 } },
        ],
      })

      expect(testId).toBeDefined()
      const test = abTesting.getTest(testId)
      expect(test).toBeDefined()
      expect(test?.name).toBe('Test Model Config')
    })

    it('should get all tests', () => {
      abTesting.createTest({
        name: 'Test 1',
        variants: [{ id: 'v1', name: 'V1', config: {} }],
      })

      abTesting.createTest({
        name: 'Test 2',
        variants: [{ id: 'v2', name: 'V2', config: {} }],
      })

      const tests = abTesting.getAllTests()
      expect(tests.length).toBe(2)
    })
  })

  describe('Test Execution', () => {
    it('should start test', () => {
      const testId = abTesting.createTest({
        name: 'Test',
        variants: [
          { id: 'v1', name: 'V1', config: {} },
          { id: 'v2', name: 'V2', config: {} },
        ],
      })

      abTesting.startTest(testId)
      const test = abTesting.getTest(testId)
      expect(test?.status).toBe('running')
    })

    it('should record variant result', () => {
      const testId = abTesting.createTest({
        name: 'Test',
        variants: [
          { id: 'v1', name: 'V1', config: {} },
          { id: 'v2', name: 'V2', config: {} },
        ],
      })

      abTesting.startTest(testId)
      abTesting.recordResult(testId, 'v1', {
        success: true,
        duration: 5000,
        accuracy: 0.95,
      })

      const test = abTesting.getTest(testId)
      expect(test?.variants[0].results.length).toBe(1)
    })

    it('should record multiple results', () => {
      const testId = abTesting.createTest({
        name: 'Test',
        variants: [
          { id: 'v1', name: 'V1', config: {} },
          { id: 'v2', name: 'V2', config: {} },
        ],
      })

      abTesting.startTest(testId)
      
      abTesting.recordResult(testId, 'v1', { success: true, duration: 5000 })
      abTesting.recordResult(testId, 'v1', { success: true, duration: 6000 })
      abTesting.recordResult(testId, 'v2', { success: false, duration: 4000 })

      const test = abTesting.getTest(testId)
      expect(test?.variants[0].results.length).toBe(2)
      expect(test?.variants[1].results.length).toBe(1)
    })
  })

  describe('Analysis', () => {
    it('should calculate variant statistics', () => {
      const testId = abTesting.createTest({
        name: 'Test',
        variants: [
          { id: 'v1', name: 'V1', config: {} },
          { id: 'v2', name: 'V2', config: {} },
        ],
      })

      abTesting.startTest(testId)
      
      abTesting.recordResult(testId, 'v1', { success: true, duration: 5000 })
      abTesting.recordResult(testId, 'v1', { success: true, duration: 6000 })
      abTesting.recordResult(testId, 'v2', { success: true, duration: 7000 })
      abTesting.recordResult(testId, 'v2', { success: false, duration: 8000 })

      const analysis = abTesting.analyzeTest(testId)
      expect(analysis).toBeDefined()
      expect(analysis.variants).toHaveLength(2)
    })

    it('should determine winning variant', () => {
      const testId = abTesting.createTest({
        name: 'Test',
        variants: [
          { id: 'v1', name: 'V1', config: {} },
          { id: 'v2', name: 'V2', config: {} },
        ],
      })

      abTesting.startTest(testId)
      
      // V1: 100% success
      abTesting.recordResult(testId, 'v1', { success: true, duration: 5000 })
      abTesting.recordResult(testId, 'v1', { success: true, duration: 6000 })
      
      // V2: 50% success
      abTesting.recordResult(testId, 'v2', { success: true, duration: 7000 })
      abTesting.recordResult(testId, 'v2', { success: false, duration: 8000 })

      const analysis = abTesting.analyzeTest(testId)
      expect(analysis.winner).toBeDefined()
    })

    it('should calculate confidence intervals', () => {
      const testId = abTesting.createTest({
        name: 'Test',
        variants: [
          { id: 'v1', name: 'V1', config: {} },
          { id: 'v2', name: 'V2', config: {} },
        ],
      })

      abTesting.startTest(testId)
      
      for (let i = 0; i < 20; i++) {
        abTesting.recordResult(testId, 'v1', { success: true, duration: 5000 })
        abTesting.recordResult(testId, 'v2', { success: i % 2 === 0, duration: 6000 })
      }

      const analysis = abTesting.analyzeTest(testId)
      expect(analysis.variants[0].confidenceInterval).toBeDefined()
    })
  })

  describe('Test Completion', () => {
    it('should complete test', () => {
      const testId = abTesting.createTest({
        name: 'Test',
        variants: [
          { id: 'v1', name: 'V1', config: {} },
          { id: 'v2', name: 'V2', config: {} },
        ],
      })

      abTesting.startTest(testId)
      abTesting.completeTest(testId)
      
      const test = abTesting.getTest(testId)
      expect(test?.status).toBe('completed')
    })
  })

  describe('Test Removal', () => {
    it('should remove test', () => {
      const testId = abTesting.createTest({
        name: 'Test',
        variants: [{ id: 'v1', name: 'V1', config: {} }],
      })

      abTesting.removeTest(testId)
      const test = abTesting.getTest(testId)
      expect(test).toBeUndefined()
    })
  })

  describe('Edge Cases', () => {
    it('should handle test with no results', () => {
      const testId = abTesting.createTest({
        name: 'Test',
        variants: [
          { id: 'v1', name: 'V1', config: {} },
        ],
      })

      abTesting.startTest(testId)
      const analysis = abTesting.analyzeTest(testId)
      expect(analysis).toBeDefined()
    })

    it('should handle single variant', () => {
      const testId = abTesting.createTest({
        name: 'Test',
        variants: [{ id: 'v1', name: 'V1', config: {} }],
      })

      abTesting.startTest(testId)
      abTesting.recordResult(testId, 'v1', { success: true, duration: 5000 })
      
      const analysis = abTesting.analyzeTest(testId)
      expect(analysis).toBeDefined()
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const a1 = getABTesting()
      const a2 = getABTesting()
      expect(a1).toBe(a2)
    })
  })
})










