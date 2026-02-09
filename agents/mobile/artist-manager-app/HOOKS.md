# Hooks Documentation

Documentación completa de todos los hooks disponibles en la aplicación.

## 📚 Categorías de Hooks

### 🔌 API Hooks (`hooks/api/`)
Hooks relacionados con data fetching y operaciones API.

- `useCalendarEvents` - Listar y gestionar eventos
- `useCalendarEvent` - Obtener evento específico
- `useCreateCalendarEvent` - Crear evento
- `useUpdateCalendarEvent` - Actualizar evento
- `useDeleteCalendarEvent` - Eliminar evento
- `useWardrobeRecommendation` - Recomendación de vestimenta
- `useRoutines` - Listar y gestionar rutinas
- `useRoutine` - Obtener rutina específica
- `usePendingRoutines` - Rutinas pendientes
- `useCreateRoutine` - Crear rutina
- `useUpdateRoutine` - Actualizar rutina
- `useDeleteRoutine` - Eliminar rutina
- `useCompleteRoutine` - Completar rutina
- `useDashboard` - Datos del dashboard
- `useDailySummary` - Resumen diario con IA

### 🎨 UI Hooks (`hooks/ui/`)
Hooks para UI y utilidades de interfaz.

- `useColorScheme` - Detectar tema (light/dark)
- `useToast` - Mostrar mensajes toast
- `useForm` - Manejo de formularios con validación

### 🛠️ Utility Hooks (`hooks/utils/`)
Hooks de utilidad general.

- `usePrevious` - Obtener valor anterior
- `useToggle` - Estado booleano con toggle
- `useLocalStorage` - Almacenamiento local sincronizado
- `useAsync` - Manejo de operaciones asíncronas
- `useInterval` - Ejecutar función en intervalos
- `useTimeout` - Ejecutar función después de delay
- `useMount` - Ejecutar solo en mount
- `useUnmount` - Ejecutar solo en unmount
- `useUpdateEffect` - Effect solo en updates
- `useDebounce` - Debounce de valores
- `useThrottle` - Throttle de funciones
- `useMemoCompare` - Memo con comparación custom
- `useForceUpdate` - Forzar re-render

### 🧭 Navigation Hooks (`hooks/navigation/`)
Hooks para navegación y routing.

- `useFocusEffect` - Effect cuando screen está en focus
- `useIsFocused` - Verificar si screen está en focus
- `useBackHandler` - Manejar botón back de Android
- `useDeepLink` - Manejar deep links

### 📱 Device Hooks (`hooks/device/`)
Hooks para información del dispositivo.

- `usePlatform` - Información de plataforma (iOS/Android/Web)
- `useOrientation` - Orientación del dispositivo
- `useKeyboard` - Estado del teclado
- `useAppState` - Estado de la app (active/background)
- `useSafeAreaInsets` - Insets de safe area
- `useMediaQuery` - Media queries responsive
- `useWindowDimensions` - Dimensiones de la ventana

### 📊 Data Hooks (`hooks/data/`)
Hooks para manipulación de datos.

- `useSearch` - Búsqueda y filtrado
- `useSort` - Ordenamiento de datos
- `useFilter` - Filtrado con múltiples filtros
- `usePagination` - Gestión de paginación
- `useRefreshControl` - Control de refresh

### 🎬 Media Hooks (`hooks/media/`)
Hooks para medios y permisos.

- `useImagePicker` - Seleccionar imágenes
- `useClipboard` - Operaciones de clipboard
- `usePermissions` - Gestión de permisos

### ✨ Animation Hooks (`hooks/animation/`)
Hooks para animaciones.

- `useAnimation` - Crear animaciones con Reanimated
- `useGesture` - Manejo de gestos

### ♿ Accessibility Hooks (`hooks/accessibility/`)
Hooks para accesibilidad.

- `useAccessibility` - Estado de accesibilidad del dispositivo

### 🌐 Network Hooks (`hooks/network/`)
Hooks para estado de red.

- `useNetworkStatus` - Estado completo de red
- `useOnlineStatus` - Estado online/offline simple

### 🔄 Updates Hooks (`hooks/updates/`)
Hooks para actualizaciones OTA.

- `useUpdateCheck` - Verificar y descargar updates

### 🔧 Other Hooks (`hooks/other/`)
Otros hooks útiles.

- `useCountdown` - Timer de cuenta regresiva
- `useClickOutside` - Detectar press fuera de elemento
- `useArtistId` - Gestión de artist ID

## 📖 Ejemplos de Uso

### useToggle
```typescript
import { useToggle } from '@/hooks';

function MyComponent() {
  const [isOpen, { toggle, setTrue, setFalse }] = useToggle(false);

  return (
    <View>
      <Button title="Toggle" onPress={toggle} />
      <Button title="Open" onPress={setTrue} />
      <Button title="Close" onPress={setFalse} />
    </View>
  );
}
```

### useAsync
```typescript
import { useAsync } from '@/hooks';

function MyComponent() {
  const { data, isLoading, error, execute } = useAsync(
    async () => {
      const response = await fetch('/api/data');
      return response.json();
    },
    { immediate: true }
  );

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error.message} />;

  return <Text>{JSON.stringify(data)}</Text>;
}
```

### useSearch
```typescript
import { useSearch } from '@/hooks';

function SearchComponent({ items }: { items: Item[] }) {
  const { searchQuery, setSearchQuery, filteredData } = useSearch({
    data: items,
    searchFn: (item, query) => 
      item.name.toLowerCase().includes(query.toLowerCase()),
  });

  return (
    <View>
      <TextInput
        value={searchQuery}
        onChangeText={setSearchQuery}
        placeholder="Search..."
      />
      <FlatList data={filteredData} renderItem={...} />
    </View>
  );
}
```

### usePagination
```typescript
import { usePagination } from '@/hooks';

function PaginatedList({ totalItems }: { totalItems: number }) {
  const {
    page,
    pageSize,
    totalPages,
    hasNextPage,
    hasPreviousPage,
    nextPage,
    previousPage,
  } = usePagination({ total: totalItems });

  return (
    <View>
      <FlatList data={...} />
      <View>
        <Button
          title="Previous"
          onPress={previousPage}
          disabled={!hasPreviousPage}
        />
        <Text>Page {page} of {totalPages}</Text>
        <Button
          title="Next"
          onPress={nextPage}
          disabled={!hasNextPage}
        />
      </View>
    </View>
  );
}
```

### useImagePicker
```typescript
import { useImagePicker } from '@/hooks';

function ImageUploadComponent() {
  const { image, pickImage, isLoading } = useImagePicker({
    allowsEditing: true,
    aspect: [1, 1],
    quality: 0.8,
  });

  return (
    <View>
      {image && <Image source={{ uri: image.uri }} />}
      <Button
        title="Pick Image"
        onPress={() => pickImage('gallery')}
        loading={isLoading}
      />
    </View>
  );
}
```

### useAnimation
```typescript
import { useAnimation } from '@/hooks';
import Animated from 'react-native-reanimated';

function AnimatedComponent() {
  const { animatedValue, fadeIn, fadeOut } = useAnimation(0);

  const style = useAnimatedStyle(() => ({
    opacity: animatedValue.value,
  }));

  return (
    <Animated.View style={style}>
      <Button title="Fade In" onPress={fadeIn} />
      <Button title="Fade Out" onPress={fadeOut} />
    </Animated.View>
  );
}
```

### useKeyboard
```typescript
import { useKeyboard } from '@/hooks';

function FormComponent() {
  const { isVisible, height } = useKeyboard();

  return (
    <View style={{ paddingBottom: isVisible ? height : 0 }}>
      <TextInput placeholder="Enter text" />
    </View>
  );
}
```

### useCountdown
```typescript
import { useCountdown } from '@/hooks';

function TimerComponent() {
  const { seconds, isRunning, start, pause, reset, isComplete } = useCountdown({
    initialSeconds: 60,
    onComplete: () => {
      console.log('Timer completed!');
    },
  });

  return (
    <View>
      <Text>{seconds}s</Text>
      <Button title="Start" onPress={start} disabled={isRunning} />
      <Button title="Pause" onPress={pause} disabled={!isRunning} />
      <Button title="Reset" onPress={reset} />
    </View>
  );
}
```

### useRefreshControl
```typescript
import { useRefreshControl } from '@/hooks';
import { FlatList } from 'react-native';

function RefreshableList() {
  const { refreshing, onRefresh } = useRefreshControl(async () => {
    await refetchData();
  });

  return (
    <FlatList
      data={data}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    />
  );
}
```

### usePlatform
```typescript
import { usePlatform } from '@/hooks';

function PlatformSpecificComponent() {
  const { isIOS, isAndroid, platform } = usePlatform();

  return (
    <View>
      {isIOS && <Text>iOS specific content</Text>}
      {isAndroid && <Text>Android specific content</Text>}
    </View>
  );
}
```

### useAccessibility
```typescript
import { useAccessibility } from '@/hooks';

function AccessibleComponent() {
  const {
    isScreenReaderEnabled,
    reduceMotionEnabled,
    announceForAccessibility,
  } = useAccessibility();

  const handlePress = () => {
    if (isScreenReaderEnabled) {
      announceForAccessibility('Button pressed');
    }
  };

  return <Button title="Press me" onPress={handlePress} />;
}
```

## 🎯 Mejores Prácticas

### 1. Usar hooks específicos
```typescript
// ✅ Bueno
import { useToggle } from '@/hooks';

// ❌ Evitar
import { useState } from 'react';
const [isOpen, setIsOpen] = useState(false);
```

### 2. Combinar hooks cuando sea necesario
```typescript
const { searchQuery, filteredData } = useSearch({...});
const { sortedData } = useSort({ data: filteredData });
const { paginatedData } = usePagination({ data: sortedData });
```

### 3. Memoizar callbacks
Los hooks ya están optimizados, pero asegúrate de pasar funciones estables cuando sea necesario.

### 4. Manejar estados de carga
```typescript
const { data, isLoading, error } = useAsync(...);

if (isLoading) return <LoadingSpinner />;
if (error) return <ErrorMessage message={error.message} />;
```

## 📝 Notas

- Todos los hooks están tipados con TypeScript
- Los hooks están optimizados para performance
- Siguen las mejores prácticas de React
- Son reutilizables y composables

## 🔄 Actualizaciones

Los hooks se actualizan constantemente. Revisa este documento para las últimas versiones y ejemplos.

