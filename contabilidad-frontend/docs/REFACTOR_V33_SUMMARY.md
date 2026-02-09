# Refactorización V33 - Resumen

## Fecha
Diciembre 2024

## Objetivo
Agregar utilidades avanzadas para permutaciones y combinaciones, seal profundo de objetos, escapado de strings, operaciones con números primos, y fechas recurrentes.

## Nuevas Utilidades (5 módulos)

### 1. `array-permutation.ts` - Permutaciones y Combinaciones
Funciones para generar permutaciones, combinaciones y variaciones de arrays.

**Funciones:**
- `permutations` - Genera todas las permutaciones de un array
- `permutationsOfSize` - Permutaciones de tamaño específico
- `combinations` - Genera todas las combinaciones
- `cartesianProduct` - Producto cartesiano de múltiples arrays
- `uniquePermutations` - Permutaciones únicas (sin duplicados)
- `uniqueCombinations` - Combinaciones únicas (sin duplicados)
- `factorial` - Calcula el factorial de un número
- `permutationCount` - Calcula número de permutaciones (nPr)
- `combinationCount` - Calcula número de combinaciones (nCr)
- `permutationsWithRepetition` - Permutaciones con repetición
- `combinationsWithRepetition` - Combinaciones con repetición
- `nextPermutation` - Siguiente permutación en orden lexicográfico

**Casos de uso:**
- Generación de todas las posibles combinaciones
- Algoritmos de optimización combinatoria
- Análisis de probabilidades
- Generación de passwords y códigos
- Problemas de optimización

### 2. `object-seal.ts` - Seal Profundo de Objetos
Utilidades para sellar objetos (prevenir agregar/eliminar propiedades, pero permitir modificar existentes).

**Funciones:**
- `deepSeal` - Sella un objeto de manera profunda
- `isDeepSealed` - Verifica si un objeto está sellado profundamente
- `deepSealWithProxy` - Sella con proxy para prevenir agregar/eliminar
- `deepSealDev` - Sella solo en modo desarrollo
- `canAddProperties` - Verifica si se pueden agregar propiedades
- `canDeleteProperties` - Verifica si se pueden eliminar propiedades
- `tryAddProperty` - Intenta agregar una propiedad
- `tryDeleteProperty` - Intenta eliminar una propiedad
- `sealStructure` - Sella estructura pero permite modificar valores
- `isSealed` - Verifica si está sellado
- `deepSealWithModify` - Sella pero permite modificar valores

**Casos de uso:**
- Configuraciones con estructura fija
- Prevención de propiedades accidentales
- Objetos de configuración inmutable en estructura
- Desarrollo seguro con validación de estructura

### 3. `string-escape.ts` - Escapado y Unescapado Avanzado
Utilidades para escapar y desescapar strings en diferentes contextos.

**Funciones:**
- `escapeHtml` / `unescapeHtml` - Escapado HTML
- `escapeRegex` - Escapado para regex
- `escapeUrl` / `unescapeUrl` - Escapado de URLs
- `escapeJson` - Escapado para JSON
- `escapeSql` - Escapado básico para SQL
- `escapeShell` - Escapado para shell
- `escapeXml` / `unescapeXml` - Escapado XML
- `escapeCss` - Escapado para CSS
- `escapeJs` / `unescapeJs` - Escapado JavaScript
- `escapeByType` - Escapado según tipo
- `unescapeByType` - Unescapado según tipo
- `escapeHtmlAttribute` - Escapado para atributos HTML
- `escapeHtmlText` - Escapado para texto HTML
- `escapeHtmlComment` - Escapado para comentarios HTML

**Casos de uso:**
- Prevención de XSS en aplicaciones web
- Sanitización de entrada de usuario
- Generación segura de código
- Manipulación de strings en diferentes contextos
- Seguridad en renderizado de contenido

### 4. `number-prime.ts` - Operaciones con Números Primos
Utilidades para trabajar con números primos y operaciones relacionadas.

**Funciones:**
- `isPrime` - Verifica si un número es primo
- `generatePrimes` - Genera todos los primos hasta un límite (criba de Eratóstenes)
- `nextPrime` - Encuentra el siguiente número primo
- `previousPrime` - Encuentra el número primo anterior
- `primeFactors` - Factoriza un número en factores primos
- `primeFactorsArray` - Factores primos como array
- `gcd` - Máximo común divisor (algoritmo de Euclides)
- `lcm` - Mínimo común múltiplo
- `lcmMultiple` - MCM de múltiples números
- `areCoprime` - Verifica si dos números son coprimos
- `eulerTotient` - Función totiente de Euler (φ)
- `nthPrime` - Encuentra el n-ésimo número primo
- `isTwinPrime` - Verifica si es primo gemelo
- `twinPrimes` - Encuentra pares de primos gemelos
- `isMersennePrime` - Verifica si es primo de Mersenne

**Casos de uso:**
- Criptografía y seguridad
- Algoritmos matemáticos
- Optimización de cálculos
- Análisis numérico
- Generación de claves

### 5. `date-recurring.ts` - Fechas Recurrentes y Patrones
Utilidades para generar y trabajar con fechas recurrentes.

**Funciones:**
- `generateRecurringDates` - Genera fechas recurrentes según opciones
- `dailyRecurrence` - Fechas diarias recurrentes
- `weeklyRecurrence` - Fechas semanales recurrentes
- `monthlyRecurrence` - Fechas mensuales recurrentes
- `yearlyRecurrence` - Fechas anuales recurrentes
- `matchesRecurrencePattern` - Verifica si fecha coincide con patrón
- `nextRecurrenceDate` - Encuentra próxima fecha recurrente
- `previousRecurrenceDate` - Encuentra fecha recurrente anterior
- `countRecurrences` - Cuenta ocurrencias entre fechas
- `businessDaysRecurrence` - Fechas de días laborables
- `weekendRecurrence` - Fechas de fines de semana

**Casos de uso:**
- Calendarios y eventos recurrentes
- Programación de tareas
- Recordatorios y notificaciones
- Cálculo de fechas de pago
- Planificación de reuniones
- Gestión de horarios

## Estadísticas Actualizadas

- **Utilidades**: 241+ módulos (236 + 5 nuevos)
- **Funciones**: 1550+ (1500+ + 50+ nuevas)
- **Linting**: 0 errores

## Mejoras Técnicas

1. **Combinatoria**: Utilidades completas para permutaciones y combinaciones
2. **Inmutabilidad**: Seal profundo para estructuras fijas pero valores modificables
3. **Seguridad**: Escapado completo para múltiples contextos
4. **Matemáticas**: Operaciones avanzadas con números primos
5. **Temporalidad**: Generación y manejo de fechas recurrentes

## Integración

Todas las nuevas utilidades están:
- ✅ Exportadas en `lib/utils/index.ts`
- ✅ Documentadas con JSDoc
- ✅ Tipadas con TypeScript
- ✅ Sin errores de linting
- ✅ Listas para usar en producción

## Casos de Uso Destacados

- **Permutaciones**: Generación de todas las posibles combinaciones para análisis
- **Seal**: Configuraciones con estructura fija pero valores configurables
- **Escapado**: Prevención de XSS y sanitización de entrada
- **Primos**: Criptografía y algoritmos matemáticos
- **Recurrencias**: Calendarios, eventos y programación de tareas

## Próximos Pasos

- Integración de fechas recurrentes en calendarios fiscales
- Uso de permutaciones en optimización de cálculos
- Aplicación de escapado en renderizado seguro
- Utilización de primos en generación de claves










