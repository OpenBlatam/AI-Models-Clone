# Utilities Documentation

This directory contains all utility functions organized by category.

## 📁 Structure

```
utils/
├── config.ts          # App configuration
├── api-client.ts      # API client setup
├── error-handler.ts   # Error handling utilities
├── format.ts          # Formatting functions
├── validation.ts      # Validation functions
├── string.ts          # String manipulation
├── array.ts           # Array utilities
├── object.ts          # Object utilities
├── storage.ts         # Storage helpers
├── navigation.ts      # Navigation helpers
├── url.ts             # URL utilities
├── file.ts            # File utilities
├── math.ts            # Math utilities
├── logger.ts          # Logging utilities
├── debounce.ts        # Debounce/throttle
└── index.ts           # Central export
```

## 📝 Usage Examples

### Formatting

```typescript
import { formatDate, formatCurrency, formatPhoneNumber } from '@/utils';

// Dates
formatDate(new Date(), 'MMM dd, yyyy'); // "Jan 15, 2024"
formatRelativeTime(date); // "2 hours ago"
formatDistanceTime(date); // "in 3 days"

// Currency
formatCurrency(1234.56, 'USD'); // "$1,234.56"

// Phone
formatPhoneNumber('1234567890'); // "(123) 456-7890"

// File Size
formatFileSize(1024000); // "1.0 MB"
```

### Validation

```typescript
import { isValidEmail, isValidPhone, isRequired } from '@/utils';

if (isValidEmail(email)) {
  // Valid email
}

if (isValidPhone(phone)) {
  // Valid phone
}

if (isRequired(value)) {
  // Value is provided
}
```

### String Manipulation

```typescript
import { capitalize, truncate, slugify, maskEmail } from '@/utils';

capitalize('hello'); // "Hello"
truncate('Long text', 10); // "Long te..."
slugify('Hello World'); // "hello-world"
maskEmail('user@example.com'); // "us**@example.com"
```

### Array Utilities

```typescript
import { unique, groupBy, sortBy, chunk } from '@/utils';

unique([1, 2, 2, 3]); // [1, 2, 3]
groupBy(items, 'category');
sortBy(items, 'name', 'asc');
chunk(array, 5); // Split into chunks of 5
```

### Object Utilities

```typescript
import { omit, pick, deepMerge, clone } from '@/utils';

omit(obj, ['key1', 'key2']);
pick(obj, ['key1', 'key2']);
deepMerge(target, source);
const cloned = clone(original);
```

### Storage

```typescript
import { getStorageItem, setStorageItem, getAuthToken } from '@/utils';

await setStorageItem('key', value);
const value = await getStorageItem('key');
const token = await getAuthToken();
```

### Navigation

```typescript
import { navigateToShipmentDetail, navigateToDashboard } from '@/utils';

navigateToShipmentDetail('123');
navigateToDashboard();
```

### URL

```typescript
import { buildQueryString, parseQueryString } from '@/utils';

const query = buildQueryString({ page: 1, limit: 20 });
const params = parseQueryString('?page=1&limit=20');
```

### File

```typescript
import { getFileExtension, isValidImageFile, formatFileSize } from '@/utils';

getFileExtension('image.jpg'); // "jpg"
isValidImageFile('image.jpg'); // true
formatFileSize(1024000); // "1.0 MB"
```

### Math

```typescript
import { clamp, round, percentage, distance } from '@/utils';

clamp(value, 0, 100);
round(3.14159, 2); // 3.14
percentage(25, 100); // 25
distance(lat1, lon1, lat2, lon2); // km
```

### Logging

```typescript
import { logger, logError, logInfo } from '@/utils';

logger.info('User logged in', { userId: '123' });
logError('Failed to load', error);
logInfo('Data loaded successfully');
```

### Debounce/Throttle

```typescript
import { debounce, throttle } from '@/utils';

const debouncedSearch = debounce(handleSearch, 500);
const throttledScroll = throttle(handleScroll, 100);
```

## 🔧 Best Practices

1. **Import from index**: Always import from `@/utils` for better tree-shaking
2. **Pure functions**: All utilities are pure functions (no side effects)
3. **Type safety**: All functions are fully typed
4. **Error handling**: Functions handle edge cases gracefully
5. **Documentation**: Functions are self-documenting with clear names

## 📋 Function Categories

### Formatting
- Date/time formatting
- Number/currency formatting
- Weight/volume formatting
- Phone number formatting
- File size formatting
- Status formatting

### Validation
- Email, phone, password validation
- Required field validation
- Length/range validation
- Coordinate validation
- File validation
- Date validation

### String Manipulation
- Case conversion
- Truncation
- Slugification
- Masking
- HTML escaping
- Initials generation

### Array Utilities
- Unique values
- Grouping
- Sorting
- Chunking
- Filtering
- Sampling

### Object Utilities
- Omit/pick properties
- Deep merge
- Clone
- Nested value access
- Flattening

### Storage
- AsyncStorage helpers
- SecureStore helpers
- Convenience functions for auth/user data

### Navigation
- Route navigation
- Deep linking
- Parameter handling

### URL
- Query string building/parsing
- URL validation
- Domain/path extraction

### File
- Extension detection
- MIME type detection
- File validation
- FormData creation

### Math
- Clamping
- Rounding
- Distance calculation
- Percentage calculations

### Logging
- Structured logging
- Log levels
- Log export

### Performance
- Debounce
- Throttle
- Async debounce

