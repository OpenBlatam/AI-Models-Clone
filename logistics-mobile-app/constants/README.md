# Constants Documentation

This directory contains all application constants organized by category.

## 📁 Structure

```
constants/
├── colors.ts          # Color palette
├── api.ts            # API endpoints and configuration
├── routes.ts         # Navigation routes
├── timing.ts         # Animation, delays, intervals
├── validation.ts     # Validation rules and messages
├── spacing.ts        # Spacing, radius, elevation
├── typography.ts     # Font sizes, weights, line heights
├── sizes.ts          # Component sizes and breakpoints
├── storage-keys.ts   # AsyncStorage and SecureStorage keys
├── logistics.ts      # Logistics-specific constants
├── messages.ts       # User-facing messages
├── animations.ts     # Animation presets and values
├── config.ts         # App configuration
└── index.ts          # Central export
```

## 🎨 Colors

```typescript
import { Colors } from '@/constants';

// Usage
<View style={{ backgroundColor: Colors.primary }} />
```

## 🔌 API

```typescript
import { API_ENDPOINTS, API_CONFIG } from '@/constants';

// Usage
const url = API_ENDPOINTS.SHIPMENT_BY_ID('123');
const timeout = API_CONFIG.TIMEOUT;
```

## 🧭 Routes

```typescript
import { ROUTES } from '@/constants';

// Usage
router.push(ROUTES.SHIPMENT_DETAIL('123'));
```

## ⏱️ Timing

```typescript
import { ANIMATION_DURATION, DELAYS, POLLING_INTERVALS } from '@/constants';

// Usage
const duration = ANIMATION_DURATION.NORMAL;
const debounceDelay = DELAYS.DEBOUNCE_SEARCH;
```

## ✅ Validation

```typescript
import { VALIDATION, VALIDATION_MESSAGES } from '@/constants';

// Usage
const isValid = VALIDATION.EMAIL_REGEX.test(email);
const message = VALIDATION_MESSAGES.REQUIRED;
```

## 📏 Spacing

```typescript
import { SPACING, RADIUS, ELEVATION } from '@/constants';

// Usage
<View style={{ padding: SPACING.MD, borderRadius: RADIUS.LG }} />
```

## 📝 Typography

```typescript
import { FONT_SIZE, FONT_WEIGHT, LINE_HEIGHT } from '@/constants';

// Usage
<Text style={{ fontSize: FONT_SIZE.LG, fontWeight: FONT_WEIGHT.BOLD }} />
```

## 📐 Sizes

```typescript
import { SIZES, BREAKPOINTS } from '@/constants';

// Usage
const buttonHeight = SIZES.BUTTON.MEDIUM_HEIGHT;
const isTablet = width >= BREAKPOINTS.MD;
```

## 💾 Storage Keys

```typescript
import { STORAGE_KEYS, SECURE_STORAGE_KEYS } from '@/constants';

// Usage
await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
await SecureStore.setItemAsync(SECURE_STORAGE_KEYS.AUTH_TOKEN, token);
```

## 🚚 Logistics

```typescript
import { TRANSPORTATION_MODES, SHIPMENT_STATUS, CONTAINER_TYPES } from '@/constants';

// Usage
if (shipment.transportation_mode === TRANSPORTATION_MODES.MARITIME) {
  // ...
}
```

## 💬 Messages

```typescript
import { SUCCESS_MESSAGES, ERROR_MESSAGES, INFO_MESSAGES } from '@/constants';

// Usage
showToast(SUCCESS_MESSAGES.QUOTE_CREATED);
showError(ERROR_MESSAGES.NETWORK_ERROR);
```

## 🎬 Animations

```typescript
import { ANIMATION_PRESETS, ANIMATION_VALUES } from '@/constants';

// Usage
const springConfig = ANIMATION_PRESETS.SPRING.GENTLE;
const scale = ANIMATION_VALUES.SCALE.PRESSED;
```

## ⚙️ Config

```typescript
import { APP_CONFIG, FEATURES, LIMITS } from '@/constants';

// Usage
const appVersion = APP_CONFIG.VERSION;
if (FEATURES.OFFLINE_MODE) {
  // ...
}
```

## 📋 Best Practices

1. **Import from index**: Always import from `@/constants` for better tree-shaking
2. **Use constants**: Never hardcode values, use constants instead
3. **Type safety**: All constants are typed with `as const`
4. **Organization**: Keep constants organized by category
5. **Documentation**: Add JSDoc comments for complex constants

## 🔄 Updates

When adding new constants:
1. Add to appropriate category file
2. Export from `index.ts`
3. Update this README if needed
4. Use `as const` for type safety


