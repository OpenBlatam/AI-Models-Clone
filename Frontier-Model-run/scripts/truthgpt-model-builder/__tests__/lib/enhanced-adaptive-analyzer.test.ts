/**
 * Unit Tests - Enhanced Adaptive Analyzer
 */

import { EnhancedAdaptiveAnalyzer, getEnhancedAdaptiveAnalyzer } from '@/lib/enhanced-adaptive-analyzer'

describe('EnhancedAdaptiveAnalyzer', () => {
  let analyzer: EnhancedAdaptiveAnalyzer

  beforeEach(() => {
    analyzer = new EnhancedAdaptiveAnalyzer()
  })

  describe('Analysis', () => {
    it('should analyze model description', () => {
      const result = analyzer.analyze('classification model for text categorization')
      
      expect(result).toBeDefined()
      expect(result.parameters).toBeDefined()
      expect(result.confidence).toBeGreaterThanOrEqual(0)
      expect(result.confidence).toBeLessThanOrEqual(1)
    })

    it('should extract learning rate', () => {
      const result = analyzer.analyze('classification model with learning rate 0.001')
      
      expect(result.parameters.learningRate).toBeDefined()
      expect(result.parameters.learningRate).toBe(0.001)
    })

    it('should extract batch size', () => {
      const result = analyzer.analyze('model with batch size 64')
      
      expect(result.parameters.batchSize).toBeDefined()
      expect(result.parameters.batchSize).toBe(64)
    })

    it('should extract epochs', () => {
      const result = analyzer.analyze('model trained for 100 epochs')
      
      expect(result.parameters.epochs).toBeDefined()
      expect(result.parameters.epochs).toBe(100)
    })

    it('should calculate confidence score', () => {
      const detailed = analyzer.analyze('classification model with learning rate 0.001, batch size 32, epochs 50')
      const vague = analyzer.analyze('some model')
      
      expect(detailed.confidence).toBeGreaterThan(vague.confidence)
    })
  })

  describe('Warnings', () => {
    it('should generate warnings for missing parameters', () => {
      const result = analyzer.analyze('classification model')
      
      expect(result.warnings).toBeDefined()
      expect(Array.isArray(result.warnings)).toBe(true)
    })

    it('should warn about high learning rate', () => {
      const result = analyzer.analyze('model with learning rate 1.0')
      
      expect(result.warnings.some(w => 
        w.message.toLowerCase().includes('learning rate') ||
        w.message.toLowerCase().includes('high')
      )).toBe(true)
    })

    it('should warn about large batch size', () => {
      const result = analyzer.analyze('model with batch size 1000')
      
      expect(result.warnings.some(w => 
        w.message.toLowerCase().includes('batch') ||
        w.message.toLowerCase().includes('large')
      )).toBe(true)
    })
  })

  describe('Resource Estimation', () => {
    it('should estimate resources', () => {
      const result = analyzer.analyze('large classification model with 1000 layers')
      
      expect(result.resourceEstimation).toBeDefined()
      expect(result.resourceEstimation.memory).toBeGreaterThan(0)
      expect(result.resourceEstimation.compute).toBeGreaterThan(0)
    })

    it('should estimate based on complexity', () => {
      const simple = analyzer.analyze('simple classification model')
      const complex = analyzer.analyze('deep neural network with 100 layers and attention mechanisms')
      
      expect(complex.resourceEstimation.memory).toBeGreaterThan(simple.resourceEstimation.memory)
      expect(complex.resourceEstimation.compute).toBeGreaterThan(simple.resourceEstimation.compute)
    })
  })

  describe('Complexity Evaluation', () => {
    it('should evaluate complexity', () => {
      const result = analyzer.analyze('classification model')
      
      expect(result.complexity).toBeDefined()
      expect(result.complexity.score).toBeGreaterThanOrEqual(0)
      expect(result.complexity.score).toBeLessThanOrEqual(1)
    })

    it('should identify complexity factors', () => {
      const result = analyzer.analyze('deep neural network with attention and transformer layers')
      
      expect(result.complexity.factors.length).toBeGreaterThan(0)
    })

    it('should classify complexity level', () => {
      const simple = analyzer.analyze('simple linear model')
      const complex = analyzer.analyze('deep transformer with 100 layers')
      
      expect(complex.complexity.level).toBe('high')
      expect(simple.complexity.level).toBe('low')
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty description', () => {
      const result = analyzer.analyze('')
      
      expect(result).toBeDefined()
      expect(result.confidence).toBe(0)
    })

    it('should handle very short description', () => {
      const result = analyzer.analyze('model')
      
      expect(result).toBeDefined()
      expect(result.confidence).toBeLessThan(0.5)
    })

    it('should handle very long description', () => {
      const longDescription = 'classification model '.repeat(100)
      const result = analyzer.analyze(longDescription)
      
      expect(result).toBeDefined()
    })

    it('should handle special characters', () => {
      const result = analyzer.analyze('classification model with @special #chars & symbols')
      
      expect(result).toBeDefined()
    })
  })

  describe('Pattern Recognition', () => {
    it('should recognize classification pattern', () => {
      const result = analyzer.analyze('classification model for text categorization')
      
      expect(result.parameters.taskType).toBe('classification')
    })

    it('should recognize regression pattern', () => {
      const result = analyzer.analyze('regression model for price prediction')
      
      expect(result.parameters.taskType).toBe('regression')
    })

    it('should recognize NLP pattern', () => {
      const result = analyzer.analyze('sentiment analysis model for text')
      
      expect(result.parameters.domain).toBe('nlp')
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const a1 = getEnhancedAdaptiveAnalyzer()
      const a2 = getEnhancedAdaptiveAnalyzer()
      expect(a1).toBe(a2)
    })
  })
})










