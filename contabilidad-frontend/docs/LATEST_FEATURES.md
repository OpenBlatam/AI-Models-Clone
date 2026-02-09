# 🆕 Últimas Características Agregadas

## ✅ Hooks Nuevos (3 hooks)

### 1. `useGeolocation` ✅
Hook para obtener la geolocalización del usuario.

```typescript
const { latitude, longitude, accuracy, error, loading } = useGeolocation({
  enableHighAccuracy: true,
  timeout: 5000,
  watch: false,
});
```

**Características:**
- Obtiene coordenadas GPS
- Soporte para watch mode (seguimiento continuo)
- Manejo de errores completo
- Opciones configurables (accuracy, timeout, maximumAge)

**Casos de uso:**
- Detectar ubicación del usuario
- Servicios basados en ubicación
- Tracking de ubicación

### 2. `useVisibility` ✅
Hook para detectar si la página está visible o en segundo plano.

```typescript
const isVisible = useVisibility();

// Ejecutar función cuando la página se vuelve visible
useOnVisible(() => {
  refreshData();
});
```

**Funciones:**
- `useVisibility` - Detecta si la página está visible
- `useOnVisible` - Ejecuta función cuando la página se vuelve visible

**Características:**
- Detecta cambios de visibilidad
- Útil para pausar/reanudar operaciones
- Optimización de recursos

**Casos de uso:**
- Pausar polling cuando la pestaña está en segundo plano
- Refrescar datos cuando el usuario vuelve
- Optimizar uso de recursos

### 3. `useIdle` ✅
Hook para detectar si el usuario está inactivo.

```typescript
const isIdle = useIdle({
  timeout: 30000, // 30 segundos
  events: ['mousedown', 'mousemove', 'keypress'],
});

// Obtener tiempo de inactividad
const idleTime = useIdleTime({ timeout: 30000 });
```

**Funciones:**
- `useIdle` - Detecta si el usuario está inactivo
- `useIdleTime` - Obtiene tiempo de inactividad en milisegundos

**Características:**
- Timeout configurable
- Eventos personalizables
- Tiempo de inactividad preciso

**Casos de uso:**
- Cerrar sesión automática
- Mostrar mensaje de inactividad
- Pausar operaciones costosas

## ✅ Utilidades Nuevas (2 módulos)

### 1. `string-slug.ts` ✅
Utilidades para crear slugs y URLs amigables.

```typescript
slugify('Hello World!'); // "hello-world"
slugify('Café & Más', '_'); // "cafe_mas"

unslugify('hello-world'); // "Hello World"
unslugify('hello-world', false); // "hello world"

uniqueSlug('Hello', ['hello']); // "hello-2"
uniqueSlug('Hello', ['hello', 'hello-2']); // "hello-3"

isValidSlug('hello-world'); // true
isValidSlug('Hello World'); // false
```

**Funciones:**
- `slugify` - Convierte texto a slug
- `unslugify` - Convierte slug a texto
- `uniqueSlug` - Genera slug único
- `isValidSlug` - Valida slug

**Características:**
- Normalización de caracteres (acentos, diacríticos)
- Separador personalizable
- Generación de slugs únicos
- Validación de slugs

### 2. `object-pick-omit.ts` ✅
Utilidades avanzadas para seleccionar y omitir propiedades.

```typescript
pick({ a: 1, b: 2, c: 3 }, ['a', 'c']); // { a: 1, c: 3 }
omit({ a: 1, b: 2, c: 3 }, ['b']); // { a: 1, c: 3 }

pickBy({ a: 1, b: 2, c: 3 }, (value) => value > 1); // { b: 2, c: 3 }
omitBy({ a: 1, b: 2, c: 3 }, (value) => value > 1); // { a: 1 }

pickDefined({ a: 1, b: null, c: undefined }); // { a: 1 }
pickTruthy({ a: 1, b: 0, c: '' }); // { a: 1 }
```

**Funciones:**
- `pick` - Selecciona propiedades específicas
- `omit` - Omite propiedades específicas
- `pickBy` - Selecciona por condición
- `omitBy` - Omite por condición
- `pickDefined` - Selecciona propiedades definidas
- `pickTruthy` - Selecciona propiedades truthy

**Características:**
- Type-safe con TypeScript
- Funciones de predicado flexibles
- Helpers comunes (defined, truthy)

## 📊 Estadísticas Actualizadas

### Hooks
- **Total de hooks**: 37 (34 anteriores + 3 nuevos)
- **Categorías**: 6 categorías organizadas

### Utilidades
- **Total de módulos**: 93+ (91 anteriores + 2 nuevos)
- **Funciones nuevas**: 12+ funciones adicionales

## 🎯 Casos de Uso

### useGeolocation - Servicios basados en ubicación
```typescript
const { latitude, longitude } = useGeolocation();

if (latitude && longitude) {
  // Mostrar servicios cercanos
  fetchNearbyServices(latitude, longitude);
}
```

### useVisibility - Optimización de recursos
```typescript
const isVisible = useVisibility();

useEffect(() => {
  if (!isVisible) {
    // Pausar polling cuando la pestaña está en segundo plano
    pausePolling();
  } else {
    // Reanudar cuando vuelve a ser visible
    resumePolling();
  }
}, [isVisible]);
```

### useIdle - Cerrar sesión automática
```typescript
const isIdle = useIdle({ timeout: 300000 }); // 5 minutos

useEffect(() => {
  if (isIdle) {
    // Mostrar advertencia o cerrar sesión
    showIdleWarning();
  }
}, [isIdle]);
```

### string-slug - URLs amigables
```typescript
// Generar slug para URL
const slug = slugify('Asesoría Fiscal Personalizada');
// "asesoria-fiscal-personalizada"

// Validar slug antes de usar
if (isValidSlug(userInput)) {
  navigate(`/servicios/${userInput}`);
}
```

### object-pick-omit - Manipulación de objetos
```typescript
// Filtrar propiedades antes de enviar a API
const cleanData = pickDefined({
  name: 'Juan',
  email: 'juan@example.com',
  phone: null,
  address: undefined,
});
// { name: 'Juan', email: 'juan@example.com' }

// Omitir propiedades sensibles
const publicData = omit(userData, ['password', 'token']);
```

## 🚀 Beneficios

### Para Desarrolladores
- ✅ Hooks de geolocalización y visibilidad para UX mejorada
- ✅ Utilidades de slugs para URLs amigables
- ✅ Manipulación avanzada de objetos type-safe

### Para el Proyecto
- ✅ Mejor experiencia de usuario con detección de inactividad
- ✅ Optimización de recursos con detección de visibilidad
- ✅ URLs más amigables y SEO-friendly

---

**Versión**: 2.5.0  
**Fecha**: $(date)  
**Estado**: ✅ COMPLETADO











