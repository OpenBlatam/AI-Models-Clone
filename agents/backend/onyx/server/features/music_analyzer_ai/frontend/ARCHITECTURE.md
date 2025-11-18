# Arquitectura del Frontend

## 📁 Estructura de Directorios

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx          # Layout principal
│   ├── page.tsx            # Página de inicio
│   ├── providers.tsx       # Providers globales
│   ├── music/              # Páginas de Music Analyzer
│   │   ├── components/     # Componentes específicos de música
│   │   ├── hooks/          # Hooks específicos de música
│   │   └── page.tsx        # Página principal de música
│   └── robot/              # Páginas de Robot Movement
├── components/             # Componentes React reutilizables
│   ├── ui/                 # Componentes UI base (barrel export)
│   ├── music/              # Componentes específicos de música
│   ├── robot/              # Componentes específicos de robot
│   ├── error-boundary.tsx  # Error boundary global
│   └── Navigation.tsx      # Navegación principal
├── lib/                    # Utilidades y servicios
│   ├── api/                # Servicios API
│   │   ├── client.ts       # Cliente Axios configurado
│   │   ├── tracks.ts        # Endpoints de tracks
│   │   ├── comparison.ts   # Endpoints de comparación
│   │   ├── recommendations.ts # Endpoints de recomendaciones
│   │   ├── favorites.ts    # Endpoints de favoritos
│   │   ├── types.ts        # Tipos TypeScript con Zod
│   │   └── index.ts        # Exportaciones principales
│   ├── config/             # Configuración
│   │   ├── env.ts          # Variables de entorno
│   │   └── app.ts          # Configuración de la aplicación
│   ├── constants/          # Constantes
│   │   └── index.ts        # Todas las constantes
│   ├── hooks/              # Hooks compartidos
│   │   ├── use-debounce.ts
│   │   ├── use-local-storage.ts
│   │   ├── use-media-query.ts
│   │   └── index.ts
│   ├── store/              # Zustand stores
│   │   ├── music-store.ts  # Store de música
│   │   └── index.ts
│   ├── types/              # Tipos TypeScript compartidos
│   │   ├── common.ts
│   │   └── index.ts
│   ├── validations/        # Esquemas Zod
│   │   ├── music.ts
│   │   └── index.ts
│   ├── errors.ts           # Tipos de error personalizados
│   └── utils.ts            # Utilidades generales
├── middleware.ts           # Middleware de Next.js
├── __tests__/              # Tests
└── public/                 # Archivos estáticos
```

## 🏗️ Principios Arquitectónicos

### 1. Separación de Responsabilidades

- **App Router**: Páginas y layouts (Next.js 14)
- **Components**: Componentes UI reutilizables
- **Lib**: Lógica de negocio, servicios, utilidades
- **Store**: Estado global (Zustand)
- **Hooks**: Lógica reutilizable de componentes

### 2. Organización por Features

Cada feature (music, robot) tiene su propia carpeta con:
- Componentes específicos
- Hooks específicos
- Páginas relacionadas

### 3. Barrel Exports

Uso de `index.ts` para exportaciones centralizadas:
```typescript
// En lugar de:
import { useDebounce } from '@/lib/hooks/use-debounce';

// Usar:
import { useDebounce } from '@/lib/hooks';
```

## 🔧 Configuración

### Variables de Entorno

Las variables de entorno se acceden a través de `lib/config/env.ts`:
```typescript
import { env } from '@/lib/config/env';

const apiUrl = env.MUSIC_API_URL;
```

### Constantes

Todas las constantes están en `lib/constants/index.ts`:
```typescript
import { QUERY_KEYS, ROUTES, PAGINATION } from '@/lib/constants';
```

## 📦 Gestión de Estado

### Zustand Stores

Para estado global que necesita persistencia:
```typescript
import { useMusicStore } from '@/lib/store';

const { currentTrack, setCurrentTrack } = useMusicStore();
```

### React Query

Para estado del servidor y caché:
```typescript
import { useQuery } from '@tanstack/react-query';
import { QUERY_KEYS } from '@/lib/constants';

const { data } = useQuery({
  queryKey: QUERY_KEYS.MUSIC.SEARCH(query),
  queryFn: () => searchTracks(query),
});
```

## 🎣 Hooks Personalizados

### Hooks Compartidos

- `useDebounce`: Para debounce de valores
- `useLocalStorage`: Para localStorage con type safety
- `useMediaQuery`: Para responsive design

### Hooks por Feature

Los hooks específicos de cada feature van en su carpeta:
- `app/music/hooks/use-music-state.ts`

## ✅ Validación

### Zod Schemas

Validación en tiempo de ejecución con Zod:
```typescript
import { searchQuerySchema } from '@/lib/validations';

const result = searchQuerySchema.parse(query);
```

## 🚨 Manejo de Errores

### Error Boundaries

Componentes envueltos en error boundaries:
```typescript
<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>
```

### Custom Errors

Tipos de error personalizados:
- `ApiError`: Errores de API
- `NetworkError`: Errores de red
- `ValidationError`: Errores de validación

## 🎨 Componentes

### Estructura de Componentes

```typescript
/**
 * Component description.
 * @param props - Component props
 */
export function Component({ prop1, prop2 }: ComponentProps) {
  // Hooks
  // State
  // Effects
  // Handlers
  // Render
}
```

### Dynamic Imports

Para code splitting:
```typescript
const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  ssr: false,
  loading: () => <LoadingState />,
});
```

## 🔒 Seguridad

### Headers de Seguridad

Configurados en `middleware.ts` y `next.config.js`:
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy
- X-DNS-Prefetch-Control

## ⚡ Optimizaciones

### Next.js Config

- Image optimization (WebP, AVIF)
- Package import optimization
- Console removal en producción
- Bundle size optimization

### Code Splitting

- Dynamic imports para componentes pesados
- Lazy loading de rutas
- Optimización de imports

## 📝 Convenciones

### Nombres de Archivos

- Componentes: `PascalCase.tsx`
- Hooks: `use-kebab-case.ts`
- Utilidades: `kebab-case.ts`
- Tipos: `kebab-case.ts`

### Imports

Orden de imports:
1. React/Next.js
2. Librerías de terceros
3. Componentes internos
4. Utilidades y tipos
5. Estilos

```typescript
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui';
import { useDebounce } from '@/lib/hooks';
import type { Track } from '@/lib/api/types';
```

## 🧪 Testing

Estructura de tests:
```
__tests__/
├── components/
├── lib/
└── utils.test.ts
```

## 📚 Recursos

- [Next.js Documentation](https://nextjs.org/docs)
- [React Query](https://tanstack.com/query/latest)
- [Zustand](https://github.com/pmndrs/zustand)
- [Zod](https://zod.dev/)

