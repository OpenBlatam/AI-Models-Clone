/**
 * Unit Tests - Model Exporter
 */

import { ModelExporter, getModelExporter } from '@/lib/modules/management'

describe('ModelExporter', () => {
  let exporter: ModelExporter

  const mockModels = [
    {
      modelId: 'model-1',
      modelName: 'test-model-1',
      description: 'Test model 1',
      status: 'completed' as const,
      duration: 5000,
      startTime: Date.now(),
      endTime: Date.now(),
    },
    {
      modelId: 'model-2',
      modelName: 'test-model-2',
      description: 'Test model 2',
      status: 'failed' as const,
      error: 'Test error',
      startTime: Date.now(),
      endTime: Date.now(),
    },
  ]

  beforeEach(() => {
    exporter = new ModelExporter()
  })

  describe('JSON Export', () => {
    it('should export as JSON', async () => {
      const blob = await exporter.exportModels(mockModels, { format: 'json' })
      
      expect(blob).toBeInstanceOf(Blob)
      expect(blob.type).toBe('application/json')
    })

    it('should include all model data in JSON', async () => {
      const blob = await exporter.exportModels(mockModels, { format: 'json' })
      const text = await blob.text()
      const data = JSON.parse(text)

      expect(data).toHaveLength(2)
      expect(data[0].modelId).toBe('model-1')
      expect(data[0].modelName).toBe('test-model-1')
    })
  })

  describe('CSV Export', () => {
    it('should export as CSV', async () => {
      const blob = await exporter.exportModels(mockModels, { format: 'csv' })
      
      expect(blob).toBeInstanceOf(Blob)
      expect(blob.type).toBe('text/csv')
    })

    it('should include headers in CSV', async () => {
      const blob = await exporter.exportModels(mockModels, { format: 'csv' })
      const text = await blob.text()

      expect(text).toContain('Model ID')
      expect(text).toContain('Model Name')
      expect(text).toContain('Status')
    })

    it('should include model data in CSV', async () => {
      const blob = await exporter.exportModels(mockModels, { format: 'csv' })
      const text = await blob.text()

      expect(text).toContain('model-1')
      expect(text).toContain('test-model-1')
      expect(text).toContain('completed')
    })
  })

  describe('YAML Export', () => {
    it('should export as YAML', async () => {
      const blob = await exporter.exportModels(mockModels, { format: 'yaml' })
      
      expect(blob).toBeInstanceOf(Blob)
      expect(blob.type).toBe('text/yaml')
    })

    it('should include model data in YAML', async () => {
      const blob = await exporter.exportModels(mockModels, { format: 'yaml' })
      const text = await blob.text()

      expect(text).toContain('modelId:')
      expect(text).toContain('modelName:')
      expect(text).toContain('status:')
    })
  })

  describe('Markdown Export', () => {
    it('should export as Markdown', async () => {
      const blob = await exporter.exportModels(mockModels, { format: 'markdown' })
      
      expect(blob).toBeInstanceOf(Blob)
      expect(blob.type).toBe('text/markdown')
    })

    it('should include table in Markdown', async () => {
      const blob = await exporter.exportModels(mockModels, { format: 'markdown' })
      const text = await blob.text()

      expect(text).toContain('# Modelos Exportados')
      expect(text).toContain('| Model ID |')
      expect(text).toContain('| Name |')
    })
  })

  describe('HTML Export', () => {
    it('should export as HTML', async () => {
      const blob = await exporter.exportModels(mockModels, { format: 'html' })
      
      expect(blob).toBeInstanceOf(Blob)
      expect(blob.type).toBe('text/html')
    })

    it('should include table in HTML', async () => {
      const blob = await exporter.exportModels(mockModels, { format: 'html' })
      const text = await blob.text()

      expect(text).toContain('<table>')
      expect(text).toContain('<th>')
      expect(text).toContain('<td>')
    })
  })

  describe('Filtering', () => {
    it('should filter models before export', async () => {
      const blob = await exporter.exportModels(mockModels, {
        format: 'json',
        filter: (model) => model.status === 'completed',
      })

      const text = await blob.text()
      const data = JSON.parse(text)

      expect(data).toHaveLength(1)
      expect(data[0].status).toBe('completed')
    })
  })

  describe('Download', () => {
    it('should download file', () => {
      const blob = new Blob(['test'], { type: 'text/plain' })
      
      // Mock createElement and click
      const mockClick = jest.fn()
      const mockAppendChild = jest.fn()
      const mockRemoveChild = jest.fn()
      
      global.document.createElement = jest.fn(() => ({
        href: '',
        download: '',
        click: mockClick,
      })) as any

      global.document.body.appendChild = mockAppendChild as any
      global.document.body.removeChild = mockRemoveChild as any

      exporter.downloadFile(blob, 'test.txt')

      expect(mockClick).toHaveBeenCalled()
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const e1 = getModelExporter()
      const e2 = getModelExporter()
      expect(e1).toBe(e2)
    })
  })
})










