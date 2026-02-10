/**
 * Unit Tests - Custom Templates
 */

import { CustomTemplates, getCustomTemplates } from '@/lib/custom-templates'

describe('CustomTemplates', () => {
  let templates: CustomTemplates

  beforeEach(() => {
    templates = new CustomTemplates()
    if (typeof window !== 'undefined') {
      localStorage.clear()
    }
  })

  afterEach(() => {
    templates.clear()
  })

  describe('Template Management', () => {
    it('should create template', () => {
      const template = templates.createTemplate({
        name: 'Test Template',
        description: 'Test description',
        category: 'classification',
        example: 'classification model',
        spec: {
          parameters: {
            learningRate: 0.001,
            batchSize: 32,
          },
        },
      })

      expect(template).toBeDefined()
      expect(template.id).toBeDefined()
      expect(template.name).toBe('Test Template')
    })

    it('should get template by ID', () => {
      const template = templates.createTemplate({
        name: 'Test Template',
        description: 'Test',
        category: 'classification',
        example: 'test',
        spec: {},
      })

      const retrieved = templates.getTemplate(template.id)
      expect(retrieved).toBeDefined()
      expect(retrieved?.name).toBe('Test Template')
    })

    it('should get all templates', () => {
      templates.createTemplate({
        name: 'Template 1',
        description: 'Test',
        category: 'classification',
        example: 'test',
        spec: {},
      })

      templates.createTemplate({
        name: 'Template 2',
        description: 'Test',
        category: 'regression',
        example: 'test',
        spec: {},
      })

      const allTemplates = templates.getAllTemplates()
      expect(allTemplates.length).toBe(2)
    })

    it('should update template', () => {
      const template = templates.createTemplate({
        name: 'Test Template',
        description: 'Test',
        category: 'classification',
        example: 'test',
        spec: {},
      })

      const updated = templates.updateTemplate(template.id, {
        name: 'Updated Template',
      })

      expect(updated?.name).toBe('Updated Template')
    })

    it('should delete template', () => {
      const template = templates.createTemplate({
        name: 'Test Template',
        description: 'Test',
        category: 'classification',
        example: 'test',
        spec: {},
      })

      templates.deleteTemplate(template.id)
      const retrieved = templates.getTemplate(template.id)
      expect(retrieved).toBeUndefined()
    })
  })

  describe('Search', () => {
    it('should search templates by name', () => {
      templates.createTemplate({
        name: 'Classification Template',
        description: 'Test',
        category: 'classification',
        example: 'test',
        spec: {},
      })

      templates.createTemplate({
        name: 'Regression Template',
        description: 'Test',
        category: 'regression',
        example: 'test',
        spec: {},
      })

      const results = templates.searchTemplates('Classification')
      expect(results.length).toBeGreaterThan(0)
      expect(results[0].name).toContain('Classification')
    })

    it('should search templates by category', () => {
      templates.createTemplate({
        name: 'Template 1',
        description: 'Test',
        category: 'classification',
        example: 'test',
        spec: {},
      })

      templates.createTemplate({
        name: 'Template 2',
        description: 'Test',
        category: 'regression',
        example: 'test',
        spec: {},
      })

      const results = templates.searchTemplates('classification')
      expect(results.some(t => t.category === 'classification')).toBe(true)
    })

    it('should search templates by description', () => {
      templates.createTemplate({
        name: 'Template 1',
        description: 'Classification model for text',
        category: 'classification',
        example: 'test',
        spec: {},
      })

      const results = templates.searchTemplates('text')
      expect(results.length).toBeGreaterThan(0)
    })
  })

  describe('Categories', () => {
    it('should get templates by category', () => {
      templates.createTemplate({
        name: 'Template 1',
        description: 'Test',
        category: 'classification',
        example: 'test',
        spec: {},
      })

      templates.createTemplate({
        name: 'Template 2',
        description: 'Test',
        category: 'regression',
        example: 'test',
        spec: {},
      })

      const classification = templates.getTemplatesByCategory('classification')
      expect(classification.length).toBe(1)
      expect(classification[0].category).toBe('classification')
    })

    it('should get all categories', () => {
      templates.createTemplate({
        name: 'Template 1',
        description: 'Test',
        category: 'classification',
        example: 'test',
        spec: {},
      })

      templates.createTemplate({
        name: 'Template 2',
        description: 'Test',
        category: 'regression',
        example: 'test',
        spec: {},
      })

      const categories = templates.getCategories()
      expect(categories).toContain('classification')
      expect(categories).toContain('regression')
    })
  })

  describe('Import/Export', () => {
    it('should export templates', () => {
      templates.createTemplate({
        name: 'Template 1',
        description: 'Test',
        category: 'classification',
        example: 'test',
        spec: {},
      })

      const exported = templates.exportTemplates()
      expect(typeof exported).toBe('string')
      const parsed = JSON.parse(exported)
      expect(parsed.length).toBeGreaterThan(0)
    })

    it('should import templates', () => {
      const templateData = {
        name: 'Imported Template',
        description: 'Test',
        category: 'classification',
        example: 'test',
        spec: {},
      }

      const imported = templates.importTemplate(templateData)
      expect(imported).toBeDefined()
      expect(imported.name).toBe('Imported Template')
    })

    it('should import multiple templates', () => {
      const templatesData = [
        {
          name: 'Template 1',
          description: 'Test',
          category: 'classification',
          example: 'test',
          spec: {},
        },
        {
          name: 'Template 2',
          description: 'Test',
          category: 'regression',
          example: 'test',
          spec: {},
        },
      ]

      const imported = templates.importTemplates(templatesData)
      expect(imported.length).toBe(2)
    })
  })

  describe('Persistence', () => {
    it('should save templates to localStorage', () => {
      templates.createTemplate({
        name: 'Test Template',
        description: 'Test',
        category: 'classification',
        example: 'test',
        spec: {},
      })

      // Templates should be saved automatically
      expect(templates.getAllTemplates().length).toBeGreaterThan(0)
    })

    it('should load templates from localStorage', () => {
      templates.createTemplate({
        name: 'Test Template',
        description: 'Test',
        category: 'classification',
        example: 'test',
        spec: {},
      })

      // Create new instance (should load from localStorage)
      const newTemplates = new CustomTemplates()
      const loaded = newTemplates.getAllTemplates()
      expect(loaded.length).toBeGreaterThan(0)
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const t1 = getCustomTemplates()
      const t2 = getCustomTemplates()
      expect(t1).toBe(t2)
    })
  })
})










