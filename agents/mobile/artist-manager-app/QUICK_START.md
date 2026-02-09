# Quick Start Guide

## Instalación Rápida

```bash
# 1. Instalar dependencias
cd agents/mobile/artist-manager-app
npm install

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu URL de API

# 3. Iniciar desarrollo
npm start
```

## Configuración Inicial

### 1. Configurar API Base URL

Editar `.env`:
```env
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000
```

O en `app.json`:
```json
{
  "expo": {
    "extra": {
      "apiBaseUrl": "http://your-api-url.com"
    }
  }
}
```

### 2. Configurar Artist ID

La aplicación necesita un `artist_id` para funcionar. Opciones:

**Opción A: En el código (desarrollo)**
```typescript
// En cualquier screen o hook
import { setArtistId } from '@/utils/storage';
await setArtistId('artist_001');
```

**Opción B: Pantalla de login (producción)**
Implementar pantalla de autenticación que guarde el `artist_id`.

### 3. Ejecutar la App

```bash
# iOS Simulator
npm run ios

# Android Emulator
npm run android

# Web Browser
npm run web
```

## Estructura de Navegación

La app tiene 5 tabs principales:

1. **Dashboard** (`/`) - Vista general con estadísticas
2. **Calendar** (`/calendar`) - Gestión de eventos
3. **Routines** (`/routines`) - Gestión de rutinas
4. **Wardrobe** (`/wardrobe`) - Gestión de vestimenta
5. **Protocols** (`/protocols`) - Gestión de protocolos

## Uso Básico

### Ver Dashboard

```typescript
// Ya implementado en app/(tabs)/index.tsx
import { useDashboard } from '@/hooks/use-dashboard';

function DashboardScreen() {
  const { data, isLoading, error } = useDashboard();
  // ...
}
```

### Crear un Evento

```typescript
import { useCreateCalendarEvent } from '@/hooks/use-calendar-events';

function CreateEventScreen() {
  const createMutation = useCreateCalendarEvent();
  
  const handleCreate = async () => {
    await createMutation.mutateAsync({
      title: 'Concierto',
      description: 'Concierto principal',
      event_type: 'concert',
      start_time: new Date(),
      end_time: new Date(Date.now() + 3 * 60 * 60 * 1000),
    });
  };
}
```

### Completar una Rutina

```typescript
import { useCompleteRoutine } from '@/hooks/use-routines';

function RoutineScreen() {
  const completeMutation = useCompleteRoutine();
  
  const handleComplete = (taskId: string) => {
    completeMutation.mutate({ taskId });
  };
}
```

## Hooks Disponibles

### Calendar
- `useCalendarEvents()` - Listar eventos
- `useCalendarEvent(id)` - Obtener evento específico
- `useCreateCalendarEvent()` - Crear evento
- `useUpdateCalendarEvent()` - Actualizar evento
- `useDeleteCalendarEvent()` - Eliminar evento
- `useWardrobeRecommendation(eventId)` - Recomendación de vestimenta

### Routines
- `useRoutines()` - Listar rutinas
- `useRoutine(id)` - Obtener rutina específica
- `usePendingRoutines()` - Rutinas pendientes
- `useCreateRoutine()` - Crear rutina
- `useUpdateRoutine()` - Actualizar rutina
- `useDeleteRoutine()` - Eliminar rutina
- `useCompleteRoutine()` - Completar rutina

### Dashboard
- `useDashboard()` - Datos del dashboard
- `useDailySummary()` - Resumen diario con IA

### Wardrobe
- Usar `wardrobeService` directamente o crear hooks similares

### Protocols
- Usar `protocolService` directamente o crear hooks similares

## Componentes Reutilizables

### Button
```typescript
<Button
  title="Click me"
  onPress={() => {}}
  variant="primary" // primary | secondary | outline | danger
  loading={false}
  disabled={false}
/>
```

### Card
```typescript
<Card padding={16}>
  <Text>Content</Text>
</Card>
```

### LoadingSpinner
```typescript
<LoadingSpinner size="large" fullScreen />
```

### ErrorMessage
```typescript
<ErrorMessage
  message="Something went wrong"
  onRetry={() => refetch()}
/>
```

## Validación de Formularios

```typescript
import { calendarEventSchema } from '@/utils/validation';
import { z } from 'zod';

const result = calendarEventSchema.safeParse(formData);

if (!result.success) {
  // result.error contiene los errores
  console.error(result.error.errors);
} else {
  // result.data contiene los datos validados
  await createEvent(result.data);
}
```

## Manejo de Errores

### Error Boundaries
Ya implementado en `app/_layout.tsx`. Captura errores de renderizado.

### API Errors
```typescript
import { ApiError } from '@/utils/api-client';

try {
  await calendarService.getEvents();
} catch (error) {
  if (error instanceof ApiError) {
    console.error('API Error:', error.status, error.message);
  }
}
```

### React Query Errors
```typescript
const { data, error, isLoading } = useQuery({
  queryKey: ['events'],
  queryFn: () => calendarService.getEvents(),
});

if (error) {
  // Manejar error
}
```

## Personalización

### Colores

Editar `src/constants/colors.ts`:
```typescript
export const Colors = {
  light: {
    primary: '#007AFF',
    // ...
  },
  dark: {
    primary: '#0A84FF',
    // ...
  },
};
```

### Configuración API

Editar `src/constants/config.ts`:
```typescript
export const Config = {
  apiBaseUrl: '...',
  timeout: 30000,
  // ...
};
```

## Troubleshooting

### Error: "Artist ID not found"
- Configurar `artist_id` usando `setArtistId()` desde `@/utils/storage`

### Error: "Network Error"
- Verificar que la API esté corriendo
- Verificar `EXPO_PUBLIC_API_BASE_URL` en `.env`
- Verificar que la URL sea accesible desde el dispositivo/emulador

### Error: "Module not found"
- Ejecutar `npm install`
- Verificar que los paths en `tsconfig.json` sean correctos
- Limpiar cache: `npm start -- --clear`

### TypeScript Errors
- Ejecutar `npm run type-check` para ver errores
- Verificar que todas las dependencias estén instaladas

## Próximos Pasos

1. Implementar pantallas de creación/edición
2. Agregar formularios con validación
3. Implementar notificaciones
4. Agregar sincronización offline
5. Implementar búsqueda y filtros


