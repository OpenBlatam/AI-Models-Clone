# Refactorización V23 - Resumen

## Fecha
Diciembre 2024

## Objetivo
Agregar utilidades avanzadas para operaciones de conjuntos, transformación de objetos, extracción de strings y composición de funciones.

## Nuevas Utilidades (5 módulos)

### 1. `array-union.ts` - Operaciones de Unión de Arrays
Utilidades para combinar arrays eliminando duplicados.

**Funciones:**
- `union<T>(...arrays: T[][]): T[]` - Combina múltiples arrays eliminando duplicados
- `unionBy<T>(arrays: T[][], comparator: (a: T, b: T) => boolean): T[]` - Unión con comparador personalizado
- `unionByKey<T, K>(arrays: T[][], keySelector: (item: T) => K): T[]` - Unión basada en clave
- `unionOrdered<T>(...arrays: T[][]): T[]` - Unión manteniendo orden y eliminando duplicados consecutivos
- `unionWithCount<T>(...arrays: T[][]): Map<T, number>` - Unión con conteo de ocurrencias

**Casos de uso:**
```typescript
import { union, unionByKey, unionWithCount } from '@/lib/utils';

// Combinar arrays únicos
const result = union([1, 2, 3], [2, 3, 4], [3, 4, 5]);
// [1, 2, 3, 4, 5]

// Unión por clave
const users1 = [{ id: 1, name: 'A' }, { id: 2, name: 'B' }];
const users2 = [{ id: 2, name: 'B' }, { id: 3, name: 'C' }];
const unique = unionByKey([users1, users2], u => u.id);
// [{ id: 1, name: 'A' }, { id: 2, name: 'B' }, { id: 3, name: 'C' }]

// Contar ocurrencias
const counts = unionWithCount([1, 2], [2, 3], [2, 4]);
// Map { 1 => 1, 2 => 3, 3 => 1, 4 => 1 }
```

### 2. `array-intersection.ts` - Operaciones de Intersección de Arrays
Utilidades para encontrar elementos comunes entre arrays.

**Funciones:**
- `intersection<T>(...arrays: T[][]): T[]` - Elementos comunes en todos los arrays
- `intersectionBy<T>(arrays: T[][], comparator: (a: T, b: T) => boolean): T[]` - Intersección con comparador
- `intersectionByKey<T, K>(arrays: T[][], keySelector: (item: T) => K): T[]` - Intersección por clave
- `difference<T>(firstArray: T[], ...arrays: T[][]): T[]` - Elementos únicos del primer array
- `differenceBy<T>(firstArray: T[], arrays: T[][], comparator: (a: T, b: T) => boolean): T[]` - Diferencia con comparador
- `differenceByKey<T, K>(firstArray: T[], arrays: T[][], keySelector: (item: T) => K): T[]` - Diferencia por clave
- `symmetricDifference<T>(...arrays: T[][]): T[]` - Diferencia simétrica (XOR)

**Casos de uso:**
```typescript
import { intersection, difference, symmetricDifference } from '@/lib/utils';

// Elementos comunes
const common = intersection([1, 2, 3], [2, 3, 4], [3, 4, 5]);
// [3]

// Diferencia
const unique = difference([1, 2, 3, 4], [2, 3], [4]);
// [1]

// Diferencia simétrica (XOR)
const xor = symmetricDifference([1, 2], [2, 3], [3, 4]);
// [1, 4] (elementos que aparecen en exactamente un array)
```

### 3. `object-transform.ts` - Transformaciones Avanzadas de Objetos
Utilidades para transformar objetos de manera funcional.

**Funciones:**
- `transformKeys<T>(obj: T, keyTransformer: (key: string) => string): Record<string, any>` - Transforma claves
- `transformValues<T, R>(obj: T, valueTransformer: (value: any, key: string) => R): Record<string, R>` - Transforma valores
- `transformEntries<T, K, V>(obj: T, transformer: (key: string, value: any) => [K, V]): Record<K, V>` - Transforma claves y valores
- `invert<T>(obj: T): Record<string, string>` - Invierte claves y valores
- `groupByValue<T, K>(obj: T, grouper: (value: any, key: string) => K): Record<K, any[]>` - Agrupa valores
- `mapObject<T, R>(obj: T, mapper: (key: string, value: any) => R): R[]` - Mapea objeto a array
- `filterObject<T>(obj: T, predicate: (key: string, value: any) => boolean): Partial<T>` - Filtra objeto
- `reduceObject<T, R>(obj: T, reducer: (acc: R, key: string, value: any) => R, initialValue: R): R` - Reduce objeto
- `fromArray<T, K, V>(array: T[], keySelector: (item: T, index: number) => K, valueSelector?: (item: T, index: number) => V): Record<K, V>` - Crea objeto desde array

**Casos de uso:**
```typescript
import { transformKeys, transformValues, invert, fromArray } from '@/lib/utils';

// Transformar claves a mayúsculas
const obj = { name: 'John', age: 30 };
const upperKeys = transformKeys(obj, k => k.toUpperCase());
// { NAME: 'John', AGE: 30 }

// Transformar valores
const doubled = transformValues(obj, v => typeof v === 'number' ? v * 2 : v);
// { name: 'John', age: 60 }

// Invertir objeto
const inverted = invert({ a: '1', b: '2' });
// { '1': 'a', '2': 'b' }

// Crear objeto desde array
const users = [{ id: 1, name: 'A' }, { id: 2, name: 'B' }];
const userMap = fromArray(users, u => u.id, u => u.name);
// { 1: 'A', 2: 'B' }
```

### 4. `string-extract.ts` - Extracción de Información de Strings
Utilidades para extraer información específica de strings.

**Funciones:**
- `extractNumbers(str: string): number[]` - Extrae todos los números
- `extractIntegers(str: string): number[]` - Extrae todos los enteros
- `extractWords(str: string): string[]` - Extrae todas las palabras
- `extractUrls(str: string): string[]` - Extrae todas las URLs
- `extractEmails(str: string): string[]` - Extrae todos los emails
- `extractMentions(str: string): string[]` - Extrae menciones (@username)
- `extractHashtags(str: string): string[]` - Extrae hashtags (#tag)
- `extractByPattern(str: string, pattern: RegExp): string[]` - Extrae por patrón regex
- `extractFirstNumber(str: string): number | null` - Extrae el primer número
- `extractLastNumber(str: string): number | null` - Extrae el último número
- `extractBetween(str: string, startDelimiter: string, endDelimiter: string): string[]` - Extrae entre delimitadores
- `extractInParentheses(str: string): string[]` - Extrae entre paréntesis
- `extractInBrackets(str: string): string[]` - Extrae entre corchetes
- `extractInBraces(str: string): string[]` - Extrae entre llaves

**Casos de uso:**
```typescript
import { extractNumbers, extractEmails, extractHashtags, extractBetween } from '@/lib/utils';

// Extraer números
const numbers = extractNumbers('Price: $123.45 and $67.89');
// [123.45, 67.89]

// Extraer emails
const emails = extractEmails('Contact: john@example.com or jane@test.com');
// ['john@example.com', 'jane@test.com']

// Extraer hashtags
const tags = extractHashtags('Check out #react #typescript #nextjs');
// ['#react', '#typescript', '#nextjs']

// Extraer entre delimitadores
const content = extractBetween('Hello [world] and [universe]', '[', ']');
// ['world', 'universe']
```

### 5. `function-compose.ts` - Composición de Funciones
Utilidades para composición y manipulación de funciones.

**Funciones:**
- `compose<T>(...functions: T[]): T` - Compone funciones de derecha a izquierda
- `pipe<T>(...functions: T[]): T` - Compone funciones de izquierda a derecha (pipe)
- `juxt<T, R>(...functions: ((value: T) => R)[]): (value: T) => R[]` - Aplica múltiples funciones
- `spread<T, R>(fn: (...args: T[]) => R): (args: T[]) => R` - Convierte función a tomar array
- `flip<T1, T2, R>(fn: (a: T1, b: T2) => R): (b: T2, a: T1) => R` - Invierte argumentos
- `partial<T>(fn: T, ...args: Partial<Parameters<T>>): (...remainingArgs: any[]) => ReturnType<T>` - Aplica argumentos parciales
- `partialRight<T>(fn: T, ...args: any[]): (...remainingArgs: any[]) => ReturnType<T>` - Aplica argumentos desde la derecha
- `memoize<T>(fn: T, keyGenerator?: (...args: Parameters<T>) => string): T` - Memoiza función
- `once<T>(fn: T): T` - Ejecuta función solo una vez
- `after<T>(n: number, fn: T): T` - Ejecuta después de n llamadas
- `before<T>(n: number, fn: T): T` - Ejecuta solo antes de n llamadas
- `wrap<T>(fn: T, beforeFn?: (...args: Parameters<T>) => void, afterFn?: (result: ReturnType<T>) => void): T` - Envuelve función

**Casos de uso:**
```typescript
import { compose, pipe, memoize, once, partial } from '@/lib/utils';

// Composición
const add1 = (x: number) => x + 1;
const multiply2 = (x: number) => x * 2;
const composed = compose(multiply2, add1);
composed(5); // (5 + 1) * 2 = 12

// Pipe
const piped = pipe(add1, multiply2);
piped(5); // (5 + 1) * 2 = 12

// Memoización
const expensiveFn = memoize((n: number) => {
  // cálculo costoso
  return n * n;
});

// Ejecutar una vez
const init = once(() => {
  console.log('Initialized');
});

// Parcial
const add = (a: number, b: number) => a + b;
const add10 = partial(add, 10);
add10(5); // 15
```

## Estadísticas

### Antes
- Utilidades: 188 módulos
- Funciones: 1013+

### Después
- Utilidades: 193 módulos (+5)
- Funciones: 1050+ (+37)

## Beneficios

1. **Operaciones de Conjuntos**: Unión e intersección de arrays con múltiples variantes
2. **Transformación Funcional**: Manipulación de objetos de manera inmutable y funcional
3. **Extracción de Datos**: Herramientas para extraer información específica de strings
4. **Composición de Funciones**: Utilidades para programación funcional avanzada
5. **Type Safety**: Todas las funciones están completamente tipadas con TypeScript

## Integración

Todas las nuevas utilidades están disponibles a través del barrel export:

```typescript
import {
  union,
  intersection,
  transformKeys,
  extractNumbers,
  compose,
  pipe
} from '@/lib/utils';
```

## Archivos Modificados

- `lib/utils/array-union.ts` (nuevo)
- `lib/utils/array-intersection.ts` (nuevo)
- `lib/utils/object-transform.ts` (nuevo)
- `lib/utils/string-extract.ts` (nuevo)
- `lib/utils/function-compose.ts` (nuevo)
- `lib/utils/index.ts` (actualizado)
- `README.md` (actualizado)

## Próximos Pasos

- Considerar agregar más utilidades de programación funcional
- Agregar tests unitarios para las nuevas funciones
- Documentar casos de uso avanzados










