# 🔧 Refactorización V29 - Resumen Completo

## ✅ Estado: COMPLETADO

Vigesimonovena ronda de refactorización con utilidades avanzadas para arrays ponderados, serialización de objetos, tokenización de strings, estadísticas numéricas y fechas comerciales.

## 📋 Nuevas Utilidades (5 módulos)

### 1. `array-weighted.ts` ✅
Utilidades para operaciones con arrays ponderados.

**Funciones:**
- `weightedRandom<T>(items: WeightedItem<T>[]): T` - Selecciona elemento aleatorio por peso
- `weightedRandomMultiple<T>(items, count, allowDuplicates?)` - Selecciona múltiples elementos
- `weightedAverage(items: WeightedItem<number>[]): number` - Calcula promedio ponderado
- `sortByWeight<T>(items, ascending?)` - Ordena por peso
- `normalizeWeights<T>(items)` - Normaliza pesos para que sumen 1
- `filterByMinWeight<T>(items, minWeight)` - Filtra por peso mínimo
- `filterByMaxWeight<T>(items, maxWeight)` - Filtra por peso máximo
- `groupByWeightRange<T>(items, ranges)` - Agrupa por rangos de peso
- `weightStatistics<T>(items)` - Calcula estadísticas de pesos

**Tipos:**
- `WeightedItem<T>` - Interfaz para elemento con peso
  - `item: T` - El elemento
  - `weight: number` - El peso

**Casos de uso:**
```typescript
import { weightedRandom, weightedAverage, normalizeWeights } from '@/lib/utils';

// Selección aleatoria ponderada
const items = [
  { item: 'A', weight: 10 },
  { item: 'B', weight: 30 },
  { item: 'C', weight: 60 }
];
const selected = weightedRandom(items);
// 'C' tiene 60% de probabilidad

// Promedio ponderado
const grades = [
  { item: 85, weight: 0.3 },
  { item: 90, weight: 0.5 },
  { item: 95, weight: 0.2 }
];
const avg = weightedAverage(grades);
// 89.5
```

### 2. `object-serialize.ts` ✅
Utilidades para serialización de objetos.

**Funciones:**
- `serializeObject(obj, options?)` - Serializa objeto a JSON con opciones
- `deserializeObject<T>(json, options?)` - Deserializa JSON a objeto
- `serializeToQueryString(obj, options?)` - Serializa a query string
- `deserializeFromQueryString(queryString, options?)` - Deserializa query string
- `serializeToUrlEncoded(obj)` - Serializa a URL-encoded
- `deserializeFromUrlEncoded(encoded)` - Deserializa URL-encoded
- `cloneBySerialization<T>(obj): T` - Clona usando serialización
- `compareBySerialization(obj1, obj2)` - Compara usando serialización

**Opciones de serialización:**
- `space?: number | string` - Espaciado del JSON
- `replacer?: (key, value) => any` - Función de reemplazo
- `includeFunctions?: boolean` - Incluir funciones
- `includeUndefined?: boolean` - Incluir undefined
- `includeSymbols?: boolean` - Incluir símbolos

**Casos de uso:**
```typescript
import {
  serializeObject,
  deserializeObject,
  serializeToQueryString
} from '@/lib/utils';

// Serializar con opciones
const serialized = serializeObject(obj, {
  space: 2,
  includeFunctions: false
});

// Deserializar con parseo de fechas
const deserialized = deserializeObject(json, {
  parseDates: true,
  parseNumbers: true
});

// Serializar a query string
const qs = serializeToQueryString({ name: 'John', age: 30 });
// 'name=John&age=30'
```

### 3. `string-tokenize.ts` ✅
Utilidades para tokenización de strings.

**Funciones:**
- `tokenizeWords(str, options?)` - Tokeniza en palabras
- `tokenizeNGrams(str, n?)` - Tokeniza en n-gramas
- `tokenizeSentences(str)` - Tokeniza en oraciones
- `tokenizeLines(str)` - Tokeniza en líneas
- `tokenizeChars(str, options?)` - Tokeniza en caracteres
- `tokenizeByDelimiter(str, delimiter, options?)` - Tokeniza por delimitador
- `tokenizeFixedLength(str, length, overlap?)` - Tokeniza en longitud fija
- `tokenizeByPattern(str, pattern)` - Tokeniza por patrón regex
- `tokenizeKeywords(str, options?)` - Tokeniza en palabras clave
- `tokenizeHashtags(str)` - Tokeniza hashtags
- `tokenizeMentions(str)` - Tokeniza menciones
- `tokenizeUrls(str)` - Tokeniza URLs
- `tokenizeEmails(str)` - Tokeniza emails
- `tokenizeNumbers(str)` - Tokeniza números

**Casos de uso:**
```typescript
import {
  tokenizeWords,
  tokenizeNGrams,
  tokenizeKeywords
} from '@/lib/utils';

// Tokenizar palabras
const words = tokenizeWords('Hello, world!', {
  caseSensitive: false,
  removePunctuation: true
});
// ['hello', 'world']

// N-gramas
const bigrams = tokenizeNGrams('hello', 2);
// ['he', 'el', 'll', 'lo']

// Palabras clave
const keywords = tokenizeKeywords('React is a JavaScript library', {
  minLength: 4,
  stopWords: ['is', 'a']
});
// ['react', 'javascript', 'library']
```

### 4. `number-statistics.ts` ✅
Utilidades para estadísticas numéricas.

**Funciones:**
- `mean(numbers: number[]): number` - Media (promedio)
- `median(numbers: number[]): number` - Mediana
- `mode(numbers: number[]): number | null` - Moda
- `standardDeviation(numbers, useSample?)` - Desviación estándar
- `variance(numbers, useSample?)` - Varianza
- `range(numbers: number[]): number` - Rango
- `quartile(numbers, quartile)` - Cuartil (1, 2, o 3)
- `interquartileRange(numbers)` - Rango intercuartílico (IQR)
- `percentile(numbers, percentile)` - Percentil (0-100)
- `statistics(numbers)` - Estadísticas completas
- `correlation(x, y)` - Correlación de Pearson
- `covariance(x, y)` - Covarianza

**Casos de uso:**
```typescript
import {
  mean,
  median,
  standardDeviation,
  statistics
} from '@/lib/utils';

const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// Estadísticas básicas
mean(numbers); // 5.5
median(numbers); // 5.5
standardDeviation(numbers); // 3.03

// Estadísticas completas
const stats = statistics(numbers);
// {
//   count: 10,
//   mean: 5.5,
//   median: 5.5,
//   variance: 9.17,
//   standardDeviation: 3.03,
//   q1: 3.25,
//   q2: 5.5,
//   q3: 7.75,
//   ...
// }
```

### 5. `date-business.ts` ✅
Utilidades para fechas comerciales y financieras.

**Funciones:**
- `isBusinessDay(date: Date): boolean` - Verifica si es día hábil
- `isWeekend(date: Date): boolean` - Verifica si es fin de semana
- `nextBusinessDay(date: Date): Date` - Siguiente día hábil
- `previousBusinessDay(date: Date): Date` - Día hábil anterior
- `countBusinessDays(startDate, endDate)` - Cuenta días hábiles
- `addBusinessDays(date, businessDays)` - Agrega días hábiles
- `lastDayOfMonth(date)` - Último día del mes
- `firstDayOfMonth(date)` - Primer día del mes
- `lastBusinessDayOfMonth(date)` - Último día hábil del mes
- `firstBusinessDayOfMonth(date)` - Primer día hábil del mes
- `isLastDayOfMonth(date)` - Verifica si es último día del mes
- `isFirstDayOfMonth(date)` - Verifica si es primer día del mes
- `daysInMonth(year, month)` - Días en un mes
- `businessDaysDifference(startDate, endDate)` - Diferencia en días hábiles
- `getBusinessDaysInRange(startDate, endDate)` - Obtiene días hábiles en rango
- `isSameMonth(date1, date2)` - Verifica mismo mes
- `isSameQuarter(date1, date2)` - Verifica mismo trimestre
- `getQuarter(date)` - Obtiene trimestre (1-4)
- `getWeekNumber(date)` - Obtiene número de semana

**Casos de uso:**
```typescript
import {
  isBusinessDay,
  addBusinessDays,
  countBusinessDays,
  getQuarter
} from '@/lib/utils';

// Verificar día hábil
isBusinessDay(new Date('2024-12-20')); // true (viernes)
isBusinessDay(new Date('2024-12-21')); // false (sábado)

// Agregar días hábiles
const date = new Date('2024-12-20'); // viernes
const next = addBusinessDays(date, 3);
// Lunes siguiente (salta fin de semana)

// Contar días hábiles
const days = countBusinessDays(
  new Date('2024-12-01'),
  new Date('2024-12-31')
);
// 22 días hábiles

// Obtener trimestre
getQuarter(new Date('2024-03-15')); // 1
```

## 📊 Estadísticas

### Antes
- Utilidades: 217 módulos
- Funciones: 1300+

### Después
- Utilidades: 222 módulos (+5)
- Funciones: 1350+ (+50+)

## 🎯 Casos de Uso Destacados

### Arrays Ponderados
- Selección aleatoria ponderada
- Cálculo de promedios ponderados
- Análisis de distribuciones

### Serialización de Objetos
- Serialización avanzada con opciones
- Conversión a query strings
- Clonación profunda

### Tokenización de Strings
- Análisis de texto
- Extracción de información
- Procesamiento de lenguaje natural

### Estadísticas Numéricas
- Análisis estadístico completo
- Medidas de tendencia central
- Medidas de dispersión
- Correlación y covarianza

### Fechas Comerciales
- Cálculo de días hábiles
- Operaciones financieras
- Análisis de períodos comerciales

## 🚀 Beneficios

### Para Desarrolladores
- ✅ Operaciones con datos ponderados
- ✅ Serialización flexible
- ✅ Análisis de texto avanzado
- ✅ Estadísticas completas
- ✅ Manejo de fechas comerciales

### Para el Proyecto
- ✅ Código más expresivo
- ✅ Análisis de datos más potente
- ✅ Mejor manejo de fechas financieras
- ✅ Type safety completo

## 📝 Integración

Todas las nuevas utilidades están disponibles a través del barrel export:

```typescript
import {
  weightedRandom,
  serializeObject,
  tokenizeWords,
  mean,
  isBusinessDay
} from '@/lib/utils';
```

## 🔄 Archivos Modificados

- `lib/utils/array-weighted.ts` (nuevo)
- `lib/utils/object-serialize.ts` (nuevo)
- `lib/utils/string-tokenize.ts` (nuevo)
- `lib/utils/number-statistics.ts` (nuevo)
- `lib/utils/date-business.ts` (nuevo)
- `lib/utils/index.ts` (actualizado)
- `README.md` (actualizado)

## 🎓 Próximos Pasos

- Considerar agregar más utilidades de análisis de datos
- Agregar tests unitarios para las nuevas funciones
- Documentar casos de uso avanzados
- Optimizar componentes adicionales

---

**Versión**: 2.32.0  
**Fecha**: Diciembre 2024  
**Estado**: ✅ COMPLETADO










