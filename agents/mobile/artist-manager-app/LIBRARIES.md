# Librerías y Dependencias

Este documento detalla todas las librerías utilizadas en el proyecto, su propósito y versión.

## 📦 Dependencias Principales

### Expo Core
- **expo** (~51.0.0) - Framework principal de Expo
- **expo-router** (~3.5.0) - Sistema de routing basado en archivos
- **expo-status-bar** (~1.12.1) - Control de la barra de estado
- **expo-constants** (~16.0.0) - Constantes del dispositivo y app
- **expo-linking** (~6.3.1) - Deep linking y URLs
- **expo-splash-screen** (~0.27.0) - Manejo de splash screen
- **expo-system-ui** (~3.0.0) - Control de UI del sistema
- **expo-font** (~12.0.0) - Carga de fuentes personalizadas
- **expo-image** (~1.12.0) - Componente de imagen optimizado
- **expo-localization** (~14.0.0) - Internacionalización y localización
- **expo-updates** (~0.25.0) - Over-the-air (OTA) updates
- **expo-haptics** (~13.0.0) - Feedback háptico
- **expo-blur** (~13.0.0) - Efectos blur
- **expo-linear-gradient** (~13.0.0) - Gradientes lineales
- **expo-error-reporter** (~1.0.0) - Reporte de errores

### React Native Core
- **react** (18.2.0) - Biblioteca React
- **react-native** (0.74.0) - Framework React Native

### Navegación y UI
- **react-native-safe-area-context** (4.10.0) - Manejo de safe areas
- **react-native-screens** (~3.31.0) - Optimización de screens nativas
- **react-native-gesture-handler** (~2.16.0) - Manejo de gestos
- **react-native-reanimated** (~3.10.0) - Animaciones de alto rendimiento
- **react-native-svg** (15.2.0) - Renderizado de SVG
- **@react-native-community/masked-view** (0.2.9) - Efectos visuales con máscaras

### State Management y Data Fetching
- **@tanstack/react-query** (^5.28.0) - Data fetching, caching y sincronización
- **zustand** (^4.5.0) - State management ligero

### Validación y Formularios
- **zod** (^3.22.4) - Validación de esquemas TypeScript-first
- **react-hook-form** (^7.51.0) - Manejo de formularios performante
- **@hookform/resolvers** (^3.3.4) - Resolvers para react-hook-form (Zod)

### Utilidades
- **date-fns** (^3.3.1) - Manipulación de fechas
- **i18n-js** (^4.4.3) - Internacionalización

### Almacenamiento
- **react-native-encrypted-storage** (^4.0.3) - Almacenamiento encriptado seguro
- **@react-native-async-storage/async-storage** (1.23.1) - Almacenamiento asíncrono

### UI Components
- **@expo/vector-icons** (^14.0.0) - Iconos vectoriales
- **react-native-toast-message** (^2.2.0) - Mensajes toast
- **react-native-flash-message** (^0.4.2) - Mensajes flash

### Red y Conectividad
- **@react-native-community/netinfo** (^11.1.0) - Información de red

## 🛠️ DevDependencies

### TypeScript
- **typescript** (~5.3.3) - Compilador TypeScript
- **@types/react** (~18.2.45) - Tipos para React
- **@types/react-native** (^0.73.0) - Tipos para React Native
- **@types/react-native-toast-message** (^1.4.0) - Tipos para toast
- **@types/jest** (^29.5.12) - Tipos para Jest

### Linting y Formatting
- **eslint** (^8.57.0) - Linter JavaScript/TypeScript
- **eslint-config-expo** (^7.0.0) - Configuración ESLint para Expo
- **eslint-config-prettier** (^9.1.0) - Desactiva reglas que conflictúan con Prettier
- **eslint-plugin-react** (^7.34.0) - Reglas ESLint para React
- **eslint-plugin-react-hooks** (^4.6.0) - Reglas para React Hooks
- **eslint-plugin-react-native** (^4.1.0) - Reglas para React Native
- **@typescript-eslint/eslint-plugin** (^7.0.0) - Plugin ESLint para TypeScript
- **@typescript-eslint/parser** (^7.0.0) - Parser ESLint para TypeScript
- **prettier** (^3.2.5) - Formateador de código
- **prettier-plugin-organize-imports** (^3.2.3) - Organiza imports automáticamente

### Testing
- **jest** (^29.7.0) - Framework de testing
- **jest-expo** (~51.0.0) - Preset Jest para Expo
- **@testing-library/react-native** (^12.4.0) - Utilidades de testing para React Native
- **@testing-library/jest-native** (^5.4.3) - Matchers adicionales para Jest
- **@testing-library/user-event** (^14.5.1) - Simulación de eventos de usuario

### Build Tools
- **@babel/core** (^7.24.0) - Compilador Babel
- **babel-plugin-module-resolver** (^5.0.0) - Resolver de módulos con alias

## 📚 Uso de Librerías Clave

### React Query
```typescript
import { useQuery } from '@tanstack/react-query';
// Data fetching con cache automático
```

### Zustand
```typescript
import { useAuthStore } from '@/store/auth-store';
// State management global ligero
```

### React Hook Form + Zod
```typescript
import { useForm } from '@/hooks/use-form';
import { calendarEventSchema } from '@/utils/validation';
// Formularios con validación
```

### Toast Messages
```typescript
import { useToast } from '@/hooks/use-toast';
// Mensajes toast con feedback háptico
```

### Haptics
```typescript
import { haptics } from '@/utils/haptics';
// Feedback háptico en interacciones
```

### Error Reporting
```typescript
import { reportError } from '@/utils/error-reporter';
// Reporte de errores en producción
```

## 🔄 Actualización de Librerías

Para actualizar las librerías:

```bash
# Verificar actualizaciones
npm outdated

# Actualizar todas las dependencias
npm update

# Actualizar una librería específica
npm install package-name@latest

# Verificar compatibilidad con Expo
npx expo-doctor
```

## ⚠️ Consideraciones

1. **Compatibilidad con Expo**: Todas las librerías deben ser compatibles con Expo SDK 51
2. **Versiones**: Usar versiones exactas (~) para Expo packages y ranges (^) para otras
3. **Native Modules**: Algunas librerías requieren configuración nativa adicional
4. **Bundle Size**: Monitorear el tamaño del bundle al agregar nuevas librerías

## 📝 Notas

- Las librerías están organizadas por categoría
- Todas las versiones son compatibles con Expo SDK 51
- Se prioriza el uso de librerías mantenidas activamente
- Se evitan duplicados de funcionalidad


