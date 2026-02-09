# AI Continuous Document Generator - Especificaciones de Diseño de UI/UX

## 1. Principios de Diseño

### 1.1 Filosofía de Diseño
- **Simplicidad**: Interfaz limpia y fácil de usar
- **Eficiencia**: Flujos de trabajo optimizados
- **Accesibilidad**: Cumplimiento WCAG 2.1 AA
- **Responsividad**: Funciona en todos los dispositivos
- **Consistencia**: Patrones de diseño coherentes
- **Feedback**: Retroalimentación clara para todas las acciones

### 1.2 Sistema de Diseño
- **Design System**: Componentes reutilizables
- **Tokens de Diseño**: Colores, tipografías, espaciados
- **Iconografía**: Conjunto consistente de iconos
- **Animaciones**: Transiciones suaves y significativas

## 2. Arquitectura de Información

### 2.1 Estructura de Navegación
```
┌─────────────────────────────────────┐
│              Header                 │
├─────────────────────────────────────┤
│  Sidebar  │        Main Content     │
│           │                         │
│  • Docs   │    Document Editor      │
│  • AI     │    + AI Panel          │
│  • Team   │    + Collaboration     │
│  • Settings│                        │
└─────────────────────────────────────┘
```

### 2.2 Jerarquía de Páginas
- **Dashboard**: Vista general de documentos
- **Document Editor**: Editor principal con IA
- **Templates**: Biblioteca de plantillas
- **Team**: Gestión de colaboradores
- **Settings**: Configuración de usuario
- **Profile**: Perfil y preferencias

## 3. Componentes de UI

### 3.1 Header/Navigation
```typescript
interface HeaderProps {
  user: User;
  notifications: Notification[];
  onLogout: () => void;
}

const Header: React.FC<HeaderProps> = ({ user, notifications, onLogout }) => {
  return (
    <header className="header">
      <div className="header-left">
        <Logo />
        <SearchBar />
      </div>
      
      <div className="header-right">
        <NotificationBell count={notifications.length} />
        <UserMenu user={user} onLogout={onLogout} />
      </div>
    </header>
  );
};
```

### 3.2 Sidebar Navigation
```typescript
interface SidebarProps {
  currentPath: string;
  documents: Document[];
  onNavigate: (path: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ currentPath, documents, onNavigate }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: 'home', path: '/' },
    { id: 'documents', label: 'Mis Documentos', icon: 'document', path: '/documents' },
    { id: 'templates', label: 'Plantillas', icon: 'template', path: '/templates' },
    { id: 'ai', label: 'Asistente IA', icon: 'brain', path: '/ai' },
    { id: 'team', label: 'Equipo', icon: 'users', path: '/team' },
    { id: 'settings', label: 'Configuración', icon: 'settings', path: '/settings' }
  ];

  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        {menuItems.map(item => (
          <NavItem
            key={item.id}
            item={item}
            isActive={currentPath === item.path}
            onClick={() => onNavigate(item.path)}
          />
        ))}
      </nav>
      
      <div className="recent-documents">
        <h3>Documentos Recientes</h3>
        {documents.slice(0, 5).map(doc => (
          <RecentDocument
            key={doc.id}
            document={doc}
            onClick={() => onNavigate(`/documents/${doc.id}`)}
          />
        ))}
      </div>
    </aside>
  );
};
```

### 3.3 Document Editor
```typescript
interface DocumentEditorProps {
  document: Document;
  collaborators: Collaborator[];
  onContentChange: (content: string) => void;
  onSave: () => void;
}

const DocumentEditor: React.FC<DocumentEditorProps> = ({
  document,
  collaborators,
  onContentChange,
  onSave
}) => {
  const [content, setContent] = useState(document.content);
  const [isCollaborating, setIsCollaborating] = useState(false);

  return (
    <div className="document-editor">
      <div className="editor-header">
        <div className="document-info">
          <h1>{document.title}</h1>
          <DocumentStatus status={document.status} />
        </div>
        
        <div className="editor-actions">
          <CollaborationIndicator
            collaborators={collaborators}
            isActive={isCollaborating}
          />
          <SaveButton onSave={onSave} />
          <ExportMenu documentId={document.id} />
        </div>
      </div>
      
      <div className="editor-content">
        <div className="editor-toolbar">
          <FormatToolbar />
          <AIToolbar documentId={document.id} />
        </div>
        
        <div className="editor-main">
          <RichTextEditor
            value={content}
            onChange={(newContent) => {
              setContent(newContent);
              onContentChange(newContent);
            }}
            placeholder="Comienza a escribir tu documento..."
            className="document-content"
          />
        </div>
      </div>
    </div>
  );
};
```

### 3.4 AI Assistant Panel
```typescript
interface AIPanelProps {
  documentId: string;
  onContentGenerated: (content: string) => void;
}

const AIPanel: React.FC<AIPanelProps> = ({ documentId, onContentGenerated }) => {
  const [prompt, setPrompt] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const templates = [
    { id: 'summary', name: 'Resumen', icon: 'summary' },
    { id: 'outline', name: 'Esquema', icon: 'list' },
    { id: 'expand', name: 'Expandir', icon: 'expand' },
    { id: 'improve', name: 'Mejorar', icon: 'improve' },
    { id: 'translate', name: 'Traducir', icon: 'translate' }
  ];

  return (
    <div className="ai-panel">
      <div className="ai-header">
        <h3>Asistente IA</h3>
        <AIStatus />
      </div>
      
      <div className="ai-templates">
        <h4>Acciones Rápidas</h4>
        <div className="template-grid">
          {templates.map(template => (
            <TemplateButton
              key={template.id}
              template={template}
              onClick={() => handleTemplateAction(template.id)}
            />
          ))}
        </div>
      </div>
      
      <div className="ai-prompt">
        <h4>Instrucciones Personalizadas</h4>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe qué quieres que genere la IA..."
          className="prompt-input"
        />
        
        <div className="prompt-options">
          <TemplateSelector
            value={selectedTemplate}
            onChange={setSelectedTemplate}
          />
          
          <ToneSelector />
          <LengthSelector />
        </div>
        
        <button
          className="generate-button"
          onClick={handleGenerate}
          disabled={isGenerating || !prompt.trim()}
        >
          {isGenerating ? (
            <>
              <Spinner />
              Generando...
            </>
          ) : (
            <>
              <BrainIcon />
              Generar Contenido
            </>
          )}
        </button>
      </div>
      
      <div className="ai-history">
        <h4>Historial de Generaciones</h4>
        <GenerationHistory documentId={documentId} />
      </div>
    </div>
  );
};
```

## 4. Sistema de Colores

### 4.1 Paleta de Colores
```css
:root {
  /* Colores Primarios */
  --primary-50: #eff6ff;
  --primary-100: #dbeafe;
  --primary-200: #bfdbfe;
  --primary-300: #93c5fd;
  --primary-400: #60a5fa;
  --primary-500: #3b82f6;
  --primary-600: #2563eb;
  --primary-700: #1d4ed8;
  --primary-800: #1e40af;
  --primary-900: #1e3a8a;

  /* Colores Secundarios */
  --secondary-50: #f8fafc;
  --secondary-100: #f1f5f9;
  --secondary-200: #e2e8f0;
  --secondary-300: #cbd5e1;
  --secondary-400: #94a3b8;
  --secondary-500: #64748b;
  --secondary-600: #475569;
  --secondary-700: #334155;
  --secondary-800: #1e293b;
  --secondary-900: #0f172a;

  /* Colores de Estado */
  --success-500: #10b981;
  --warning-500: #f59e0b;
  --error-500: #ef4444;
  --info-500: #3b82f6;

  /* Colores de Fondo */
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  --bg-dark: #0f172a;

  /* Colores de Texto */
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-tertiary: #94a3b8;
  --text-inverse: #ffffff;
}
```

### 4.2 Modo Oscuro
```css
[data-theme="dark"] {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-tertiary: #334155;
  
  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --text-tertiary: #94a3b8;
  --text-inverse: #0f172a;
}
```

## 5. Tipografía

### 5.1 Sistema de Tipografía
```css
:root {
  /* Fuentes */
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  /* Tamaños de Fuente */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  --text-4xl: 2.25rem;   /* 36px */
  
  /* Pesos de Fuente */
  --font-light: 300;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* Altura de Línea */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
}
```

### 5.2 Componentes de Texto
```typescript
interface TextProps {
  variant: 'h1' | 'h2' | 'h3' | 'h4' | 'body' | 'caption' | 'label';
  children: React.ReactNode;
  className?: string;
}

const Text: React.FC<TextProps> = ({ variant, children, className }) => {
  const baseClasses = 'text-primary font-normal';
  
  const variantClasses = {
    h1: 'text-4xl font-bold leading-tight',
    h2: 'text-3xl font-semibold leading-tight',
    h3: 'text-2xl font-semibold leading-normal',
    h4: 'text-xl font-medium leading-normal',
    body: 'text-base leading-normal',
    caption: 'text-sm text-secondary',
    label: 'text-sm font-medium text-secondary'
  };

  return (
    <span className={`${baseClasses} ${variantClasses[variant]} ${className}`}>
      {children}
    </span>
  );
};
```

## 6. Espaciado y Layout

### 6.1 Sistema de Espaciado
```css
:root {
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
  --space-24: 6rem;     /* 96px */
}
```

### 6.2 Grid System
```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

.grid {
  display: grid;
  gap: var(--space-6);
}

.grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }

@media (min-width: 768px) {
  .md\:grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
  .md\:grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
}

@media (min-width: 1024px) {
  .lg\:grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
  .lg\:grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
}
```

## 7. Componentes Interactivos

### 7.1 Botones
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({
  variant,
  size,
  children,
  onClick,
  disabled,
  loading,
  icon
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variantClasses = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
    secondary: 'bg-secondary-100 text-secondary-900 hover:bg-secondary-200 focus:ring-secondary-500',
    outline: 'border border-secondary-300 text-secondary-700 hover:bg-secondary-50 focus:ring-secondary-500',
    ghost: 'text-secondary-700 hover:bg-secondary-100 focus:ring-secondary-500',
    danger: 'bg-error-600 text-white hover:bg-error-700 focus:ring-error-500'
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading ? <Spinner size="sm" /> : icon}
      {children}
    </button>
  );
};
```

### 7.2 Input Fields
```typescript
interface InputProps {
  type: 'text' | 'email' | 'password' | 'textarea';
  label?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
}

const Input: React.FC<InputProps> = ({
  type,
  label,
  placeholder,
  value,
  onChange,
  error,
  disabled,
  required
}) => {
  const baseClasses = 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors';
  const errorClasses = error ? 'border-error-300 focus:ring-error-500' : 'border-secondary-300 focus:border-primary-500';
  const disabledClasses = disabled ? 'bg-secondary-50 cursor-not-allowed' : 'bg-white';

  return (
    <div className="input-group">
      {label && (
        <label className="block text-sm font-medium text-secondary-700 mb-1">
          {label}
          {required && <span className="text-error-500 ml-1">*</span>}
        </label>
      )}
      
      {type === 'textarea' ? (
        <textarea
          className={`${baseClasses} ${errorClasses} ${disabledClasses} resize-vertical`}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          rows={4}
        />
      ) : (
        <input
          type={type}
          className={`${baseClasses} ${errorClasses} ${disabledClasses}`}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
        />
      )}
      
      {error && (
        <p className="mt-1 text-sm text-error-600">{error}</p>
      )}
    </div>
  );
};
```

## 8. Estados y Feedback

### 8.1 Loading States
```typescript
interface LoadingSpinnerProps {
  size: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary' | 'white';
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size, color = 'primary' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };
  
  const colorClasses = {
    primary: 'text-primary-600',
    secondary: 'text-secondary-600',
    white: 'text-white'
  };

  return (
    <div className={`animate-spin ${sizeClasses[size]} ${colorClasses[color]}`}>
      <svg className="w-full h-full" fill="none" viewBox="0 0 24 24">
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </div>
  );
};
```

### 8.2 Toast Notifications
```typescript
interface ToastProps {
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  onClose: () => void;
}

const Toast: React.FC<ToastProps> = ({ type, title, message, duration = 5000, onClose }) => {
  const typeClasses = {
    success: 'bg-success-50 border-success-200 text-success-800',
    error: 'bg-error-50 border-error-200 text-error-800',
    warning: 'bg-warning-50 border-warning-200 text-warning-800',
    info: 'bg-info-50 border-info-200 text-info-800'
  };

  const iconClasses = {
    success: 'text-success-400',
    error: 'text-error-400',
    warning: 'text-warning-400',
    info: 'text-info-400'
  };

  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  return (
    <div className={`fixed top-4 right-4 max-w-sm w-full bg-white border rounded-lg shadow-lg p-4 ${typeClasses[type]}`}>
      <div className="flex items-start">
        <div className={`flex-shrink-0 ${iconClasses[type]}`}>
          <Icon name={type} size="sm" />
        </div>
        
        <div className="ml-3 flex-1">
          <h4 className="text-sm font-medium">{title}</h4>
          {message && (
            <p className="mt-1 text-sm opacity-90">{message}</p>
          )}
        </div>
        
        <button
          onClick={onClose}
          className="ml-4 flex-shrink-0 text-gray-400 hover:text-gray-600"
        >
          <Icon name="close" size="sm" />
        </button>
      </div>
    </div>
  );
};
```

## 9. Responsive Design

### 9.1 Breakpoints
```css
:root {
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
}

@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
@media (min-width: 1536px) { /* 2xl */ }
```

### 9.2 Mobile-First Layout
```typescript
const ResponsiveLayout: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Mobile Header */}
      <header className="lg:hidden bg-white border-b border-secondary-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <Logo />
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 text-secondary-600"
          >
            <Icon name="menu" />
          </button>
        </div>
      </header>

      {/* Desktop Header */}
      <header className="hidden lg:block bg-white border-b border-secondary-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <Logo />
          <SearchBar />
          <UserMenu />
        </div>
      </header>

      <div className="flex">
        {/* Mobile Sidebar */}
        {isMobileMenuOpen && (
          <div className="lg:hidden fixed inset-0 z-50">
            <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setIsMobileMenuOpen(false)} />
            <div className="fixed left-0 top-0 h-full w-64 bg-white shadow-lg">
              <Sidebar onNavigate={() => setIsMobileMenuOpen(false)} />
            </div>
          </div>
        )}

        {/* Desktop Sidebar */}
        <aside className="hidden lg:block w-64 bg-white border-r border-secondary-200">
          <Sidebar />
        </aside>

        {/* Main Content */}
        <main className="flex-1 lg:ml-0">
          <div className="p-4 lg:p-6">
            <DocumentEditor />
          </div>
        </main>
      </div>
    </div>
  );
};
```

## 10. Accesibilidad

### 10.1 ARIA Labels y Roles
```typescript
const AccessibleButton: React.FC<ButtonProps> = ({ children, onClick, disabled, ...props }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      aria-disabled={disabled}
      role="button"
      tabIndex={disabled ? -1 : 0}
      {...props}
    >
      {children}
    </button>
  );
};

const AccessibleInput: React.FC<InputProps> = ({ label, error, ...props }) => {
  const inputId = useId();
  const errorId = useId();

  return (
    <div>
      <label htmlFor={inputId} className="block text-sm font-medium">
        {label}
      </label>
      <input
        id={inputId}
        aria-describedby={error ? errorId : undefined}
        aria-invalid={error ? 'true' : 'false'}
        {...props}
      />
      {error && (
        <div id={errorId} role="alert" className="text-sm text-error-600">
          {error}
        </div>
      )}
    </div>
  );
};
```

### 10.2 Navegación por Teclado
```typescript
const KeyboardNavigation: React.FC = () => {
  const handleKeyDown = (event: KeyboardEvent) => {
    switch (event.key) {
      case 'Escape':
        // Cerrar modales o menús
        break;
      case 'Enter':
        // Activar botones o enlaces
        break;
      case 'Tab':
        // Navegación secuencial
        break;
      case 'ArrowUp':
      case 'ArrowDown':
        // Navegación en listas
        break;
    }
  };

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return <div>Content with keyboard navigation</div>;
};
```

## 11. Animaciones y Transiciones

### 11.1 Transiciones CSS
```css
.transition-base {
  transition: all 0.2s ease-in-out;
}

.transition-colors {
  transition: color 0.2s ease-in-out, background-color 0.2s ease-in-out, border-color 0.2s ease-in-out;
}

.transition-transform {
  transition: transform 0.2s ease-in-out;
}

.transition-opacity {
  transition: opacity 0.2s ease-in-out;
}

/* Hover Effects */
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.hover-scale:hover {
  transform: scale(1.05);
}

/* Focus Effects */
.focus-ring:focus {
  outline: none;
  ring: 2px solid var(--primary-500);
  ring-offset: 2px;
}
```

### 11.2 Animaciones de Entrada
```typescript
const FadeIn: React.FC<{ children: React.ReactNode; delay?: number }> = ({ children, delay = 0 }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  return (
    <div
      className={`transition-opacity duration-500 ${
        isVisible ? 'opacity-100' : 'opacity-0'
      }`}
    >
      {children}
    </div>
  );
};

const SlideIn: React.FC<{ children: React.ReactNode; direction: 'left' | 'right' | 'up' | 'down' }> = ({
  children,
  direction
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const directionClasses = {
    left: isVisible ? 'translate-x-0' : '-translate-x-full',
    right: isVisible ? 'translate-x-0' : 'translate-x-full',
    up: isVisible ? 'translate-y-0' : '-translate-y-full',
    down: isVisible ? 'translate-y-0' : 'translate-y-full'
  };

  return (
    <div
      className={`transition-transform duration-300 ease-out ${directionClasses[direction]}`}
    >
      {children}
    </div>
  );
};
```

## 12. Testing de UI

### 12.1 Component Testing
```typescript
// Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button variant="primary">Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button variant="primary" onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button variant="primary" disabled>Click me</Button>);
    expect(screen.getByText('Click me')).toBeDisabled();
  });

  it('shows loading state', () => {
    render(<Button variant="primary" loading>Click me</Button>);
    expect(screen.getByText('Generando...')).toBeInTheDocument();
  });
});
```

### 12.2 Visual Regression Testing
```typescript
// visual-regression.test.tsx
import { render } from '@testing-library/react';
import { Button } from './Button';

describe('Visual Regression Tests', () => {
  it('matches snapshot for primary button', () => {
    const { container } = render(<Button variant="primary">Primary Button</Button>);
    expect(container.firstChild).toMatchSnapshot();
  });

  it('matches snapshot for secondary button', () => {
    const { container } = render(<Button variant="secondary">Secondary Button</Button>);
    expect(container.firstChild).toMatchSnapshot();
  });
});
```

Esta especificación de diseño de UI/UX proporciona una base sólida para crear una interfaz de usuario moderna, accesible y fácil de usar para el sistema de generación de documentos con IA.







