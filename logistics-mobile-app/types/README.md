# Types Documentation

This directory contains all TypeScript type definitions organized by category.

## 📁 Structure

```
types/
├── index.ts          # Main types (logistics domain)
├── ui.ts             # UI component types
├── navigation.ts     # Navigation types
├── forms.ts          # Form types
├── events.ts         # Event types
├── state.ts          # State management types
├── api.ts            # API types
├── hooks.ts          # Hook return types
├── storage.ts        # Storage types
├── theme.ts          # Theme types
├── common.ts         # Common utility types
├── refs.ts           # Ref types
├── gestures.ts       # Gesture types
├── animations.ts     # Animation types
└── README.md         # This file
```

## 📝 Usage Examples

### UI Types

```typescript
import { ButtonProps, InputProps, CardProps } from '@/types';

function MyButton(props: ButtonProps) {
  // ...
}

function MyInput(props: InputProps) {
  // ...
}
```

### Navigation Types

```typescript
import { RootStackParamList, RootRouteProp } from '@/types';

type ShipmentDetailRouteProp = RootRouteProp<'shipment/[id]'>;

function ShipmentDetailScreen({ route }: { route: ShipmentDetailRouteProp }) {
  const { id } = route.params;
  // ...
}
```

### Form Types

```typescript
import { UseFormReturn, FormValidationSchema } from '@/types';

interface MyFormData {
  email: string;
  password: string;
}

const validationSchema: FormValidationSchema<MyFormData> = {
  email: {
    required: true,
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
  password: {
    required: true,
    minLength: 8,
  },
};
```

### State Types

```typescript
import { AsyncState, PaginatedState } from '@/types';

const [state, setState] = useState<AsyncState<ShipmentResponse>>({
  data: null,
  isLoading: false,
  error: null,
  isSuccess: false,
  isError: false,
});
```

### API Types

```typescript
import { ApiResponse, ApiError, PaginatedResponse } from '@/types';

async function fetchShipments(): Promise<PaginatedResponse<ShipmentResponse>> {
  // ...
}
```

### Hook Types

```typescript
import { UseAsyncReturn, UseToggleReturn } from '@/types';

function useMyAsync<T>(): UseAsyncReturn<T> {
  // ...
}

function useMyToggle(): UseToggleReturn {
  // ...
}
```

### Common Utility Types

```typescript
import { Nullable, Optional, Maybe, DeepPartial } from '@/types';

type User = {
  id: string;
  name: string;
  email: string;
};

type PartialUser = DeepPartial<User>;
type NullableUser = Nullable<User>;
type OptionalUser = Optional<User>;
type MaybeUser = Maybe<User>;
```

### Theme Types

```typescript
import { Theme, ThemeContextValue, ThemeMode } from '@/types';

function useTheme(): ThemeContextValue {
  // ...
}
```

### Event Types

```typescript
import { AppEvent, ErrorEvent, NetworkEvent } from '@/types';

function handleEvent(event: AppEvent) {
  if (event.type === 'error') {
    const errorEvent = event as ErrorEvent;
    // Handle error
  }
}
```

### Ref Types

```typescript
import { TextInputRef, ScrollViewRef } from '@/types';

const inputRef = useRef<TextInputRef>(null);
const scrollRef = useRef<ScrollViewRef>(null);
```

### Gesture Types

```typescript
import { PanGestureHandlerEvent, SwipeGestureConfig } from '@/types';

function handlePan(event: PanGestureHandlerEvent) {
  const { translationX, translationY } = event.nativeEvent;
  // ...
}
```

### Animation Types

```typescript
import { SpringConfig, TimingConfig, AnimatedStyle } from '@/types';

const springConfig: SpringConfig = {
  damping: 20,
  stiffness: 90,
};
```

## 🔧 Best Practices

1. **Use interfaces over types** for object shapes
2. **Use type aliases** for unions, intersections, and primitives
3. **Avoid enums** - use const objects with `as const`
4. **Export types** from index.ts for easy importing
5. **Use generic types** for reusable type definitions
6. **Document complex types** with JSDoc comments
7. **Use branded types** for type safety (ID, Email, etc.)

## 📋 Type Categories

### Domain Types
- Logistics-specific types (Shipment, Quote, Booking, etc.)
- Status enums and constants
- Request/Response types

### UI Types
- Component prop types
- Style types
- Event handler types

### Utility Types
- Common transformations (Nullable, Optional, DeepPartial)
- Branded types (ID, Email, URL)
- Generic utility types

### Framework Types
- React Native types
- Navigation types
- Hook return types
- State management types

## 🎯 Type Safety Tips

1. **Strict mode**: Always use strict TypeScript
2. **No any**: Avoid `any` type, use `unknown` instead
3. **Type guards**: Use type guards for runtime checks
4. **Discriminated unions**: Use for type-safe state machines
5. **Branded types**: Use for type-safe primitives (ID, Email)

