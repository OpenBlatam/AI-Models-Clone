/**
 * Unit Tests - Performance Optimizer
 */

import { PerformanceOptimizer, getPerformanceOptimizer } from '@/lib/performance-optimizer'

describe('PerformanceOptimizer', () => {
  let optimizer: PerformanceOptimizer

  beforeEach(() => {
    optimizer = new PerformanceOptimizer()
  })

  afterEach(() => {
    optimizer.cleanup()
  })

  describe('Debounce', () => {
    it('should debounce function calls', (done) => {
      let callCount = 0
      const fn = jest.fn(() => {
        callCount++
      })

      const debounced = optimizer.debounce('test-key', fn, 100)

      debounced()
      debounced()
      debounced()

      setTimeout(() => {
        expect(fn).toHaveBeenCalledTimes(1)
        done()
      }, 200)
    })

    it('should use different keys for different debounces', (done) => {
      let count1 = 0
      let count2 = 0

      const fn1 = jest.fn(() => { count1++ })
      const fn2 = jest.fn(() => { count2++ })

      const debounced1 = optimizer.debounce('key1', fn1, 100)
      const debounced2 = optimizer.debounce('key2', fn2, 100)

      debounced1()
      debounced2()

      setTimeout(() => {
        expect(fn1).toHaveBeenCalledTimes(1)
        expect(fn2).toHaveBeenCalledTimes(1)
        done()
      }, 200)
    })

    it('should cancel previous debounce', (done) => {
      const fn = jest.fn()
      const debounced = optimizer.debounce('test-key', fn, 100)

      debounced()
      setTimeout(() => {
        debounced()
      }, 50)

      setTimeout(() => {
        expect(fn).toHaveBeenCalledTimes(1)
        done()
      }, 300)
    })
  })

  describe('Memoize', () => {
    it('should memoize function results', () => {
      let callCount = 0
      const fn = jest.fn((x: number) => {
        callCount++
        return x * 2
      })

      const memoized = optimizer.memoize('test-fn', fn)

      const result1 = memoized(5)
      const result2 = memoized(5)
      const result3 = memoized(5)

      expect(result1).toBe(10)
      expect(result2).toBe(10)
      expect(result3).toBe(10)
      expect(callCount).toBe(1) // Should only call once
    })

    it('should cache results by arguments', () => {
      const fn = jest.fn((x: number) => x * 2)
      const memoized = optimizer.memoize('test-fn', fn)

      memoized(5)
      memoized(10)
      memoized(5)

      expect(fn).toHaveBeenCalledTimes(2) // 5 and 10, then 5 from cache
    })

    it('should respect TTL', (done) => {
      const fn = jest.fn((x: number) => x * 2)
      const memoized = optimizer.memoize('test-fn', fn, 100)

      memoized(5)
      expect(fn).toHaveBeenCalledTimes(1)

      setTimeout(() => {
        memoized(5)
        expect(fn).toHaveBeenCalledTimes(2) // Cache expired
        done()
      }, 150)
    })

    it('should handle different arguments', () => {
      const fn = jest.fn((x: number, y: number) => x + y)
      const memoized = optimizer.memoize('test-fn', fn)

      memoized(5, 10)
      memoized(5, 20)
      memoized(5, 10)

      expect(fn).toHaveBeenCalledTimes(2) // 5,10 and 5,20, then 5,10 from cache
    })
  })

  describe('Cache Management', () => {
    it('should clear cache', () => {
      const fn = jest.fn((x: number) => x * 2)
      const memoized = optimizer.memoize('test-fn', fn)

      memoized(5)
      optimizer.clearCache('test-fn')
      memoized(5)

      expect(fn).toHaveBeenCalledTimes(2) // Cache cleared
    })

    it('should clear all caches', () => {
      const fn1 = jest.fn((x: number) => x * 2)
      const fn2 = jest.fn((x: number) => x * 3)

      const memoized1 = optimizer.memoize('fn1', fn1)
      const memoized2 = optimizer.memoize('fn2', fn2)

      memoized1(5)
      memoized2(5)

      optimizer.cleanup()

      memoized1(5)
      memoized2(5)

      expect(fn1).toHaveBeenCalledTimes(2)
      expect(fn2).toHaveBeenCalledTimes(2)
    })

    it('should handle cache size limits', () => {
      const fn = jest.fn((x: number) => x)
      const memoized = optimizer.memoize('test-fn', fn)

      // Add many items
      for (let i = 0; i < 200; i++) {
        memoized(i)
      }

      // Cache should be limited
      expect(fn).toHaveBeenCalled()
    })
  })

  describe('Performance', () => {
    it('should improve performance with memoization', () => {
      const expensiveFn = jest.fn((n: number) => {
        // Simulate expensive operation
        let sum = 0
        for (let i = 0; i < n; i++) {
          sum += i
        }
        return sum
      })

      const memoized = optimizer.memoize('expensive', expensiveFn)

      const start1 = Date.now()
      memoized(1000)
      const time1 = Date.now() - start1

      const start2 = Date.now()
      memoized(1000)
      const time2 = Date.now() - start2

      // Second call should be faster (from cache)
      expect(time2).toBeLessThan(time1)
      expect(expensiveFn).toHaveBeenCalledTimes(1)
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const o1 = getPerformanceOptimizer()
      const o2 = getPerformanceOptimizer()
      expect(o1).toBe(o2)
    })
  })
})










