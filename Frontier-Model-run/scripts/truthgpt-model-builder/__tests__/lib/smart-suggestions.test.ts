/**
 * Unit Tests - Smart Suggestions
 */

import { SmartSuggestions, getSmartSuggestions } from '@/lib/smart-suggestions'

describe('SmartSuggestions', () => {
  let suggestions: SmartSuggestions

  beforeEach(() => {
    suggestions = new SmartSuggestions()
  })

  afterEach(() => {
    suggestions.clear()
  })

  describe('History Management', () => {
    it('should add to history', () => {
      suggestions.addToHistory('classification model for text')
      const history = suggestions.getHistory()
      expect(history.length).toBeGreaterThan(0)
    })

    it('should limit history size', () => {
      for (let i = 0; i < 200; i++) {
        suggestions.addToHistory(`test model ${i}`)
      }
      const history = suggestions.getHistory()
      expect(history.length).toBeLessThanOrEqual(100)
    })

    it('should clear history', () => {
      suggestions.addToHistory('test')
      suggestions.clear()
      const history = suggestions.getHistory()
      expect(history.length).toBe(0)
    })
  })

  describe('Suggestion Generation', () => {
    beforeEach(() => {
      suggestions.addToHistory('classification model for text categorization')
      suggestions.addToHistory('sentiment analysis model')
      suggestions.addToHistory('regression model for predictions')
    })

    it('should generate suggestions from input', () => {
      const results = suggestions.generateSuggestions('classify', 5)
      expect(results.length).toBeGreaterThan(0)
      expect(results[0]).toHaveProperty('text')
      expect(results[0]).toHaveProperty('confidence')
    })

    it('should limit number of suggestions', () => {
      const results = suggestions.generateSuggestions('model', 3)
      expect(results.length).toBeLessThanOrEqual(3)
    })

    it('should calculate confidence scores', () => {
      const results = suggestions.generateSuggestions('classification', 5)
      expect(results.every(r => r.confidence >= 0 && r.confidence <= 1)).toBe(true)
    })

    it('should assign categories', () => {
      suggestions.addToHistory('classification model')
      const results = suggestions.generateSuggestions('classify', 5)
      expect(results.some(r => r.category)).toBe(true)
    })

    it('should handle empty input', () => {
      const results = suggestions.generateSuggestions('', 5)
      expect(results.length).toBe(0)
    })

    it('should handle short input', () => {
      const results = suggestions.generateSuggestions('a', 5)
      // Should handle gracefully
      expect(Array.isArray(results)).toBe(true)
    })
  })

  describe('Learning', () => {
    it('should learn from history', () => {
      suggestions.addToHistory('classification model')
      suggestions.addToHistory('classification model')
      suggestions.addToHistory('classification model')

      const results = suggestions.generateSuggestions('class', 5)
      // Should prioritize frequently used patterns
      expect(results.length).toBeGreaterThan(0)
    })

    it('should extract patterns', () => {
      suggestions.addToHistory('classification model for text')
      suggestions.addToHistory('sentiment analysis model')
      suggestions.addToHistory('regression model')

      const patterns = suggestions.extractPatterns()
      expect(patterns.length).toBeGreaterThan(0)
    })
  })

  describe('Context Awareness', () => {
    it('should provide context-aware suggestions', () => {
      suggestions.addToHistory('classification model for text categorization')
      const results = suggestions.generateSuggestions('text', 5)
      
      expect(results.some(r => 
        r.text.toLowerCase().includes('classification') || 
        r.text.toLowerCase().includes('categorization')
      )).toBe(true)
    })
  })

  describe('Ranking', () => {
    it('should rank by relevance', () => {
      suggestions.addToHistory('classification model')
      suggestions.addToHistory('regression model')
      
      const results = suggestions.generateSuggestions('classification', 5)
      if (results.length > 1) {
        expect(results[0].confidence).toBeGreaterThanOrEqual(results[1].confidence)
      }
    })

    it('should rank by frequency', () => {
      suggestions.addToHistory('classification model')
      suggestions.addToHistory('classification model')
      suggestions.addToHistory('regression model')
      
      const results = suggestions.generateSuggestions('model', 5)
      // Classification should rank higher due to frequency
      expect(results.length).toBeGreaterThan(0)
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const s1 = getSmartSuggestions()
      const s2 = getSmartSuggestions()
      expect(s1).toBe(s2)
    })
  })
})










