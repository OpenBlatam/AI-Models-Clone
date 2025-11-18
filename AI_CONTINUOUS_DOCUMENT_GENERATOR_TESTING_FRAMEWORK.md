# AI Continuous Document Generator - Framework de Testing Completo

## 1. Estrategia de Testing

### 1.1 Pirámide de Testing
```
┌─────────────────────────────────────┐
│           E2E Tests (10%)           │
├─────────────────────────────────────┤
│        Integration Tests (20%)      │
├─────────────────────────────────────┤
│         Unit Tests (70%)            │
└─────────────────────────────────────┘
```

### 1.2 Tipos de Testing
- **Unit Tests**: Funciones y componentes individuales
- **Integration Tests**: Interacción entre módulos
- **E2E Tests**: Flujos completos de usuario
- **Performance Tests**: Rendimiento y carga
- **Security Tests**: Vulnerabilidades y seguridad
- **Visual Regression Tests**: Cambios en UI
- **API Tests**: Endpoints y contratos
- **Database Tests**: Operaciones de base de datos

## 2. Configuración del Framework

### 2.1 Dependencias de Testing
```json
{
  "devDependencies": {
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^5.16.5",
    "@testing-library/user-event": "^14.4.3",
    "jest": "^29.5.0",
    "jest-environment-jsdom": "^29.5.0",
    "supertest": "^6.3.3",
    "cypress": "^12.10.0",
    "playwright": "^1.35.0",
    "k6": "^0.45.0",
    "artillery": "^2.0.0",
    "mocha": "^10.2.0",
    "chai": "^4.3.7",
    "sinon": "^15.2.0",
    "nock": "^13.3.0",
    "faker": "^6.6.6",
    "factory-girl": "^5.0.4"
  }
}
```

### 2.2 Configuración de Jest
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@components/(.*)$': '<rootDir>/src/components/$1',
    '^@services/(.*)$': '<rootDir>/src/services/$1',
    '^@utils/(.*)$': '<rootDir>/src/utils/$1'
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
    '!src/reportWebVitals.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{test,spec}.{js,jsx,ts,tsx}'
  ],
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest'
  }
};
```

### 2.3 Setup de Testing
```javascript
// src/setupTests.js
import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';
import { server } from './mocks/server';

// Configurar testing library
configure({ testIdAttribute: 'data-testid' });

// Setup MSW para mocking de APIs
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Mock de WebSocket
global.WebSocket = class WebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = 1;
    this.onopen = null;
    this.onmessage = null;
    this.onclose = null;
    this.onerror = null;
  }
  
  send(data) {
    // Mock implementation
  }
  
  close() {
    this.readyState = 3;
  }
};

// Mock de localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock de fetch
global.fetch = jest.fn();
```

## 3. Tests Unitarios

### 3.1 Tests de Servicios
```javascript
// src/services/__tests__/DocumentService.test.js
import { DocumentService } from '../DocumentService';
import { Document } from '../../models/Document';
import { AIService } from '../AIService';

// Mock de dependencias
jest.mock('../../models/Document');
jest.mock('../AIService');

describe('DocumentService', () => {
  let documentService;
  let mockDocument;
  let mockAIService;

  beforeEach(() => {
    mockDocument = {
      create: jest.fn(),
      findById: jest.fn(),
      findByIdAndUpdate: jest.fn(),
      find: jest.fn(),
      deleteOne: jest.fn()
    };
    
    mockAIService = {
      generateContent: jest.fn()
    };
    
    Document.mockImplementation(() => mockDocument);
    AIService.mockImplementation(() => mockAIService);
    
    documentService = new DocumentService();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('createDocument', () => {
    it('should create a new document successfully', async () => {
      const documentData = {
        title: 'Test Document',
        content: 'Test content',
        userId: 'user123'
      };

      const expectedDocument = {
        id: 'doc123',
        ...documentData,
        createdAt: new Date()
      };

      mockDocument.create.mockResolvedValue(expectedDocument);

      const result = await documentService.createDocument(documentData);

      expect(mockDocument.create).toHaveBeenCalledWith(documentData);
      expect(result).toEqual(expectedDocument);
    });

    it('should throw error when document creation fails', async () => {
      const documentData = {
        title: 'Test Document',
        content: 'Test content',
        userId: 'user123'
      };

      mockDocument.create.mockRejectedValue(new Error('Database error'));

      await expect(documentService.createDocument(documentData))
        .rejects.toThrow('Database error');
    });
  });

  describe('generateContent', () => {
    it('should generate content using AI service', async () => {
      const documentId = 'doc123';
      const prompt = 'Generate a summary';
      const expectedContent = 'Generated summary content';

      mockDocument.findById.mockResolvedValue({
        id: documentId,
        content: 'Original content'
      });

      mockAIService.generateContent.mockResolvedValue(expectedContent);
      mockDocument.findByIdAndUpdate.mockResolvedValue({
        id: documentId,
        content: expectedContent
      });

      const result = await documentService.generateContent(documentId, prompt);

      expect(mockAIService.generateContent).toHaveBeenCalledWith({
        prompt,
        context: 'Original content'
      });
      expect(result.content).toBe(expectedContent);
    });

    it('should handle AI service errors gracefully', async () => {
      const documentId = 'doc123';
      const prompt = 'Generate a summary';

      mockDocument.findById.mockResolvedValue({
        id: documentId,
        content: 'Original content'
      });

      mockAIService.generateContent.mockRejectedValue(new Error('AI service error'));

      await expect(documentService.generateContent(documentId, prompt))
        .rejects.toThrow('AI service error');
    });
  });

  describe('getDocuments', () => {
    it('should return paginated documents', async () => {
      const userId = 'user123';
      const options = { page: 1, limit: 10 };
      const mockDocuments = [
        { id: 'doc1', title: 'Document 1' },
        { id: 'doc2', title: 'Document 2' }
      ];

      mockDocument.find.mockReturnValue({
        sort: jest.fn().mockReturnValue({
          skip: jest.fn().mockReturnValue({
            limit: jest.fn().mockReturnValue({
              exec: jest.fn().mockResolvedValue(mockDocuments)
            })
          })
        })
      });

      const result = await documentService.getDocuments(userId, options);

      expect(result.documents).toEqual(mockDocuments);
      expect(result.pagination.page).toBe(1);
      expect(result.pagination.limit).toBe(10);
    });
  });
});
```

### 3.2 Tests de Componentes React
```javascript
// src/components/__tests__/DocumentEditor.test.jsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DocumentEditor } from '../DocumentEditor';
import { useDocument } from '../../hooks/useDocument';
import { useCollaboration } from '../../hooks/useCollaboration';

// Mock de hooks
jest.mock('../../hooks/useDocument');
jest.mock('../../hooks/useCollaboration');

describe('DocumentEditor', () => {
  const mockDocument = {
    id: 'doc123',
    title: 'Test Document',
    content: 'Initial content',
    status: 'draft'
  };

  const mockCollaborators = [
    { id: 'user1', name: 'John Doe', color: '#FF5733' },
    { id: 'user2', name: 'Jane Smith', color: '#33FF57' }
  ];

  beforeEach(() => {
    useDocument.mockReturnValue({
      document: mockDocument,
      updateContent: jest.fn(),
      loading: false,
      error: null
    });

    useCollaboration.mockReturnValue({
      collaborators: mockCollaborators,
      isConnected: true,
      sendChange: jest.fn()
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should render document editor with initial content', () => {
    render(<DocumentEditor documentId="doc123" />);

    expect(screen.getByDisplayValue('Test Document')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Initial content')).toBeInTheDocument();
  });

  it('should update content when user types', async () => {
    const user = userEvent.setup();
    const mockUpdateContent = jest.fn();
    
    useDocument.mockReturnValue({
      document: mockDocument,
      updateContent: mockUpdateContent,
      loading: false,
      error: null
    });

    render(<DocumentEditor documentId="doc123" />);

    const contentTextarea = screen.getByDisplayValue('Initial content');
    await user.clear(contentTextarea);
    await user.type(contentTextarea, 'Updated content');

    expect(mockUpdateContent).toHaveBeenCalledWith('Updated content');
  });

  it('should display collaborators', () => {
    render(<DocumentEditor documentId="doc123" />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
  });

  it('should show connection status', () => {
    render(<DocumentEditor documentId="doc123" />);

    expect(screen.getByText('Conectado')).toBeInTheDocument();
  });

  it('should handle loading state', () => {
    useDocument.mockReturnValue({
      document: null,
      updateContent: jest.fn(),
      loading: true,
      error: null
    });

    render(<DocumentEditor documentId="doc123" />);

    expect(screen.getByText('Cargando documento...')).toBeInTheDocument();
  });

  it('should handle error state', () => {
    useDocument.mockReturnValue({
      document: null,
      updateContent: jest.fn(),
      loading: false,
      error: 'Error loading document'
    });

    render(<DocumentEditor documentId="doc123" />);

    expect(screen.getByText('Error loading document')).toBeInTheDocument();
  });
});
```

### 3.3 Tests de Hooks Personalizados
```javascript
// src/hooks/__tests__/useDocument.test.js
import { renderHook, act } from '@testing-library/react';
import { useDocument } from '../useDocument';
import { DocumentService } from '../../services/DocumentService';

jest.mock('../../services/DocumentService');

describe('useDocument', () => {
  let mockDocumentService;

  beforeEach(() => {
    mockDocumentService = {
      getDocument: jest.fn(),
      updateDocument: jest.fn(),
      deleteDocument: jest.fn()
    };
    
    DocumentService.mockImplementation(() => mockDocumentService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should fetch document on mount', async () => {
    const mockDocument = {
      id: 'doc123',
      title: 'Test Document',
      content: 'Test content'
    };

    mockDocumentService.getDocument.mockResolvedValue(mockDocument);

    const { result } = renderHook(() => useDocument('doc123'));

    expect(result.current.loading).toBe(true);

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.document).toEqual(mockDocument);
    expect(result.current.loading).toBe(false);
    expect(mockDocumentService.getDocument).toHaveBeenCalledWith('doc123');
  });

  it('should handle document update', async () => {
    const mockDocument = {
      id: 'doc123',
      title: 'Test Document',
      content: 'Test content'
    };

    const updatedDocument = {
      ...mockDocument,
      content: 'Updated content'
    };

    mockDocumentService.getDocument.mockResolvedValue(mockDocument);
    mockDocumentService.updateDocument.mockResolvedValue(updatedDocument);

    const { result } = renderHook(() => useDocument('doc123'));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    await act(async () => {
      await result.current.updateContent('Updated content');
    });

    expect(mockDocumentService.updateDocument).toHaveBeenCalledWith('doc123', {
      content: 'Updated content'
    });
    expect(result.current.document).toEqual(updatedDocument);
  });

  it('should handle errors', async () => {
    const error = new Error('Failed to fetch document');
    mockDocumentService.getDocument.mockRejectedValue(error);

    const { result } = renderHook(() => useDocument('doc123'));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.error).toBe('Failed to fetch document');
    expect(result.current.loading).toBe(false);
  });
});
```

## 4. Tests de Integración

### 4.1 API Integration Tests
```javascript
// tests/integration/api.test.js
const request = require('supertest');
const app = require('../../src/app');
const { User, Document } = require('../../src/models');
const { generateAuthToken } = require('../helpers/auth');

describe('API Integration Tests', () => {
  let authToken;
  let userId;
  let documentId;

  beforeAll(async () => {
    // Setup test database
    await setupTestDatabase();
    
    // Create test user
    const user = await User.create({
      email: 'test@example.com',
      password: 'password123',
      firstName: 'Test',
      lastName: 'User'
    });
    
    userId = user.id;
    authToken = generateAuthToken(user);
  });

  afterAll(async () => {
    await cleanupTestDatabase();
  });

  describe('Document API', () => {
    describe('POST /api/documents', () => {
      it('should create a new document', async () => {
        const documentData = {
          title: 'Test Document',
          content: 'Test content',
          template: 'business-report'
        };

        const response = await request(app)
          .post('/api/documents')
          .set('Authorization', `Bearer ${authToken}`)
          .send(documentData)
          .expect(201);

        expect(response.body.success).toBe(true);
        expect(response.body.data.title).toBe(documentData.title);
        expect(response.body.data.userId).toBe(userId);

        documentId = response.body.data.id;
      });

      it('should return 401 without authentication', async () => {
        const documentData = {
          title: 'Test Document',
          content: 'Test content'
        };

        await request(app)
          .post('/api/documents')
          .send(documentData)
          .expect(401);
      });

      it('should validate required fields', async () => {
        const response = await request(app)
          .post('/api/documents')
          .set('Authorization', `Bearer ${authToken}`)
          .send({})
          .expect(400);

        expect(response.body.error).toContain('title is required');
      });
    });

    describe('GET /api/documents/:id', () => {
      it('should get document by id', async () => {
        const response = await request(app)
          .get(`/api/documents/${documentId}`)
          .set('Authorization', `Bearer ${authToken}`)
          .expect(200);

        expect(response.body.success).toBe(true);
        expect(response.body.data.id).toBe(documentId);
        expect(response.body.data.title).toBe('Test Document');
      });

      it('should return 404 for non-existent document', async () => {
        await request(app)
          .get('/api/documents/nonexistent')
          .set('Authorization', `Bearer ${authToken}`)
          .expect(404);
      });
    });

    describe('PUT /api/documents/:id', () => {
      it('should update document', async () => {
        const updateData = {
          title: 'Updated Document',
          content: 'Updated content'
        };

        const response = await request(app)
          .put(`/api/documents/${documentId}`)
          .set('Authorization', `Bearer ${authToken}`)
          .send(updateData)
          .expect(200);

        expect(response.body.success).toBe(true);
        expect(response.body.data.title).toBe(updateData.title);
        expect(response.body.data.content).toBe(updateData.content);
      });
    });

    describe('DELETE /api/documents/:id', () => {
      it('should delete document', async () => {
        await request(app)
          .delete(`/api/documents/${documentId}`)
          .set('Authorization', `Bearer ${authToken}`)
          .expect(200);

        // Verify document is deleted
        await request(app)
          .get(`/api/documents/${documentId}`)
          .set('Authorization', `Bearer ${authToken}`)
          .expect(404);
      });
    });
  });

  describe('AI Generation API', () => {
    beforeEach(async () => {
      // Create a new document for AI tests
      const document = await Document.create({
        title: 'AI Test Document',
        content: 'Initial content',
        userId: userId
      });
      documentId = document.id;
    });

    describe('POST /api/documents/:id/generate', () => {
      it('should generate content using AI', async () => {
        const generateData = {
          prompt: 'Generate a summary',
          template: 'business-report'
        };

        const response = await request(app)
          .post(`/api/documents/${documentId}/generate`)
          .set('Authorization', `Bearer ${authToken}`)
          .send(generateData)
          .expect(200);

        expect(response.body.success).toBe(true);
        expect(response.body.data.generatedContent).toBeDefined();
        expect(response.body.data.metadata.model).toBeDefined();
      });

      it('should handle AI service errors', async () => {
        // Mock AI service to throw error
        jest.spyOn(require('../../src/services/AIService'), 'generateContent')
          .mockRejectedValue(new Error('AI service unavailable'));

        const generateData = {
          prompt: 'Generate a summary'
        };

        const response = await request(app)
          .post(`/api/documents/${documentId}/generate`)
          .set('Authorization', `Bearer ${authToken}`)
          .send(generateData)
          .expect(500);

        expect(response.body.error).toContain('AI service unavailable');
      });
    });
  });
});
```

### 4.2 Database Integration Tests
```javascript
// tests/integration/database.test.js
const { connectDB, disconnectDB } = require('../../src/config/database');
const { User, Document, DocumentVersion } = require('../../src/models');

describe('Database Integration Tests', () => {
  beforeAll(async () => {
    await connectDB();
  });

  afterAll(async () => {
    await disconnectDB();
  });

  beforeEach(async () => {
    // Clean up test data
    await User.deleteMany({});
    await Document.deleteMany({});
    await DocumentVersion.deleteMany({});
  });

  describe('User Model', () => {
    it('should create user with valid data', async () => {
      const userData = {
        email: 'test@example.com',
        password: 'hashedPassword',
        firstName: 'Test',
        lastName: 'User'
      };

      const user = await User.create(userData);

      expect(user.id).toBeDefined();
      expect(user.email).toBe(userData.email);
      expect(user.firstName).toBe(userData.firstName);
      expect(user.lastName).toBe(userData.lastName);
      expect(user.createdAt).toBeDefined();
    });

    it('should not create user with duplicate email', async () => {
      const userData = {
        email: 'test@example.com',
        password: 'hashedPassword',
        firstName: 'Test',
        lastName: 'User'
      };

      await User.create(userData);

      await expect(User.create(userData)).rejects.toThrow();
    });
  });

  describe('Document Model', () => {
    let userId;

    beforeEach(async () => {
      const user = await User.create({
        email: 'test@example.com',
        password: 'hashedPassword',
        firstName: 'Test',
        lastName: 'User'
      });
      userId = user.id;
    });

    it('should create document with valid data', async () => {
      const documentData = {
        title: 'Test Document',
        content: 'Test content',
        userId: userId,
        template: 'business-report'
      };

      const document = await Document.create(documentData);

      expect(document.id).toBeDefined();
      expect(document.title).toBe(documentData.title);
      expect(document.content).toBe(documentData.content);
      expect(document.userId.toString()).toBe(userId);
      expect(document.status).toBe('draft');
    });

    it('should create document version on update', async () => {
      const document = await Document.create({
        title: 'Test Document',
        content: 'Initial content',
        userId: userId
      });

      // Update document
      document.content = 'Updated content';
      await document.save();

      // Check if version was created
      const versions = await DocumentVersion.find({ documentId: document.id });
      expect(versions).toHaveLength(1);
      expect(versions[0].content).toBe('Initial content');
    });
  });

  describe('Document Relationships', () => {
    let userId;
    let documentId;

    beforeEach(async () => {
      const user = await User.create({
        email: 'test@example.com',
        password: 'hashedPassword',
        firstName: 'Test',
        lastName: 'User'
      });
      userId = user.id;

      const document = await Document.create({
        title: 'Test Document',
        content: 'Test content',
        userId: userId
      });
      documentId = document.id;
    });

    it('should populate user in document query', async () => {
      const document = await Document.findById(documentId)
        .populate('userId', 'firstName lastName email');

      expect(document.userId.firstName).toBe('Test');
      expect(document.userId.lastName).toBe('User');
      expect(document.userId.email).toBe('test@example.com');
    });

    it('should cascade delete document versions when document is deleted', async () => {
      // Create document version
      await DocumentVersion.create({
        documentId: documentId,
        versionNumber: 1,
        content: 'Version 1 content',
        createdBy: userId
      });

      // Delete document
      await Document.findByIdAndDelete(documentId);

      // Check if version was deleted
      const versions = await DocumentVersion.find({ documentId: documentId });
      expect(versions).toHaveLength(0);
    });
  });
});
```

## 5. Tests End-to-End (E2E)

### 5.1 Cypress E2E Tests
```javascript
// cypress/e2e/document-creation.cy.js
describe('Document Creation Flow', () => {
  beforeEach(() => {
    // Login before each test
    cy.login('test@example.com', 'password123');
  });

  it('should create a new document successfully', () => {
    cy.visit('/documents');
    
    // Click create document button
    cy.get('[data-testid="create-document-btn"]').click();
    
    // Fill document form
    cy.get('[data-testid="document-title"]').type('My Test Document');
    cy.get('[data-testid="document-template"]').select('business-report');
    cy.get('[data-testid="document-content"]').type('This is the initial content of my document.');
    
    // Submit form
    cy.get('[data-testid="save-document-btn"]').click();
    
    // Verify document was created
    cy.url().should('include', '/documents/');
    cy.get('[data-testid="document-title"]').should('contain', 'My Test Document');
    cy.get('[data-testid="document-content"]').should('contain', 'This is the initial content');
  });

  it('should generate content using AI', () => {
    // Create a document first
    cy.createDocument({
      title: 'AI Test Document',
      content: 'Initial content for AI generation'
    });
    
    // Open AI panel
    cy.get('[data-testid="ai-panel-toggle"]').click();
    
    // Select AI action
    cy.get('[data-testid="ai-action-summary"]').click();
    
    // Wait for AI generation
    cy.get('[data-testid="ai-generating"]').should('be.visible');
    cy.get('[data-testid="ai-generated-content"]', { timeout: 10000 }).should('be.visible');
    
    // Verify generated content
    cy.get('[data-testid="ai-generated-content"]').should('not.be.empty');
  });

  it('should collaborate in real-time', () => {
    // Create document
    cy.createDocument({
      title: 'Collaboration Test',
      content: 'Initial content'
    });
    
    // Open in new tab (simulate second user)
    cy.window().then((win) => {
      cy.stub(win, 'open').callsFake((url) => {
        win.location.href = url;
      });
    });
    
    cy.get('[data-testid="share-document"]').click();
    cy.get('[data-testid="copy-link"]').click();
    
    // Simulate second user
    cy.visit('/documents/collaboration-test');
    cy.login('collaborator@example.com', 'password123');
    
    // Both users should see each other
    cy.get('[data-testid="collaborator-indicator"]').should('have.length', 2);
  });
});
```

### 5.2 Playwright E2E Tests
```javascript
// tests/e2e/document-workflow.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Document Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="login-btn"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should complete full document creation and editing workflow', async ({ page }) => {
    // Navigate to documents
    await page.click('[data-testid="documents-nav"]');
    await expect(page).toHaveURL('/documents');
    
    // Create new document
    await page.click('[data-testid="create-document-btn"]');
    await page.fill('[data-testid="document-title"]', 'E2E Test Document');
    await page.selectOption('[data-testid="document-template"]', 'business-report');
    await page.fill('[data-testid="document-content"]', 'This is a test document for E2E testing.');
    
    // Save document
    await page.click('[data-testid="save-document-btn"]');
    await expect(page.locator('[data-testid="document-title"]')).toContainText('E2E Test Document');
    
    // Edit document
    await page.click('[data-testid="edit-document-btn"]');
    await page.fill('[data-testid="document-content"]', 'This is the updated content of the document.');
    await page.click('[data-testid="save-document-btn"]');
    
    // Verify changes
    await expect(page.locator('[data-testid="document-content"]')).toContainText('updated content');
    
    // Generate AI content
    await page.click('[data-testid="ai-panel-toggle"]');
    await page.click('[data-testid="ai-action-improve"]');
    await page.fill('[data-testid="ai-prompt"]', 'Improve the clarity and flow of this content');
    await page.click('[data-testid="generate-content-btn"]');
    
    // Wait for AI generation
    await expect(page.locator('[data-testid="ai-generated-content"]')).toBeVisible({ timeout: 15000 });
    
    // Apply AI content
    await page.click('[data-testid="apply-ai-content"]');
    await expect(page.locator('[data-testid="document-content"]')).not.toContainText('updated content');
    
    // Export document
    await page.click('[data-testid="export-menu"]');
    await page.click('[data-testid="export-pdf"]');
    
    // Verify download started
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="confirm-export"]');
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/E2E Test Document\.pdf$/);
  });

  test('should handle collaboration features', async ({ browser }) => {
    // Create two browser contexts for two users
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();
    
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();
    
    // Login both users
    await page1.goto('/login');
    await page1.fill('[data-testid="email"]', 'user1@example.com');
    await page1.fill('[data-testid="password"]', 'password123');
    await page1.click('[data-testid="login-btn"]');
    
    await page2.goto('/login');
    await page2.fill('[data-testid="email"]', 'user2@example.com');
    await page2.fill('[data-testid="password"]', 'password123');
    await page2.click('[data-testid="login-btn"]');
    
    // User 1 creates document
    await page1.goto('/documents');
    await page1.click('[data-testid="create-document-btn"]');
    await page1.fill('[data-testid="document-title"]', 'Collaboration Test');
    await page1.fill('[data-testid="document-content"]', 'Initial content');
    await page1.click('[data-testid="save-document-btn"]');
    
    // User 1 shares document
    await page1.click('[data-testid="share-document"]');
    await page1.click('[data-testid="add-collaborator"]');
    await page1.fill('[data-testid="collaborator-email"]', 'user2@example.com');
    await page1.selectOption('[data-testid="collaborator-role"]', 'editor');
    await page1.click('[data-testid="send-invitation"]');
    
    // User 2 accepts invitation and opens document
    await page2.goto('/documents');
    await page2.click('[data-testid="shared-documents"]');
    await page2.click('[data-testid="collaboration-test-document"]');
    
    // Both users should see each other
    await expect(page1.locator('[data-testid="collaborator-indicator"]')).toHaveCount(2);
    await expect(page2.locator('[data-testid="collaborator-indicator"]')).toHaveCount(2);
    
    // User 2 makes changes
    await page2.click('[data-testid="edit-document-btn"]');
    await page2.fill('[data-testid="document-content"]', 'Content edited by user 2');
    
    // User 1 should see changes in real-time
    await expect(page1.locator('[data-testid="document-content"]')).toContainText('Content edited by user 2');
    
    await context1.close();
    await context2.close();
  });
});
```

## 6. Tests de Rendimiento

### 6.1 K6 Performance Tests
```javascript
// tests/performance/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: 100 }, // Ramp up
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 200 }, // Ramp up to 200 users
    { duration: '5m', target: 200 }, // Stay at 200 users
    { duration: '2m', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests must complete below 2s
    http_req_failed: ['rate<0.1'],     // Error rate must be below 10%
    errors: ['rate<0.1'],
  },
};

const BASE_URL = 'https://api.documentgenerator.com';
let authToken;

export function setup() {
  // Login and get auth token
  const loginResponse = http.post(`${BASE_URL}/auth/login`, {
    email: 'loadtest@example.com',
    password: 'password123'
  });
  
  check(loginResponse, {
    'login successful': (r) => r.status === 200,
  });
  
  return loginResponse.json('data.tokens.accessToken');
}

export default function(token) {
  authToken = token;
  
  const headers = {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json',
  };
  
  // Test document creation
  const createDocResponse = http.post(`${BASE_URL}/api/documents`, {
    title: `Load Test Document ${__VU}`,
    content: 'This is a load test document',
    template: 'business-report'
  }, { headers });
  
  check(createDocResponse, {
    'document creation successful': (r) => r.status === 201,
    'document creation time < 2s': (r) => r.timings.duration < 2000,
  }) || errorRate.add(1);
  
  if (createDocResponse.status === 201) {
    const documentId = createDocResponse.json('data.id');
    
    // Test document retrieval
    const getDocResponse = http.get(`${BASE_URL}/api/documents/${documentId}`, { headers });
    
    check(getDocResponse, {
      'document retrieval successful': (r) => r.status === 200,
      'document retrieval time < 1s': (r) => r.timings.duration < 1000,
    }) || errorRate.add(1);
    
    // Test AI generation
    const aiResponse = http.post(`${BASE_URL}/api/documents/${documentId}/generate`, {
      prompt: 'Generate a summary',
      template: 'business-report'
    }, { headers });
    
    check(aiResponse, {
      'AI generation successful': (r) => r.status === 200,
      'AI generation time < 10s': (r) => r.timings.duration < 10000,
    }) || errorRate.add(1);
    
    // Test document update
    const updateResponse = http.put(`${BASE_URL}/api/documents/${documentId}`, {
      content: 'Updated content for load testing'
    }, { headers });
    
    check(updateResponse, {
      'document update successful': (r) => r.status === 200,
      'document update time < 1s': (r) => r.timings.duration < 1000,
    }) || errorRate.add(1);
  }
  
  sleep(1);
}
```

### 6.2 Artillery Performance Tests
```yaml
# tests/performance/artillery-config.yml
config:
  target: 'https://api.documentgenerator.com'
  phases:
    - duration: 60
      arrivalRate: 10
      name: "Warm up"
    - duration: 120
      arrivalRate: 50
      name: "Ramp up load"
    - duration: 300
      arrivalRate: 100
      name: "Sustained load"
    - duration: 60
      arrivalRate: 0
      name: "Ramp down"
  defaults:
    headers:
      Content-Type: 'application/json'
  processor: './artillery-processor.js'

scenarios:
  - name: "Document Creation and AI Generation"
    weight: 70
    flow:
      - post:
          url: "/auth/login"
          json:
            email: "{{ $randomString() }}@example.com"
            password: "password123"
          capture:
            - json: "$.data.tokens.accessToken"
              as: "authToken"
      - post:
          url: "/api/documents"
          headers:
            Authorization: "Bearer {{ authToken }}"
          json:
            title: "Performance Test Document {{ $randomString() }}"
            content: "This is a performance test document"
            template: "business-report"
          capture:
            - json: "$.data.id"
              as: "documentId"
      - post:
          url: "/api/documents/{{ documentId }}/generate"
          headers:
            Authorization: "Bearer {{ authToken }}"
          json:
            prompt: "Generate a summary of this document"
            template: "business-report"
      - get:
          url: "/api/documents/{{ documentId }}"
          headers:
            Authorization: "Bearer {{ authToken }}"

  - name: "Document Collaboration"
    weight: 30
    flow:
      - post:
          url: "/auth/login"
          json:
            email: "collaborator{{ $randomString() }}@example.com"
            password: "password123"
          capture:
            - json: "$.data.tokens.accessToken"
              as: "authToken"
      - get:
          url: "/api/documents"
          headers:
            Authorization: "Bearer {{ authToken }}"
      - post:
          url: "/api/documents"
          headers:
            Authorization: "Bearer {{ authToken }}"
          json:
            title: "Collaboration Test {{ $randomString() }}"
            content: "Initial content for collaboration"
      - function: "simulateCollaboration"
```

## 7. Tests de Seguridad

### 7.1 Security Test Suite
```javascript
// tests/security/security.test.js
const request = require('supertest');
const app = require('../../src/app');

describe('Security Tests', () => {
  describe('Authentication Security', () => {
    it('should reject requests without authentication', async () => {
      const response = await request(app)
        .get('/api/documents')
        .expect(401);
      
      expect(response.body.error).toBe('Authentication required');
    });

    it('should reject invalid JWT tokens', async () => {
      const response = await request(app)
        .get('/api/documents')
        .set('Authorization', 'Bearer invalid-token')
        .expect(401);
      
      expect(response.body.error).toBe('Invalid token');
    });

    it('should reject expired JWT tokens', async () => {
      const expiredToken = generateExpiredToken();
      
      const response = await request(app)
        .get('/api/documents')
        .set('Authorization', `Bearer ${expiredToken}`)
        .expect(401);
      
      expect(response.body.error).toBe('Token expired');
    });

    it('should implement rate limiting', async () => {
      const promises = [];
      
      // Make 150 requests quickly
      for (let i = 0; i < 150; i++) {
        promises.push(
          request(app)
            .get('/api/documents')
            .set('Authorization', 'Bearer valid-token')
        );
      }
      
      const responses = await Promise.all(promises);
      const rateLimitedResponses = responses.filter(r => r.status === 429);
      
      expect(rateLimitedResponses.length).toBeGreaterThan(0);
    });
  });

  describe('Input Validation', () => {
    it('should prevent SQL injection', async () => {
      const maliciousInput = "'; DROP TABLE documents; --";
      
      const response = await request(app)
        .get('/api/documents')
        .query({ search: maliciousInput })
        .set('Authorization', 'Bearer valid-token')
        .expect(400);
      
      expect(response.body.error).toContain('Invalid input');
    });

    it('should prevent XSS attacks', async () => {
      const xssPayload = '<script>alert("xss")</script>';
      
      const response = await request(app)
        .post('/api/documents')
        .set('Authorization', 'Bearer valid-token')
        .send({
          title: xssPayload,
          content: 'Test content'
        })
        .expect(400);
      
      expect(response.body.error).toContain('Invalid input');
    });

    it('should validate file uploads', async () => {
      const maliciousFile = Buffer.from('malicious content');
      
      const response = await request(app)
        .post('/api/documents/upload')
        .set('Authorization', 'Bearer valid-token')
        .attach('file', maliciousFile, 'malicious.exe')
        .expect(400);
      
      expect(response.body.error).toContain('Invalid file type');
    });
  });

  describe('Authorization', () => {
    it('should prevent access to other users documents', async () => {
      const user1Token = await getAuthToken('user1@example.com');
      const user2Token = await getAuthToken('user2@example.com');
      
      // Create document as user1
      const docResponse = await request(app)
        .post('/api/documents')
        .set('Authorization', `Bearer ${user1Token}`)
        .send({ title: 'User1 Document', content: 'Private content' });
      
      const documentId = docResponse.body.data.id;
      
      // Try to access as user2
      const response = await request(app)
        .get(`/api/documents/${documentId}`)
        .set('Authorization', `Bearer ${user2Token}`)
        .expect(403);
      
      expect(response.body.error).toBe('Access denied');
    });

    it('should enforce role-based permissions', async () => {
      const viewerToken = await getAuthToken('viewer@example.com');
      
      const response = await request(app)
        .delete('/api/documents/some-document-id')
        .set('Authorization', `Bearer ${viewerToken}`)
        .expect(403);
      
      expect(response.body.error).toBe('Insufficient permissions');
    });
  });

  describe('Data Protection', () => {
    it('should encrypt sensitive data', async () => {
      const response = await request(app)
        .post('/api/documents')
        .set('Authorization', 'Bearer valid-token')
        .send({
          title: 'Sensitive Document',
          content: 'This contains sensitive information'
        });
      
      // Check that data is encrypted in database
      const document = await Document.findById(response.body.data.id);
      expect(document.content).not.toBe('This contains sensitive information');
    });

    it('should sanitize user input', async () => {
      const response = await request(app)
        .post('/api/documents')
        .set('Authorization', 'Bearer valid-token')
        .send({
          title: 'Document with <b>HTML</b>',
          content: 'Content with <script>alert("xss")</script>'
        });
      
      expect(response.body.data.title).toBe('Document with HTML');
      expect(response.body.data.content).not.toContain('<script>');
    });
  });
});
```

## 8. Tests de Regresión Visual

### 8.1 Visual Regression Tests
```javascript
// tests/visual/visual-regression.test.js
const { test, expect } = require('@playwright/test');

test.describe('Visual Regression Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="login-btn"]');
  });

  test('dashboard should match snapshot', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    await expect(page).toHaveScreenshot('dashboard.png');
  });

  test('document editor should match snapshot', async ({ page }) => {
    await page.goto('/documents');
    await page.click('[data-testid="create-document-btn"]');
    await page.fill('[data-testid="document-title"]', 'Visual Test Document');
    await page.fill('[data-testid="document-content"]', 'This is a visual test document.');
    
    await expect(page).toHaveScreenshot('document-editor.png');
  });

  test('AI panel should match snapshot', async ({ page }) => {
    await page.goto('/documents');
    await page.click('[data-testid="create-document-btn"]');
    await page.click('[data-testid="ai-panel-toggle"]');
    
    await expect(page).toHaveScreenshot('ai-panel.png');
  });

  test('mobile view should match snapshot', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard');
    
    await expect(page).toHaveScreenshot('dashboard-mobile.png');
  });
});
```

## 9. Configuración de CI/CD

### 9.1 GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run unit tests
      run: npm run test:unit
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage/lcov.info

  integration-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run integration tests
      run: npm run test:integration
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379

  e2e-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Install Playwright
      run: npx playwright install --with-deps
    
    - name: Run E2E tests
      run: npm run test:e2e
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: failure()
      with:
        name: playwright-report
        path: playwright-report/

  performance-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run performance tests
      run: npm run test:performance

  security-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run security tests
      run: npm run test:security
    
    - name: Run security audit
      run: npm audit --audit-level moderate
```

### 9.2 Scripts de Testing
```json
{
  "scripts": {
    "test": "jest",
    "test:unit": "jest --testPathPattern=__tests__",
    "test:integration": "jest --testPathPattern=integration",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:performance": "k6 run tests/performance/load-test.js",
    "test:security": "jest --testPathPattern=security",
    "test:visual": "playwright test --grep @visual",
    "test:coverage": "jest --coverage",
    "test:watch": "jest --watch",
    "test:ci": "jest --ci --coverage --watchAll=false"
  }
}
```

Este framework de testing completo proporciona una cobertura exhaustiva del sistema de generación de documentos con IA, asegurando calidad, rendimiento y seguridad en todos los niveles.




