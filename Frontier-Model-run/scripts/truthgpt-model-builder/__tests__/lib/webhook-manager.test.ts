/**
 * Unit Tests - Webhook Manager
 */

import { WebhookManager, getWebhookManager } from '@/lib/webhook-manager'

// Mock fetch
global.fetch = jest.fn()

describe('WebhookManager', () => {
  let webhookManager: WebhookManager

  beforeEach(() => {
    webhookManager = new WebhookManager()
    jest.clearAllMocks()
  })

  afterEach(() => {
    webhookManager.clear()
  })

  describe('Webhook Management', () => {
    it('should add webhook', () => {
      webhookManager.addWebhook({
        url: 'https://example.com/webhook',
        events: ['model.completed'],
      })

      const webhooks = webhookManager.getWebhooks()
      expect(webhooks.length).toBe(1)
      expect(webhooks[0].url).toBe('https://example.com/webhook')
    })

    it('should remove webhook', () => {
      const id = webhookManager.addWebhook({
        url: 'https://example.com/webhook',
        events: ['model.completed'],
      })

      webhookManager.removeWebhook(id)
      const webhooks = webhookManager.getWebhooks()
      expect(webhooks.length).toBe(0)
    })

    it('should get webhook by ID', () => {
      const id = webhookManager.addWebhook({
        url: 'https://example.com/webhook',
        events: ['model.completed'],
      })

      const webhook = webhookManager.getWebhook(id)
      expect(webhook).toBeDefined()
      expect(webhook?.url).toBe('https://example.com/webhook')
    })
  })

  describe('Event Triggering', () => {
    it('should trigger webhook for matching event', async () => {
      const mockFetch = global.fetch as jest.Mock
      mockFetch.mockResolvedValueOnce({ ok: true, status: 200 })

      webhookManager.addWebhook({
        url: 'https://example.com/webhook',
        events: ['model.completed'],
      })

      await webhookManager.triggerWebhook('model.completed', {
        modelId: 'model-1',
        status: 'completed',
      })

      expect(mockFetch).toHaveBeenCalledTimes(1)
      expect(mockFetch).toHaveBeenCalledWith(
        'https://example.com/webhook',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      )
    })

    it('should not trigger webhook for non-matching event', async () => {
      const mockFetch = global.fetch as jest.Mock

      webhookManager.addWebhook({
        url: 'https://example.com/webhook',
        events: ['model.completed'],
      })

      await webhookManager.triggerWebhook('model.failed', {})

      expect(mockFetch).not.toHaveBeenCalled()
    })

    it('should trigger multiple webhooks', async () => {
      const mockFetch = global.fetch as jest.Mock
      mockFetch.mockResolvedValue({ ok: true, status: 200 })

      webhookManager.addWebhook({
        url: 'https://example.com/webhook1',
        events: ['model.completed'],
      })

      webhookManager.addWebhook({
        url: 'https://example.com/webhook2',
        events: ['model.completed'],
      })

      await webhookManager.triggerWebhook('model.completed', {})

      expect(mockFetch).toHaveBeenCalledTimes(2)
    })

    it('should include payload in request', async () => {
      const mockFetch = global.fetch as jest.Mock
      mockFetch.mockResolvedValueOnce({ ok: true, status: 200 })

      webhookManager.addWebhook({
        url: 'https://example.com/webhook',
        events: ['model.completed'],
      })

      const payload = { modelId: 'model-1', status: 'completed' }
      await webhookManager.triggerWebhook('model.completed', payload)

      expect(mockFetch).toHaveBeenCalledWith(
        'https://example.com/webhook',
        expect.objectContaining({
          body: JSON.stringify(payload),
        })
      )
    })
  })

  describe('Retry Logic', () => {
    it('should retry on failure', async () => {
      const mockFetch = global.fetch as jest.Mock
      mockFetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({ ok: true, status: 200 })

      webhookManager.addWebhook({
        url: 'https://example.com/webhook',
        events: ['model.completed'],
        retries: 2,
      })

      await webhookManager.triggerWebhook('model.completed', {})

      expect(mockFetch).toHaveBeenCalledTimes(2)
    })

    it('should respect max retries', async () => {
      const mockFetch = global.fetch as jest.Mock
      mockFetch.mockRejectedValue(new Error('Network error'))

      webhookManager.addWebhook({
        url: 'https://example.com/webhook',
        events: ['model.completed'],
        retries: 2,
      })

      await webhookManager.triggerWebhook('model.completed', {})

      expect(mockFetch).toHaveBeenCalledTimes(3) // 1 initial + 2 retries
    })
  })

  describe('Security', () => {
    it('should include secret in headers', async () => {
      const mockFetch = global.fetch as jest.Mock
      mockFetch.mockResolvedValueOnce({ ok: true, status: 200 })

      webhookManager.addWebhook({
        url: 'https://example.com/webhook',
        events: ['model.completed'],
        secret: 'test-secret',
      })

      await webhookManager.triggerWebhook('model.completed', {})

      expect(mockFetch).toHaveBeenCalledWith(
        'https://example.com/webhook',
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-Webhook-Secret': 'test-secret',
          }),
        })
      )
    })
  })

  describe('Timeout', () => {
    it('should timeout after specified duration', async () => {
      const mockFetch = global.fetch as jest.Mock
      mockFetch.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 2000))
      )

      webhookManager.addWebhook({
        url: 'https://example.com/webhook',
        events: ['model.completed'],
        timeout: 1000,
      })

      await webhookManager.triggerWebhook('model.completed', {})

      // Should handle timeout
      expect(mockFetch).toHaveBeenCalled()
    })
  })

  describe('Statistics', () => {
    it('should track webhook statistics', async () => {
      const mockFetch = global.fetch as jest.Mock
      mockFetch.mockResolvedValue({ ok: true, status: 200 })

      const id = webhookManager.addWebhook({
        url: 'https://example.com/webhook',
        events: ['model.completed'],
      })

      await webhookManager.triggerWebhook('model.completed', {})
      await webhookManager.triggerWebhook('model.completed', {})

      const webhook = webhookManager.getWebhook(id)
      expect(webhook?.stats).toBeDefined()
      expect(webhook?.stats.successCount).toBeGreaterThan(0)
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const w1 = getWebhookManager()
      const w2 = getWebhookManager()
      expect(w1).toBe(w2)
    })
  })
})










