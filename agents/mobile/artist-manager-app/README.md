# Artist Manager Mobile App

Aplicación móvil React Native con Expo para gestión integral de artistas. Replica toda la funcionalidad del backend con una arquitectura moderna y optimizada.

## Características

- 📅 **Gestión de Calendarios**: Visualización y gestión de eventos
- 🔄 **Gestión de Rutinas**: Seguimiento de rutinas diarias y semanales
- 📋 **Protocolos de Comportamiento**: Visualización y gestión de protocolos
- 👔 **Gestión de Vestimenta**: Gestión de items y outfits
- 📊 **Dashboard**: Vista general con estadísticas y resumen diario
- 🌙 **Dark Mode**: Soporte automático para modo oscuro
- ⚡ **Optimizado**: React Query para caching y sincronización
- 🔒 **Seguro**: Almacenamiento encriptado para datos sensibles
- 📱 **Responsive**: Diseño adaptativo para diferentes tamaños de pantalla

## Tecnologías

### Core
- **Expo** ~51.0.0
- **React Native** 0.74.0
- **TypeScript** 5.3.3
- **Expo Router** 3.5.0 (File-based routing)

### State & Data
- **React Query** 5.28.0 (Data fetching & caching)
- **Zustand** 4.5.0 (State management)
- **React Hook Form** 7.51.0 (Form management)

### UI & Animations
- **React Native Reanimated** 3.10.0 (Animations)
- **React Native Gesture Handler** 2.16.0
- **Expo Haptics** 13.0.0 (Haptic feedback)
- **React Native Toast Message** 2.2.0 (Toast notifications)

### Validation & Utils
- **Zod** 3.22.4 (Schema validation)
- **date-fns** 3.3.1 (Date manipulation)
- **i18n-js** 4.4.3 (Internationalization)

### Expo Modules
- **expo-updates** 0.25.0 (OTA updates)
- **expo-error-reporter** 1.0.0 (Error reporting)
- **expo-blur** 13.0.0 (Blur effects)
- **expo-linear-gradient** 13.0.0 (Gradients)

## Instalación

```bash
# Instalar dependencias
npm install

# Iniciar desarrollo
npm start

# Ejecutar en iOS
npm run ios

# Ejecutar en Android
npm run android

# Ejecutar en Web
npm run web
```

## Configuración

### Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000
```

O configurar en `app.json`:

```json
{
  "expo": {
    "extra": {
      "apiBaseUrl": "http://your-api-url.com"
    }
  }
}
```

### Configuración de Artista

La aplicación requiere un `artist_id` para funcionar. Esto se puede configurar en:
- Pantalla de autenticación (si se implementa)
- Almacenamiento local encriptado

## Estructura del Proyecto

```
artist-manager-app/
├── app/                    # Expo Router (file-based routing)
│   ├── (tabs)/            # Tab navigation screens
│   │   ├── _layout.tsx   # Tab layout
│   │   ├── index.tsx      # Dashboard
│   │   ├── calendar.tsx   # Calendar screen
│   │   ├── routines.tsx   # Routines screen
│   │   ├── wardrobe.tsx   # Wardrobe screen
│   │   └── protocols.tsx  # Protocols screen
│   └── _layout.tsx        # Root layout
├── src/
│   ├── components/        # Componentes reutilizables
│   │   ├── ui/           # UI Components (Button, Card, etc.)
│   │   ├── layout/       # Layout Components (ErrorBoundary, etc.)
│   │   └── index.ts      # Barrel exports
│   ├── providers/        # Context Providers
│   │   ├── app-provider.tsx
│   │   └── index.ts
│   ├── context/          # React Contexts
│   │   ├── theme-context.tsx
│   │   └── index.ts
│   ├── hooks/            # Custom hooks
│   │   ├── api/          # API hooks
│   │   ├── ui/           # UI hooks
│   │   └── index.ts      # Barrel exports
│   ├── services/         # API Services
│   │   ├── base-service.ts
│   │   ├── calendar-service.ts
│   │   ├── routine-service.ts
│   │   ├── dashboard-service.ts
│   │   ├── wardrobe-service.ts
│   │   ├── protocol-service.ts
│   │   └── index.ts      # Barrel exports
│   ├── store/            # Zustand stores
│   │   └── auth-store.ts
│   ├── types/            # TypeScript types
│   │   ├── domain.ts     # Domain types
│   │   ├── api.ts        # API types
│   │   ├── schemas.ts    # Schema types
│   │   └── index.ts      # Barrel exports
│   ├── utils/            # Utilidades
│   │   ├── api-client.ts
│   │   ├── storage.ts
│   │   ├── validation.ts
│   │   ├── format.ts
│   │   ├── logger.ts
│   │   ├── haptics.ts
│   │   ├── i18n.ts
│   │   ├── error-reporter.ts
│   │   ├── lazy-load.ts
│   │   └── index.ts      # Barrel exports
│   └── constants/        # Constantes
│       ├── colors.ts
│       ├── config.ts
│       └── index.ts      # Barrel exports
├── assets/               # Imágenes y recursos
└── package.json
```

Ver `ARCHITECTURE_V2.md` para detalles completos de la arquitectura.

## Arquitectura

### State Management

- **React Query**: Para data fetching, caching y sincronización con el servidor
- **Zustand**: Para estado global de autenticación y preferencias
- **Local State**: useState/useReducer para estado local de componentes

### API Client

Cliente HTTP centralizado con:
- Manejo de errores robusto
- Timeout configurable
- Autenticación automática
- Tipado TypeScript completo

### Componentes

Componentes reutilizables siguiendo principios:
- Composición sobre herencia
- Props tipadas con TypeScript
- Soporte para dark mode
- Accesibilidad (a11y)

### Navegación

Expo Router con:
- File-based routing
- Type-safe navigation
- Deep linking support
- Tab navigation

## Uso

### Dashboard

Vista principal con:
- Estadísticas generales
- Eventos próximos
- Resumen diario (con IA)

### Calendario

- Ver todos los eventos
- Crear nuevos eventos
- Editar eventos existentes
- Eliminar eventos
- Obtener recomendaciones de vestimenta

### Rutinas

- Ver todas las rutinas
- Ver rutinas pendientes
- Completar rutinas
- Crear nuevas rutinas

### Vestimenta

- Gestionar items del guardarropa
- Crear y gestionar outfits
- Ver historial de uso

### Protocolos

- Ver todos los protocolos
- Verificar cumplimiento
- Crear nuevos protocolos

## Optimizaciones

- **React Query Caching**: Cache inteligente con staleTime y gcTime
- **Lazy Loading**: Componentes cargados bajo demanda
- **Memoization**: useMemo y useCallback para evitar re-renders
- **Image Optimization**: expo-image para imágenes optimizadas
- **Code Splitting**: Separación de código por rutas

## Testing

```bash
# Ejecutar tests
npm test

# Tests en modo watch
npm run test:watch

# Type checking
npm run type-check
```

## Build y Deploy

```bash
# Build para producción
eas build --platform ios
eas build --platform android

# Publicar actualizaciones OTA
eas update
```

## Mejores Prácticas Implementadas

✅ **TypeScript strict mode** - Type safety completo
✅ **Error boundaries** - Manejo global de errores
✅ **Safe area handling** - SafeAreaView y SafeAreaScrollView
✅ **Dark mode support** - Soporte automático con useColorScheme
✅ **Responsive design** - useWindowDimensions para adaptación
✅ **Accessibility (a11y)** - ARIA roles, labels, hints
✅ **Performance optimization** - React Query, memoization, lazy loading
✅ **Secure storage** - react-native-encrypted-storage
✅ **Code splitting** - Separación por rutas
✅ **Lazy loading** - Componentes bajo demanda
✅ **Animations** - React Native Reanimated para animaciones fluidas
✅ **Network status** - Detección de conexión offline
✅ **Logging** - Sistema de logging estructurado
✅ **Internationalization** - Soporte multi-idioma (i18n)
✅ **Debouncing** - Hook para optimizar búsquedas
✅ **Gesture handling** - React Native Gesture Handler
✅ **Font loading** - Carga optimizada de fuentes
✅ **Splash screen** - Manejo mejorado del splash
✅ **Form management** - React Hook Form con validación Zod
✅ **Toast notifications** - Mensajes toast con feedback háptico
✅ **Haptic feedback** - Feedback táctil en interacciones
✅ **Error reporting** - Sistema de reporte de errores
✅ **OTA updates** - Actualizaciones over-the-air
✅ **Gradients & Blur** - Efectos visuales avanzados
✅ **Enhanced linting** - ESLint con reglas React Native
✅ **Testing setup** - Jest con React Native Testing Library
✅ **50+ Custom Hooks** - Hooks útiles para desarrollo móvil
✅ **Organized Architecture** - Estructura modular con barrel exports

## Licencia

Propietaria - Blatam Academy

## Autor

Blatam Academy

