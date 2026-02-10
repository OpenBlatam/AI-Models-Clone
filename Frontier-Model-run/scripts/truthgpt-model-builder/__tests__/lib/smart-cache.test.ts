/**
 * Unit Tests - Smart Cache
 */

import { SmartCache, getSmartCache } from '@/lib/smart-cache'

describe('SmartCache', () => {
  let cache: SmartCache

  beforeEach(() => {
    cache = new SmartCache({ maxSize: 10, strategy: 'lru' })
  })

  afterEach(() => {
    cache.clear()
  })

  describe('Basic Operations', () => {
    it('should set and get value', () => {
      cache.set('key1', 'value1')
      expect(cache.get('key1')).toBe('value1')
    })

    it('should return null for non-existent key', () => {
      expect(cache.get('nonexistent')).toBeNull()
    })

    it('should delete value', () => {
      cache.set('key1', 'value1')
      expect(cache.delete('key1')).toBe(true)
      expect(cache.get('key1')).toBeNull()
    })

    it('should check if key exists', () => {
      cache.set('key1', 'value1')
      expect(cache.has('key1')).toBe(true)
      expect(cache.has('nonexistent')).toBe(false)
    })

    it('should clear all entries', () => {
      cache.set('key1', 'value1')
      cache.set('key2', 'value2')
      cache.clear()
      expect(cache.get('key1')).toBeNull()
      expect(cache.get('key2')).toBeNull()
    })
  })

  describe('TTL (Time To Live)', () => {
    it('should expire entry after TTL', (done) => {
      cache.set('key1', 'value1', 100) // 100ms TTL
      expect(cache.get('key1')).toBe('value1')
      
      setTimeout(() => {
        expect(cache.get('key1')).toBeNull()
        done()
      }, 150)
    })

    it('should not expire entry before TTL', (done) => {
      cache.set('key1', 'value1', 200)
      setTimeout(() => {
        expect(cache.get('key1')).toBe('value1')
        done()
      }, 100)
    })
  })

  describe('LRU Strategy', () => {
    it('should evict least recently used when full', () => {
      const lruCache = new SmartCache({ maxSize: 3, strategy: 'lru' })
      
      lruCache.set('key1', 'value1')
      lruCache.set('key2', 'value2')
      lruCache.set('key3', 'value3')
      
      // Access key1 to make it recently used
      lruCache.get('key1')
      
      // Add new key - should evict key2 (least recently used)
      lruCache.set('key4', 'value4')
      
      expect(lruCache.get('key1')).toBe('value1')
      expect(lruCache.get('key2')).toBeNull() // Evicted
      expect(lruCache.get('key3')).toBe('value3')
      expect(lruCache.get('key4')).toBe('value4')
    })
  })

  describe('LFU Strategy', () => {
    it('should evict least frequently used when full', () => {
      const lfuCache = new SmartCache({ maxSize: 3, strategy: 'lfu' })
      
      lfuCache.set('key1', 'value1')
      lfuCache.set('key2', 'value2')
      lfuCache.set('key3', 'value3')
      
      // Access key1 and key3 multiple times
      lfuCache.get('key1')
      lfuCache.get('key1')
      lfuCache.get('key3')
      lfuCache.get('key3')
      
      // Add new key - should evict key2 (least frequently used)
      lfuCache.set('key4', 'value4')
      
      expect(lfuCache.get('key1')).toBe('value1')
      expect(lfuCache.get('key2')).toBeNull() // Evicted
      expect(lfuCache.get('key3')).toBe('value3')
    })
  })

  describe('Statistics', () => {
    it('should calculate correct statistics', () => {
      cache.set('key1', 'value1')
      cache.set('key2', 'value2')
      cache.get('key1')
      cache.get('key1')
      cache.get('key2')
      
      const stats = cache.getStats()
      
      expect(stats.size).toBe(2)
      expect(stats.maxSize).toBe(10)
      expect(stats.totalHits).toBe(2)
      expect(stats.totalAccesses).toBeGreaterThan(0)
    })
  })

  describe('Clean Expired', () => {
    it('should clean expired entries', (done) => {
      cache.set('key1', 'value1', 50)
      cache.set('key2', 'value2', 50)
      cache.set('key3', 'value3') // No expiration
      
      setTimeout(() => {
        const cleaned = cache.cleanExpired()
        expect(cleaned).toBe(2)
        expect(cache.get('key1')).toBeNull()
        expect(cache.get('key2')).toBeNull()
        expect(cache.get('key3')).toBe('value3')
        done()
      }, 100)
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const cache1 = getSmartCache('test')
      const cache2 = getSmartCache('test')
      expect(cache1).toBe(cache2)
    })

    it('should return different instances for different names', () => {
      const cache1 = getSmartCache('test1')
      const cache2 = getSmartCache('test2')
      expect(cache1).not.toBe(cache2)
    })
  })
})


