# 📚 Referencia de API - Utilidades y Hooks

## 🎣 Hooks

### `useTaskPolling`
Polling automático de tareas.

```typescript
const { taskStatus, result, isLoading, error } = useTaskPolling(taskId);
```

### `useLocalStorage`
localStorage con sincronización cross-tab.

```typescript
const [value, setValue] = useLocalStorage('key', defaultValue);
```

### `useDebounce`
Debounce de valores.

```typescript
const debouncedValue = useDebounce(value, 500);
```

### `useDarkMode`
Gestión de modo oscuro.

```typescript
const { isDark, toggle, setDark } = useDarkMode();
```

## 🛠️ Utilidades Principales

### Formateo

```typescript
import { formatCurrencyMXN, formatDate, formatPhoneNumberMX } from '@/lib/utils';

formatCurrencyMXN(1234.56); // "$1,234.56 MXN"
formatDate(new Date()); // "15 de enero, 2024"
formatPhoneNumberMX('5512345678'); // "(55) 1234-5678"
```

### Validación Fiscal

```typescript
import { validateRFC, validateCURP, validateCLABE } from '@/lib/utils';

validateRFC('XAXX010101000'); // { isValid: true, ... }
validateCURP('XAXX010101HDFXXX00'); // { isValid: true, ... }
validateCLABE('012345678901234567'); // { isValid: true, ... }
```

### Cálculos Fiscales

```typescript
import { calculateISR, calculateIVA, calculateProfitMargin } from '@/lib/utils';

calculateISR(100000, 'asalariado'); // { tax: 15000, ... }
calculateIVA(1000, 0.16); // { tax: 160, total: 1160 }
calculateProfitMargin(1000, 600); // { margin: 0.4, percentage: 40 }
```

### Exportación

```typescript
import { exportToJSON, exportToCSV, exportToPDF } from '@/lib/utils';

exportToJSON(data, 'export.json');
exportToCSV(data, 'export.csv');
exportToPDF({ status, result }, 'export.pdf');
```

## 📖 Documentación Completa

Ver archivos individuales en `lib/utils/` y `lib/hooks/` para documentación detallada.












