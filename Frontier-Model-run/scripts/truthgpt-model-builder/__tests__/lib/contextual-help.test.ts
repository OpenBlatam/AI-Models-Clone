/**
 * Unit Tests - Contextual Help
 */

import { ContextualHelp, getContextualHelp } from '@/lib/contextual-help'

describe('ContextualHelp', () => {
  let help: ContextualHelp

  beforeEach(() => {
    help = new ContextualHelp()
  })

  afterEach(() => {
    help.clear()
  })

  describe('Topic Management', () => {
    it('should add topic', () => {
      help.addTopic({
        id: 'test-topic',
        title: 'Test Topic',
        content: 'Test content',
        category: 'general',
        tags: ['test'],
      })

      const topic = help.getTopic('test-topic')
      expect(topic).toBeDefined()
      expect(topic?.title).toBe('Test Topic')
    })

    it('should get all topics', () => {
      help.addTopic({
        id: 'topic1',
        title: 'Topic 1',
        content: 'Content 1',
        category: 'general',
        tags: [],
      })

      help.addTopic({
        id: 'topic2',
        title: 'Topic 2',
        content: 'Content 2',
        category: 'features',
        tags: [],
      })

      const topics = help.getAllTopics()
      expect(topics).toHaveLength(2)
    })

    it('should get topics by category', () => {
      help.addTopic({
        id: 'topic1',
        title: 'Topic 1',
        content: 'Content 1',
        category: 'general',
        tags: [],
      })

      help.addTopic({
        id: 'topic2',
        title: 'Topic 2',
        content: 'Content 2',
        category: 'features',
        tags: [],
      })

      const generalTopics = help.getTopicsByCategory('general')
      expect(generalTopics).toHaveLength(1)
      expect(generalTopics[0].category).toBe('general')
    })
  })

  describe('Context Search', () => {
    it('should search by context component', () => {
      help.addTopic({
        id: 'topic1',
        title: 'Topic 1',
        content: 'Content 1',
        category: 'general',
        tags: ['proactive-builder'],
      })

      help.addTopic({
        id: 'topic2',
        title: 'Topic 2',
        content: 'Content 2',
        category: 'features',
        tags: ['other'],
      })

      const results = help.searchByContext({ component: 'proactive-builder' })
      expect(results.length).toBeGreaterThan(0)
      expect(results[0].tags).toContain('proactive-builder')
    })

    it('should score by relevance', () => {
      help.addTopic({
        id: 'topic1',
        title: 'Topic 1',
        content: 'Content 1',
        category: 'proactive-builder',
        tags: ['proactive-builder', 'builder'],
      })

      help.addTopic({
        id: 'topic2',
        title: 'Topic 2',
        content: 'Content 2',
        category: 'general',
        tags: ['other'],
      })

      const results = help.searchByContext({ component: 'proactive-builder' })
      // Topic1 should have higher relevance
      expect(results[0].id).toBe('topic1')
    })
  })

  describe('Search', () => {
    it('should search topics by query', () => {
      help.addTopic({
        id: 'topic1',
        title: 'Getting Started',
        content: 'How to get started with the builder',
        category: 'general',
        tags: [],
      })

      const results = help.searchTopics('getting started')
      expect(results.length).toBeGreaterThan(0)
      expect(results[0].title.toLowerCase()).toContain('getting')
    })

    it('should search by content', () => {
      help.addTopic({
        id: 'topic1',
        title: 'Test',
        content: 'This topic explains batch mode',
        category: 'general',
        tags: [],
      })

      const results = help.searchTopics('batch mode')
      expect(results.length).toBeGreaterThan(0)
    })

    it('should search by tags', () => {
      help.addTopic({
        id: 'topic1',
        title: 'Test',
        content: 'Content',
        category: 'general',
        tags: ['classification', 'nlp'],
      })

      const results = help.searchTopics('classification')
      expect(results.length).toBeGreaterThan(0)
    })
  })

  describe('Related Topics', () => {
    it('should get related topics', () => {
      help.addTopic({
        id: 'topic1',
        title: 'Topic 1',
        content: 'Content 1',
        category: 'general',
        tags: [],
        relatedTopics: ['topic2'],
      })

      help.addTopic({
        id: 'topic2',
        title: 'Topic 2',
        content: 'Content 2',
        category: 'general',
        tags: [],
      })

      const related = help.getRelatedTopics('topic1')
      expect(related).toHaveLength(1)
      expect(related[0].id).toBe('topic2')
    })
  })

  describe('View History', () => {
    it('should record view', () => {
      help.addTopic({
        id: 'topic1',
        title: 'Topic 1',
        content: 'Content 1',
        category: 'general',
        tags: [],
      })

      help.recordView('topic1')
      // Should record view (no direct way to verify, but should not error)
    })

    it('should get most viewed topics', () => {
      help.addTopic({
        id: 'topic1',
        title: 'Topic 1',
        content: 'Content 1',
        category: 'general',
        tags: [],
      })

      help.addTopic({
        id: 'topic2',
        title: 'Topic 2',
        content: 'Content 2',
        category: 'general',
        tags: [],
      })

      help.recordView('topic1')
      help.recordView('topic1')
      help.recordView('topic2')

      const mostViewed = help.getMostViewedTopics(1)
      expect(mostViewed.length).toBeGreaterThan(0)
      expect(mostViewed[0].id).toBe('topic1')
    })
  })

  describe('Default Topics', () => {
    it('should initialize default topics', () => {
      const helpWithDefaults = getContextualHelp()
      const topics = helpWithDefaults.getAllTopics()
      expect(topics.length).toBeGreaterThan(0)
    })
  })

  describe('Categories', () => {
    it('should get all categories', () => {
      help.addTopic({
        id: 'topic1',
        title: 'Topic 1',
        content: 'Content 1',
        category: 'general',
        tags: [],
      })

      help.addTopic({
        id: 'topic2',
        title: 'Topic 2',
        content: 'Content 2',
        category: 'features',
        tags: [],
      })

      const categories = help.getCategories()
      expect(categories).toContain('general')
      expect(categories).toContain('features')
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const h1 = getContextualHelp()
      const h2 = getContextualHelp()
      expect(h1).toBe(h2)
    })
  })
})










