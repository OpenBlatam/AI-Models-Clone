# Resumen de Hooks

## 📊 Estadísticas

- **Total de Hooks**: 50+
- **Categorías**: 10
- **Cobertura**: Completa para desarrollo móvil

## 📁 Categorías

### 🔌 API Hooks (13 hooks)
Hooks para data fetching y operaciones API con React Query.

### 🎨 UI Hooks (3 hooks)
Hooks para UI, formularios y toasts.

### 🛠️ Utility Hooks (17 hooks)
Hooks de utilidad: estado, timers, comparación, estructuras de datos.

### 🧭 Navigation Hooks (4 hooks)
Hooks para navegación, focus, deep linking.

### 📱 Device Hooks (8 hooks)
Hooks para información del dispositivo: plataforma, orientación, teclado, etc.

### 📊 Data Hooks (5 hooks)
Hooks para manipulación de datos: búsqueda, ordenamiento, filtrado, paginación.

### 🎬 Media Hooks (3 hooks)
Hooks para medios: imágenes, clipboard, permisos.

### ✨ Animation Hooks (2 hooks)
Hooks para animaciones con Reanimated y gestos.

### ♿ Accessibility Hooks (1 hook)
Hooks para accesibilidad.

### 🌐 Network Hooks (2 hooks)
Hooks para estado de red.

### 🔄 Updates Hooks (1 hook)
Hooks para OTA updates.

### 🔧 Other Hooks (4 hooks)
Otros hooks útiles: countdown, click outside, etc.

## 🎯 Hooks Más Útiles

### Top 10 Hooks Recomendados

1. **useToggle** - Estado booleano con toggle
2. **useDebounce** - Debounce para búsquedas
3. **useAsync** - Manejo de operaciones asíncronas
4. **useSearch** - Búsqueda y filtrado
5. **usePagination** - Paginación
6. **useImagePicker** - Seleccionar imágenes
7. **useKeyboard** - Estado del teclado
8. **usePlatform** - Detección de plataforma
9. **useToast** - Mensajes toast
10. **useAnimation** - Animaciones

## 💡 Ejemplos Rápidos

### useToggle
```typescript
const [isOpen, { toggle }] = useToggle();
```

### useDebounce
```typescript
const debouncedValue = useDebounce(value, 300);
```

### useAsync
```typescript
const { data, isLoading, error, execute } = useAsync(fetchData);
```

### useSearch
```typescript
const { filteredData, searchQuery, setSearchQuery } = useSearch({
  data: items,
  searchFn: (item, query) => item.name.includes(query),
});
```

### usePagination
```typescript
const { page, nextPage, hasNextPage } = usePagination({ total: 100 });
```

## 🔍 Búsqueda de Hooks

Para encontrar un hook específico, busca por categoría en `HOOKS.md` o revisa los barrel exports en cada carpeta de hooks.

