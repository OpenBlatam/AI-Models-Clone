# 🛠️ Utilidades Completas - Documentación

## ✅ Todas las Utilidades Disponibles

### 📅 Date Helpers (`date-helpers.ts`)
Utilidades para trabajar con fechas de manera inteligente:

- `formatSmartDate()` - Formatea fechas de manera inteligente (hoy, ayer, esta semana, etc.)
- `formatRelativeDate()` - Formatea fechas relativas de manera natural
- `startOfDay()` - Obtiene el inicio del día
- `endOfDay()` - Obtiene el final del día
- `isDateInRange()` - Verifica si una fecha está en un rango
- `daysBetween()` - Calcula días entre dos fechas

**Ejemplo:**
```typescript
import { formatSmartDate, daysBetween } from '@/lib/utils';

const date = new Date();
formatSmartDate(date); // "14:30" si es hoy, "Ayer", "Lunes", etc.
daysBetween(date1, date2); // 5
```

### 📝 String Helpers (`string-helpers.ts`)
Utilidades para manipulación de strings:

- `capitalize()` - Capitaliza primera letra
- `capitalizeWords()` - Capitaliza cada palabra
- `truncate()` - Trunca strings con sufijo
- `removeAccents()` - Remueve acentos
- `slugify()` - Convierte a slug
- `formatCurrency()` - Formatea como moneda
- `formatNumber()` - Formatea números con separadores
- `extractNumbers()` - Extrae números de un string
- `isValidEmail()` - Valida emails
- `maskEmail()` - Enmascara emails

**Ejemplo:**
```typescript
import { capitalize, formatCurrency, slugify } from '@/lib/utils';

capitalize('hola mundo'); // "Hola mundo"
formatCurrency(1234.56); // "$1,234.56 MXN"
slugify('Hola Mundo!'); // "hola-mundo"
```

### 📊 Array Helpers (`array-helpers.ts`)
Utilidades para manipulación de arrays:

- `groupBy()` - Agrupa por clave
- `sortBy()` - Ordena por clave
- `unique()` - Elimina duplicados
- `uniqueBy()` - Elimina duplicados por clave
- `chunk()` - Particiona en chunks
- `find()` - Encuentra elemento
- `filter()` - Filtra elementos
- `mapFilter()` - Mapea y filtra nulos
- `sum()` - Suma valores
- `average()` - Promedio de valores

**Ejemplo:**
```typescript
import { groupBy, sortBy, chunk } from '@/lib/utils';

groupBy(tasks, 'status'); // { completed: [...], pending: [...] }
sortBy(tasks, 'createdAt', 'desc');
chunk([1,2,3,4,5], 2); // [[1,2], [3,4], [5]]
```

### 🔧 Object Helpers (`object-helpers.ts`)
Utilidades para manipulación de objetos:

- `getNestedValue()` - Obtiene valor anidado
- `setNestedValue()` - Establece valor anidado
- `omit()` - Omite propiedades
- `pick()` - Selecciona propiedades
- `deepMerge()` - Fusiona objetos profundamente
- `deepClone()` - Clona objetos profundamente
- `deepEqual()` - Compara objetos profundamente

**Ejemplo:**
```typescript
import { getNestedValue, omit, deepMerge } from '@/lib/utils';

getNestedValue(obj, 'user.profile.name'); // "Juan"
omit(user, ['password', 'token']); // { name, email, ... }
deepMerge(target, source1, source2); // Merge profundo
```

### 🛡️ Error Handling (`error-handling.ts`)
Utilidades avanzadas para manejo de errores:

- `AppError` - Clase de error personalizada
- `handleError()` - Maneja errores centralizadamente
- `withErrorHandling()` - Wrapper para funciones async
- `retryWithBackoff()` - Retry con backoff exponencial
- `withTimeout()` - Timeout para promesas

**Ejemplo:**
```typescript
import { withErrorHandling, retryWithBackoff, AppError } from '@/lib/utils';

const safeFn = withErrorHandling(async () => {
  // código que puede fallar
}, { component: 'MyComponent' });

const result = await retryWithBackoff(
  () => fetchData(),
  3, // max retries
  1000, // initial delay
  { component: 'DataFetcher' }
);
```

### 🔍 Type Guards (`type-guards.ts`)
Type guards para validación en runtime:

- `isTaskStatus()` - Verifica TaskStatus
- `isTaskResult()` - Verifica TaskResult
- `isServiceType()` - Verifica ServiceType
- `isTaskStatusType()` - Verifica TaskStatusType
- `isPositiveNumber()` - Verifica número positivo
- `isNonEmptyString()` - Verifica string no vacío
- `isValidEmail()` - Verifica email válido

**Ejemplo:**
```typescript
import { isTaskStatus, isPositiveNumber } from '@/lib/utils';

if (isTaskStatus(data)) {
  // TypeScript sabe que data es TaskStatus
  console.log(data.status);
}
```

### 🔗 Constants Helpers (`constants-helpers.ts`)
Helpers para trabajar con constantes:

- `getAllServiceIds()` - Todos los IDs de servicios
- `getServiceById()` - Servicio por ID
- `isValidService()` - Verifica servicio válido
- `getServiceName()` - Nombre de servicio
- `getStatusConfig()` - Configuración de estado
- `getAllStatusTypes()` - Todos los estados
- `isValidStatus()` - Verifica estado válido

**Ejemplo:**
```typescript
import { getServiceById, isValidService } from '@/lib/utils';

if (isValidService(serviceId)) {
  const service = getServiceById(serviceId);
  console.log(service.title);
}
```

### 📋 Component Index (`component-index.ts`)
Índice de componentes para documentación:

- `componentIndex` - Array con info de componentes
- `getComponentInfo()` - Info de un componente
- `getMemoizedComponents()` - Componentes memoizados
- `getComponentsByCategory()` - Por categoría

**Ejemplo:**
```typescript
import { getComponentInfo, getMemoizedComponents } from '@/lib/utils';

const buttonInfo = getComponentInfo('Button');
const memoized = getMemoizedComponents();
```

## 📚 Categorías de Utilidades

### Manipulación de Datos
- ✅ Arrays (groupBy, sortBy, unique, etc.)
- ✅ Objetos (deepMerge, omit, pick, etc.)
- ✅ Strings (capitalize, slugify, formatCurrency, etc.)
- ✅ Fechas (formatSmartDate, daysBetween, etc.)

### Validación y Type Safety
- ✅ Type guards (isTaskStatus, isValidEmail, etc.)
- ✅ Validación (Validator class, validation rules)
- ✅ Constants helpers (isValidService, etc.)

### Manejo de Errores
- ✅ AppError class
- ✅ Error handling centralizado
- ✅ Retry con backoff
- ✅ Timeout handling

### Utilidades de Desarrollo
- ✅ Component index
- ✅ Performance monitoring
- ✅ Logging
- ✅ Analytics

## 🎯 Uso Recomendado

### Importaciones Limpias
```typescript
// Importar todo desde el barrel export
import { 
  formatSmartDate, 
  groupBy, 
  deepMerge,
  withErrorHandling 
} from '@/lib/utils';
```

### Type Safety
```typescript
// Usar type guards para validación
if (isTaskStatus(data)) {
  // TypeScript sabe el tipo
  processTask(data);
}
```

### Error Handling
```typescript
// Usar wrappers para manejo automático de errores
const safeOperation = withErrorHandling(
  async () => await riskyOperation(),
  { component: 'MyComponent' }
);
```

## 📊 Estadísticas

- **Total de utilidades**: 50+ funciones
- **Categorías**: 8 categorías principales
- **Type-safe**: 100%
- **Documentado**: ✅
- **Testeable**: ✅

## ✨ Beneficios

- ✅ **Reutilización** - Funciones comunes centralizadas
- ✅ **Type Safety** - Type guards y validación
- ✅ **Consistencia** - Mismo comportamiento en toda la app
- ✅ **Mantenibilidad** - Fácil de actualizar y extender
- ✅ **Performance** - Funciones optimizadas
- ✅ **Documentación** - Bien documentadas

---

**Versión**: 3.1.0
**Estado**: ✅ COMPLETO












