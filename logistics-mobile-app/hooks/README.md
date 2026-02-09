# Custom Hooks Documentation

This directory contains all custom React hooks used throughout the application.

## 📚 API Hooks

### `useQuotes`
Hook for managing quotes with React Query.

```typescript
const { mutate: createQuote, isLoading } = useCreateQuote();
const { data: quote } = useQuote(quoteId);
```

### `useShipments`
Hook for managing shipments with React Query.

```typescript
const { data: shipments } = useShipments({ status: 'in_transit' });
const { data: shipment } = useShipment(shipmentId);
```

### `useTracking`
Hook for tracking shipments and containers.

```typescript
const { data: tracking } = useShipmentTracking(shipmentId);
const { data: summary } = useTrackingSummary();
```

### `useDashboard`
Hook for dashboard statistics.

```typescript
const { data: stats } = useDashboardStats();
```

## 🛠 Utility Hooks

### `useDebounce`
Debounce a value to reduce frequent updates.

```typescript
const [searchTerm, setSearchTerm] = useState('');
const debouncedSearch = useDebounce(searchTerm, 500);
```

### `useThrottle`
Throttle a function to limit execution frequency.

```typescript
const throttledScroll = useThrottle(handleScroll, 100);
```

### `useInterval`
Execute a function at regular intervals.

```typescript
useInterval(() => {
  refetch();
}, 30000);
```

### `usePrevious`
Get the previous value of a state or prop.

```typescript
const previousValue = usePrevious(currentValue);
```

### `useToggle`
Toggle a boolean value with helper methods.

```typescript
const { value, toggle, setTrue, setFalse } = useToggle(false);
```

### `useMount`
Execute a callback only on component mount.

```typescript
useMount(() => {
  initialize();
});
```

### `useUnmount`
Execute a callback only on component unmount.

```typescript
useUnmount(() => {
  cleanup();
});
```

## 📱 Device Hooks

### `useKeyboard`
Monitor keyboard visibility and height.

```typescript
const { isVisible, height, dismiss } = useKeyboard();
```

### `useSafeArea`
Get safe area insets for all edges.

```typescript
const { top, bottom, left, right } = useSafeArea();
```

### `useWindowDimensions`
Get and monitor window dimensions.

```typescript
const { width, height, scale, fontScale } = useWindowDimensions();
```

### `useMediaQuery`
Responsive breakpoints based on window width.

```typescript
const { isMobile, isTablet, isDesktop, isMd, isLg } = useMediaQuery();
```

### `useAppState`
Monitor app state (active, background, inactive).

```typescript
const { isActive, isBackground, appState } = useAppState();
```

### `useOnlineStatus`
Check online/offline status.

```typescript
const { isOnline, isOffline } = useOnlineStatus();
```

### `useNetworkStatus`
Detailed network status information.

```typescript
const { isConnected, isInternetReachable, type } = useNetworkStatus();
```

## 💾 Storage Hooks

### `useAsyncStorage`
Persist data in AsyncStorage with automatic loading.

```typescript
const { storedValue, setValue, removeValue, isLoading } = useAsyncStorage('key', initialValue);
```

## 🔐 Permission Hooks

### `usePermissions`
Request and check device permissions.

```typescript
const { granted, requestPermission, isLoading } = usePermissions('location');
```

### `useLocation`
Get current device location.

```typescript
const { location, error, isLoading, refreshLocation, hasPermission } = useLocation();
```

### `useImagePicker`
Pick images from camera or library.

```typescript
const { image, pickImage, clearImage, hasPermission } = useImagePicker();
```

## 🎨 UI Hooks

### `useClipboard`
Read and write to clipboard.

```typescript
const { clipboardContent, copyToClipboard, readClipboard } = useClipboard();
```

### `useHapticFeedback`
Provide haptic feedback to users.

```typescript
const { light, medium, heavy, success, warning, error, selection } = useHapticFeedback();
```

### `useFocusEffect`
Execute callback when screen comes into focus.

```typescript
useFocusEffect(() => {
  refetch();
  return () => cleanup();
});
```

## 📝 Usage Examples

### Example 1: Search with Debounce
```typescript
function SearchScreen() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 500);
  
  const { data } = useQuery({
    queryKey: ['search', debouncedQuery],
    queryFn: () => searchAPI(debouncedQuery),
    enabled: debouncedQuery.length > 0,
  });
  
  return <Input value={query} onChangeText={setQuery} />;
}
```

### Example 2: Keyboard-Aware Layout
```typescript
function FormScreen() {
  const { isVisible, height } = useKeyboard();
  const { bottom } = useSafeArea();
  
  return (
    <View style={{ paddingBottom: isVisible ? height - bottom : 0 }}>
      {/* Form content */}
    </View>
  );
}
```

### Example 3: Responsive Design
```typescript
function ResponsiveComponent() {
  const { isMobile, isTablet, width } = useMediaQuery();
  
  return (
    <View style={{ flexDirection: isMobile ? 'column' : 'row' }}>
      {/* Content */}
    </View>
  );
}
```

### Example 4: Location Tracking
```typescript
function TrackingScreen() {
  const { location, refreshLocation, hasPermission } = useLocation();
  
  if (!hasPermission) {
    return <PermissionRequest />;
  }
  
  return (
    <View>
      <Text>Lat: {location?.latitude}</Text>
      <Text>Lng: {location?.longitude}</Text>
      <Button title="Refresh" onPress={refreshLocation} />
    </View>
  );
}
```

### Example 5: Haptic Feedback
```typescript
function ButtonWithFeedback() {
  const { success, error } = useHapticFeedback();
  
  function handleSuccess() {
    success();
    // Perform action
  }
  
  function handleError() {
    error();
    // Show error
  }
  
  return (
    <>
      <Button title="Success" onPress={handleSuccess} />
      <Button title="Error" onPress={handleError} />
    </>
  );
}
```

## 🔄 Hook Dependencies

Some hooks depend on others:
- `useOnlineStatus` → `useNetworkStatus`
- `useLocation` → `usePermissions`
- `useImagePicker` → `usePermissions`
- `useMediaQuery` → `useWindowDimensions`

## ⚠️ Best Practices

1. **Always handle loading states** when using async hooks
2. **Check permissions** before using device features
3. **Clean up subscriptions** in hooks that use event listeners
4. **Use debounce/throttle** for expensive operations
5. **Memoize callbacks** when passing to child components
6. **Handle errors** appropriately in all hooks


