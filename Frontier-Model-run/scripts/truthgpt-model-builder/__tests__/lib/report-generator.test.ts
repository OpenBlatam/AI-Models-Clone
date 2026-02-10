/**
 * Unit Tests - Report Generator
 */

import { ReportGenerator, getReportGenerator } from '@/lib/report-generator'

describe('ReportGenerator', () => {
  let generator: ReportGenerator

  const mockModels = [
    {
      modelId: 'model-1',
      modelName: 'test-1',
      description: 'test',
      status: 'completed' as const,
      duration: 5000,
      startTime: Date.now() - 10000,
      endTime: Date.now() - 5000,
    },
    {
      modelId: 'model-2',
      modelName: 'test-2',
      description: 'test',
      status: 'failed' as const,
      error: 'Test error',
      startTime: Date.now() - 5000,
      endTime: Date.now(),
    },
  ]

  beforeEach(() => {
    generator = new ReportGenerator()
  })

  describe('Report Generation', () => {
    it('should generate JSON report', async () => {
      const report = await generator.generateReport(mockModels, { format: 'json' })
      expect(report).toBeDefined()
      expect(typeof report).toBe('string')

      const parsed = JSON.parse(report)
      expect(parsed).toHaveProperty('summary')
      expect(parsed).toHaveProperty('models')
    })

    it('should generate CSV report', async () => {
      const report = await generator.generateReport(mockModels, { format: 'csv' })
      expect(report).toBeDefined()
      expect(report).toContain('Model ID')
      expect(report).toContain('Model Name')
      expect(report).toContain('Status')
    })

    it('should generate HTML report', async () => {
      const report = await generator.generateReport(mockModels, { format: 'html' })
      expect(report).toBeDefined()
      expect(report).toContain('<html>')
      expect(report).toContain('<table>')
    })

    it('should generate Markdown report', async () => {
      const report = await generator.generateReport(mockModels, { format: 'markdown' })
      expect(report).toBeDefined()
      expect(report).toContain('#')
      expect(report).toContain('|')
    })

    it('should generate YAML report', async () => {
      const report = await generator.generateReport(mockModels, { format: 'yaml' })
      expect(report).toBeDefined()
      expect(report).toContain('models:')
      expect(report).toContain('summary:')
    })

    it('should generate PDF report', async () => {
      const report = await generator.generateReport(mockModels, { format: 'pdf' })
      expect(report).toBeDefined()
      // PDF is binary, so we just check it exists
      expect(report.length).toBeGreaterThan(0)
    })
  })

  describe('Report Summary', () => {
    it('should include summary statistics', async () => {
      const report = await generator.generateReport(mockModels, { format: 'json' })
      const parsed = JSON.parse(report)

      expect(parsed.summary).toHaveProperty('total')
      expect(parsed.summary).toHaveProperty('completed')
      expect(parsed.summary).toHaveProperty('failed')
      expect(parsed.summary).toHaveProperty('successRate')
    })

    it('should calculate correct statistics', async () => {
      const report = await generator.generateReport(mockModels, { format: 'json' })
      const parsed = JSON.parse(report)

      expect(parsed.summary.total).toBe(2)
      expect(parsed.summary.completed).toBe(1)
      expect(parsed.summary.failed).toBe(1)
      expect(parsed.summary.successRate).toBe(0.5)
    })
  })

  describe('Report Customization', () => {
    it('should include custom fields', async () => {
      const report = await generator.generateReport(mockModels, {
        format: 'json',
        includeFields: ['modelId', 'modelName'],
      })

      const parsed = JSON.parse(report)
      expect(parsed.models[0]).toHaveProperty('modelId')
      expect(parsed.models[0]).toHaveProperty('modelName')
    })

    it('should filter models', async () => {
      const report = await generator.generateReport(mockModels, {
        format: 'json',
        filter: (model) => model.status === 'completed',
      })

      const parsed = JSON.parse(report)
      expect(parsed.models).toHaveLength(1)
      expect(parsed.models[0].status).toBe('completed')
    })
  })

  describe('Report Download', () => {
    it('should trigger download', () => {
      const blob = new Blob(['test'], { type: 'text/plain' })
      
      // Mock download
      const mockClick = jest.fn()
      global.document.createElement = jest.fn(() => ({
        href: '',
        download: '',
        click: mockClick,
      })) as any

      generator.downloadReport(blob, 'test.txt')
      expect(mockClick).toHaveBeenCalled()
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const g1 = getReportGenerator()
      const g2 = getReportGenerator()
      expect(g1).toBe(g2)
    })
  })
})










