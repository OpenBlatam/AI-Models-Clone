# 📁 Estructura del Proyecto - Contabilidad Mexicana AI Frontend

## 🎯 Visión General

Frontend de calidad enterprise para el sistema de Contabilidad Mexicana AI, construido con Next.js 15.4, TypeScript, y Tailwind CSS.

## 📂 Estructura de Directorios

```
contabilidad-frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx          # Layout principal
│   ├── page.tsx            # Página principal
│   └── globals.css         # Estilos globales
│
├── components/             # Componentes React
│   ├── ui/                 # Componentes UI base (barrel export)
│   ├── forms/              # Formularios de servicios
│   └── [componentes].tsx   # Componentes individuales
│
├── lib/                    # Librerías y utilidades
│   ├── api-client.ts       # Cliente API
│   ├── config/              # Configuración
│   │   ├── env.ts          # Variables de entorno
│   │   └── features.ts     # Feature flags
│   ├── constants/          # Constantes
│   │   ├── services.ts     # Servicios disponibles
│   │   ├── task-status.ts  # Estados de tareas
│   │   └── commands.ts     # Comandos de la app
│   ├── hooks/              # Custom hooks
│   │   └── index.ts        # Barrel export de hooks
│   ├── services/           # Servicios centralizados
│   │   ├── analyticsService.ts
│   │   ├── cacheService.ts
│   │   ├── logger.ts
│   │   ├── storageService.ts
│   │   └── taskService.ts
│   └── utils/              # Utilidades (85+ módulos)
│       └── index.ts        # Barrel export de utilidades
│
├── types/                  # TypeScript types
│   ├── api.ts              # Tipos de API
│   ├── common.ts           # Tipos comunes
│   └── index.ts            # Barrel export de tipos
│
└── docs/                   # Documentación
    └── PROJECT_STRUCTURE.md # Este archivo
```

## 🧩 Componentes

### Componentes UI Base
- `Button`, `Input`, `Card`, `Badge`
- `FormField`, `Tooltip`, `LoadingSpinner`
- `ProgressBar`, `EmptyState`, `ConfirmDialog`
- `StatusIndicator`, `CopyButton`

### Componentes Avanzados
- `Dashboard` - Panel principal
- `TaskMonitor` - Monitoreo de tareas
- `ResultViewer` - Visualizador de resultados
- `CommandPalette` - Paleta de comandos
- `NotificationCenter` - Centro de notificaciones
- `AdvancedSearch` - Búsqueda avanzada
- `DataTable` - Tabla de datos
- `CalendarView` - Vista de calendario

### Formularios de Servicios
- `AsesoriaFiscalForm`
- `CalcularImpuestosForm`
- `AyudaDeclaracionForm`
- `TramiteSATForm`
- `GuiaFiscalForm`

## 🎣 Hooks Personalizados (26)

### Hooks de Estado
- `useLocalStorage` - localStorage con sincronización
- `useToggle` - Toggle booleano
- `useCounter` - Contador
- `usePrevious` - Valor anterior

### Hooks de UI
- `useDarkMode` - Modo oscuro
- `useMediaQuery` - Media queries
- `useClickOutside` - Click fuera
- `useHover` - Estado hover
- `useFocus` - Estado focus
- `useWindowSize` - Tamaño de ventana

### Hooks de Performance
- `useDebounce` - Debounce
- `useThrottle` - Throttle
- `useCachedRequest` - Request con caché
- `usePerformance` - Métricas de performance

### Hooks de Tareas
- `useTaskPolling` - Polling de tareas
- `useTaskHistory` - Historial de tareas
- `useServiceForm` - Formulario de servicio

### Hooks Avanzados
- `useAccessibility` - Accesibilidad
- `useAnalytics` - Analytics
- `useErrorHandler` - Manejo de errores
- `useNotifications` - Notificaciones
- `useAutoSave` - Auto-guardado
- `useFavorites` - Favoritos
- `useTranslation` - Internacionalización
- `useFeatureFlag` - Feature flags
- `useHealthCheck` - Health check
- `useOnlineStatus` - Estado online
- `usePreferences` - Preferencias
- `useAppCommands` - Comandos de app
- `useAppKeyboardShortcuts` - Atajos de teclado
- `useFocusTrap` - Focus trap
- `useIntersectionObserver` - Intersection Observer
- `useAsync` - Operaciones asíncronas
- `useTimeout` - Timeout
- `useInterval` - Interval

## 🛠️ Utilidades (85+ Módulos)

### Categorías Principales

1. **Error Handling** (2 módulos)
   - `error-handling`, `errorMessages`

2. **Export y Formateo** (5 módulos)
   - `export`, `export-advanced`, `formatDate`, `format-helpers`, `format-advanced`, `formatting-helpers`

3. **Performance** (6 módulos)
   - `memo`, `performance`, `performance-advanced`, `react-optimization`, `debounce-throttle`, `optimization-helpers`

4. **Validación** (4 módulos)
   - `validation`, `validation-advanced`, `validation-fiscal`, `type-guards`

5. **Manipulación de Datos** (12 módulos)
   - `array-helpers`, `object-helpers`, `string-helpers`, `string-advanced`
   - `date-helpers`, `time-helpers`, `number-helpers`, `math-helpers`
   - `collection-helpers`, `transform-helpers`, `sort-helpers`, `filter-helpers`

6. **Fiscal Mexicano** (7 módulos)
   - `currency-helpers`, `tax-helpers`, `fiscal-helpers`, `date-fiscal`
   - `report-helpers`, `calculation-helpers`, `constants-fiscal`

7. **Visualización** (4 módulos)
   - `chart-helpers`, `table-helpers`, `import-helpers`, `export-advanced`

8. **Seguridad** (2 módulos)
   - `security-helpers`, `security-advanced`

9. **Monitoreo** (1 módulo)
   - `monitoring-helpers`

10. **Otros** (40+ módulos)
    - Accesibilidad, SEO, DOM, Eventos, Regex, IDs, Animaciones
    - Promises, Async, Batch, Stream, Iterator, Queue, Cache
    - Estado, Observables, Funcional, Logging, Paginación
    - Muestreo, Codificación, Búsqueda, Agrupación, Diferencias
    - Merge, Storage, URL, Query, Form, Color, Theme, Copy, File

## 🔧 Servicios

### `analyticsService`
- Tracking de eventos
- Métricas de uso
- Análisis de comportamiento

### `cacheService`
- Caché en memoria
- LRU cache
- TTL support

### `logger`
- Logging centralizado
- Niveles de log
- Formateo de logs

### `storageService`
- localStorage wrapper
- Sincronización cross-tab
- Migración de datos

### `taskService`
- Gestión de tareas
- Polling automático
- Historial de tareas

## 📊 Estadísticas

- **Componentes**: 50+
- **Hooks**: 26
- **Utilidades**: 85+ módulos, 400+ funciones
- **Servicios**: 5
- **Tipos**: 100% TypeScript
- **Linting**: 0 errores

## 🚀 Próximos Pasos

1. Agregar tests unitarios
2. Implementar Storybook
3. Agregar E2E tests
4. Optimizar bundle size
5. Implementar PWA












