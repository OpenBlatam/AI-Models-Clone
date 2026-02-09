# Arquitectura de la Aplicación

## Visión General

La aplicación está construida con una arquitectura modular y escalable, siguiendo las mejores prácticas de React Native y Expo.

## Estructura de Carpetas

```
app/                    # Expo Router (File-based routing)
├── (tabs)/            # Tab navigation screens
└── _layout.tsx        # Root layout con providers

src/
├── components/        # Componentes reutilizables
│   ├── button.tsx
│   ├── card.tsx
│   ├── error-boundary.tsx
│   └── ...
├── constants/         # Constantes y configuración
│   ├── colors.ts
│   └── config.ts
├── hooks/            # Custom hooks
│   ├── use-color-scheme.ts
│   ├── use-calendar-events.ts
│   └── ...
├── services/         # Servicios API
│   ├── calendar-service.ts
│   ├── routine-service.ts
│   └── ...
├── store/           # Zustand stores
│   └── auth-store.ts
├── types/           # TypeScript types
│   └── index.ts
└── utils/           # Utilidades
    ├── api-client.ts
    ├── storage.ts
    ├── validation.ts
    └── format.ts
```

## Flujo de Datos

### 1. Data Fetching (React Query)

```
Component → Hook → Service → API Client → Backend
                ↓
         React Query Cache
```

- **Hooks personalizados** (`use-calendar-events.ts`, etc.) encapsulan la lógica de React Query
- **Servicios** (`calendar-service.ts`, etc.) manejan las llamadas API
- **API Client** (`api-client.ts`) centraliza el manejo de HTTP
- **React Query** maneja caching, refetching y sincronización

### 2. State Management

#### Global State (Zustand)
- Autenticación (`auth-store.ts`)
- Preferencias de usuario
- Estado compartido entre screens

#### Server State (React Query)
- Datos del servidor (eventos, rutinas, etc.)
- Cache automático
- Sincronización en background

#### Local State (useState/useReducer)
- Estado UI local (formularios, modales, etc.)
- No se comparte entre componentes

## Componentes

### Principios de Diseño

1. **Composición sobre Herencia**: Componentes pequeños y reutilizables
2. **Props Tipadas**: TypeScript para type safety
3. **Dark Mode**: Soporte automático con `useColorScheme`
4. **Accesibilidad**: Props de accesibilidad nativas

### Componentes Principales

- `Button`: Botón reutilizable con variantes
- `Card`: Contenedor con estilo consistente
- `ErrorBoundary`: Manejo de errores global
- `LoadingSpinner`: Indicador de carga
- `ErrorMessage`: Mensaje de error con retry

## Servicios API

### Estructura

Cada servicio (`calendar-service.ts`, `routine-service.ts`, etc.) exporta funciones que:
1. Obtienen el `artist_id` del storage
2. Construyen la URL del endpoint
3. Llaman al API client
4. Retornan datos tipados

### Manejo de Errores

- `ApiError` custom class para errores de API
- Timeout configurable
- Retry automático con React Query
- Mensajes de error user-friendly

## Validación

### Zod Schemas

- `calendarEventSchema`: Validación de eventos
- `routineTaskSchema`: Validación de rutinas
- `protocolSchema`: Validación de protocolos
- `wardrobeItemSchema`: Validación de items
- `outfitSchema`: Validación de outfits

### Uso

```typescript
import { calendarEventSchema } from '@/utils/validation';

const result = calendarEventSchema.safeParse(formData);
if (!result.success) {
  // Manejar errores de validación
}
```

## Navegación

### Expo Router

- **File-based routing**: Rutas basadas en estructura de archivos
- **Type-safe navigation**: TypeScript para navegación
- **Deep linking**: Soporte para links profundos
- **Tab navigation**: Navegación por tabs en `(tabs)/`

### Rutas Principales

- `/` - Dashboard
- `/calendar` - Calendario
- `/routines` - Rutinas
- `/wardrobe` - Vestimenta
- `/protocols` - Protocolos

## Optimizaciones

### Performance

1. **React Query Caching**
   - `staleTime`: Tiempo antes de considerar datos stale
   - `gcTime`: Tiempo antes de garbage collection
   - Cache compartido entre componentes

2. **Code Splitting**
   - Lazy loading de screens
   - Dynamic imports para componentes pesados

3. **Memoization**
   - `useMemo` para cálculos costosos
   - `useCallback` para funciones pasadas como props
   - `React.memo` para componentes puros

4. **Image Optimization**
   - `expo-image` para imágenes optimizadas
   - Lazy loading de imágenes
   - Formatos modernos (WebP)

### Bundle Size

- Tree shaking automático
- Importaciones específicas
- Code splitting por ruta

## Seguridad

### Almacenamiento

- **Secure Storage**: `react-native-encrypted-storage` para datos sensibles
  - API keys
  - Artist IDs
- **Async Storage**: Para datos no sensibles
  - Preferencias
  - Cache de UI

### API

- HTTPS obligatorio
- Autenticación con Bearer tokens
- Validación de inputs con Zod
- Sanitización de datos

## Testing

### Estrategia

1. **Unit Tests**: Funciones puras y utilidades
2. **Component Tests**: Componentes con React Native Testing Library
3. **Integration Tests**: Flujos completos con Detox
4. **E2E Tests**: Tests end-to-end críticos

## Internacionalización (i18n)

### Preparado para

- `expo-localization` para detectar idioma
- Soporte para múltiples idiomas
- RTL layouts
- Formateo de fechas y números

## Accesibilidad

### Implementado

- Labels descriptivos
- Roles ARIA donde aplica
- Contraste de colores adecuado
- Tamaños de texto escalables
- Navegación por teclado (web)

## Monitoreo y Analytics

### Preparado para

- Error tracking (Sentry)
- Analytics (Firebase, Amplitude)
- Performance monitoring
- Crash reporting

## Escalabilidad

### Consideraciones

1. **Modularidad**: Fácil agregar nuevas features
2. **Type Safety**: TypeScript previene errores
3. **Testing**: Base sólida para tests
4. **Documentación**: Código autodocumentado
5. **Performance**: Optimizado desde el inicio

## Próximos Pasos

1. Implementar pantallas de creación/edición
2. Agregar formularios con validación
3. Implementar notificaciones push
4. Agregar sincronización offline
5. Implementar búsqueda avanzada
6. Agregar filtros y ordenamiento
7. Implementar analytics
8. Agregar tests


