# Arquitectura Mejorada V2

## Visión General

Arquitectura modular y escalable mejorada siguiendo las mejores prácticas de React Native, Expo y TypeScript.

## Estructura de Carpetas Mejorada

```
app/                          # Expo Router (File-based routing)
├── (tabs)/                  # Tab navigation screens
│   ├── _layout.tsx         # Tab layout
│   ├── index.tsx           # Dashboard
│   ├── calendar.tsx        # Calendar screen
│   ├── routines.tsx        # Routines screen
│   ├── wardrobe.tsx        # Wardrobe screen
│   └── protocols.tsx       # Protocols screen
└── _layout.tsx              # Root layout

src/
├── components/              # Componentes reutilizables
│   ├── ui/                 # UI Components (Button, Card, etc.)
│   │   ├── index.ts        # Barrel export
│   │   └── ...
│   ├── layout/             # Layout Components (ErrorBoundary, etc.)
│   │   ├── index.ts        # Barrel export
│   │   └── ...
│   └── index.ts            # Main barrel export
│
├── providers/              # Context Providers
│   ├── app-provider.tsx    # Main app provider
│   └── index.ts            # Barrel export
│
├── context/                # React Contexts
│   ├── theme-context.tsx   # Theme context
│   └── index.ts            # Barrel export
│
├── hooks/                  # Custom Hooks
│   ├── api/                # API-related hooks
│   │   ├── index.ts        # Barrel export
│   │   └── ...
│   ├── ui/                 # UI-related hooks
│   │   ├── index.ts        # Barrel export
│   │   └── ...
│   └── index.ts            # Main barrel export
│
├── services/               # API Services
│   ├── base-service.ts     # Base service class
│   ├── calendar-service.ts
│   ├── routine-service.ts
│   ├── dashboard-service.ts
│   ├── wardrobe-service.ts
│   ├── protocol-service.ts
│   └── index.ts            # Barrel export
│
├── store/                  # Zustand Stores
│   └── auth-store.ts
│
├── types/                  # TypeScript Types
│   ├── domain.ts           # Domain types (CalendarEvent, etc.)
│   ├── api.ts              # API types (ApiResponse, etc.)
│   ├── schemas.ts          # Zod schema types
│   └── index.ts            # Main barrel export
│
├── utils/                  # Utilidades
│   ├── api-client.ts       # HTTP client
│   ├── storage.ts          # Storage utilities
│   ├── validation.ts       # Zod schemas
│   ├── format.ts           # Formatting utilities
│   ├── logger.ts           # Logging
│   ├── haptics.ts          # Haptic feedback
│   ├── i18n.ts             # Internationalization
│   ├── error-reporter.ts   # Error reporting
│   └── index.ts            # Barrel export
│
└── constants/              # Constantes
    ├── colors.ts
    ├── config.ts
    └── index.ts            # Barrel export
```

## Mejoras Arquitectónicas

### 1. Barrel Exports

Todos los módulos principales tienen `index.ts` que exporta sus contenidos:

```typescript
// Antes
import { Button } from '@/components/button';
import { Card } from '@/components/card';

// Ahora
import { Button, Card } from '@/components/ui';
```

**Beneficios:**
- Imports más limpios
- Mejor organización
- Fácil refactoring
- Mejor tree-shaking

### 2. Separación de Componentes

#### UI Components (`components/ui/`)
- Componentes de interfaz reutilizables
- Button, Card, LoadingSpinner, ErrorMessage
- No dependen de lógica de negocio

#### Layout Components (`components/layout/`)
- Componentes de estructura
- ErrorBoundary, ToastProvider, NetworkStatus
- SafeAreaScrollView, TabBarIcon

### 3. Providers Centralizados

#### AppProvider
- Envuelve toda la aplicación
- Incluye: ErrorBoundary, GestureHandler, SafeArea, QueryClient, Toast
- Simplifica `_layout.tsx`

#### ThemeProvider (Context)
- Context para tema
- Evita prop drilling
- Mejor performance que hooks individuales

### 4. Base Service Class

```typescript
class BaseService {
  protected async getArtistIdOrThrow(): Promise<string>
  protected handleError(error: unknown): never
}
```

**Beneficios:**
- DRY (Don't Repeat Yourself)
- Manejo de errores consistente
- Fácil extensión

### 5. Organización de Tipos

#### Domain Types (`types/domain.ts`)
- Tipos del dominio de negocio
- CalendarEvent, RoutineTask, Protocol, etc.
- Interfaces principales

#### API Types (`types/api.ts`)
- Tipos relacionados con API
- ApiResponse, PaginatedResponse, etc.
- Re-exporta domain types

#### Schema Types (`types/schemas.ts`)
- Tipos derivados de Zod schemas
- Para validación de formularios

### 6. Hooks Organizados

#### API Hooks (`hooks/api/`)
- Hooks relacionados con data fetching
- useCalendarEvents, useRoutines, etc.
- Encapsulan lógica de React Query

#### UI Hooks (`hooks/ui/`)
- Hooks de UI y utilidades
- useColorScheme, useWindowDimensions, useToast, etc.

### 7. Context API

#### ThemeContext
- Reemplaza múltiples llamadas a `useColorScheme`
- Mejor performance
- Fácil de extender

## Flujo de Datos Mejorado

```
Component
  ↓
Hook (useCalendarEvents)
  ↓
Service (calendarService)
  ↓
BaseService (getArtistIdOrThrow, handleError)
  ↓
API Client (apiClient)
  ↓
Backend API
  ↓
React Query Cache
```

## Patrones Implementados

### 1. Provider Pattern
- AppProvider centraliza todos los providers
- ThemeProvider para tema
- Fácil agregar nuevos providers

### 2. Service Pattern
- BaseService para lógica común
- Servicios específicos extienden funcionalidad
- Separación de concerns

### 3. Hook Pattern
- Custom hooks encapsulan lógica
- Reutilización de código
- Testing más fácil

### 4. Barrel Export Pattern
- Imports más limpios
- Mejor organización
- Fácil refactoring

### 5. Context Pattern
- ThemeContext evita prop drilling
- Mejor performance
- Fácil de extender

## Beneficios de la Nueva Arquitectura

### 1. Mantenibilidad
- ✅ Código más organizado
- ✅ Fácil encontrar archivos
- ✅ Separación clara de concerns

### 2. Escalabilidad
- ✅ Fácil agregar nuevas features
- ✅ Estructura preparada para crecimiento
- ✅ Patrones consistentes

### 3. Performance
- ✅ Mejor tree-shaking con barrel exports
- ✅ Context reduce re-renders
- ✅ Lazy loading preparado

### 4. Developer Experience
- ✅ Imports más limpios
- ✅ Autocomplete mejorado
- ✅ Mejor IntelliSense

### 5. Testing
- ✅ Fácil mockear servicios
- ✅ Hooks testables
- ✅ Componentes aislados

## Migración

### Antes
```typescript
import { Button } from '@/components/button';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { calendarService } from '@/services/calendar-service';
```

### Después
```typescript
import { Button } from '@/components/ui';
import { useTheme } from '@/context';
import { calendarService } from '@/services';
```

## Próximas Mejoras

1. **Feature-based Structure** (Opcional)
   - Agrupar por features cuando crezca
   - `features/calendar/`, `features/routines/`, etc.

2. **Lazy Loading**
   - Dynamic imports para screens
   - Code splitting por feature

3. **Error Boundaries Granulares**
   - Error boundaries por feature
   - Mejor manejo de errores

4. **State Management**
   - Más stores de Zustand si es necesario
   - Context para estado compartido

5. **Testing Structure**
   - `__tests__/` junto a archivos
   - `__mocks__/` para mocks

## Convenciones

### Naming
- ✅ Lowercase con dashes para carpetas
- ✅ PascalCase para componentes
- ✅ camelCase para funciones y variables
- ✅ UPPER_CASE para constantes

### File Structure
- ✅ Un componente por archivo
- ✅ Barrel exports en `index.ts`
- ✅ Types separados por categoría

### Imports
- ✅ Barrel exports cuando sea posible
- ✅ Imports absolutos con `@/`
- ✅ Agrupar imports (external, internal, types)

## Conclusión

La nueva arquitectura proporciona:
- ✅ Mejor organización
- ✅ Código más mantenible
- ✅ Fácil escalabilidad
- ✅ Mejor developer experience
- ✅ Preparada para crecimiento


