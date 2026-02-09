# Logistics AI Platform - Mobile App

A comprehensive React Native mobile application built with Expo and TypeScript for the Logistics AI Platform backend.

## 🚀 Features

- **Quotes Management**: Create and manage freight quotes
- **Bookings**: Create bookings from quotes
- **Shipments**: View and manage shipments with real-time tracking
- **Containers**: Track container status and location
- **Real-time Tracking**: Track shipments and containers with detailed event history
- **Invoices**: View and manage invoices
- **Documents**: Upload and manage shipping documents
- **Alerts**: Receive and manage shipment alerts
- **Insurance**: Manage cargo insurance policies
- **Dashboard**: View key metrics and statistics
- **Dark Mode**: Automatic dark mode support
- **Offline Support**: Network status monitoring
- **Error Handling**: Comprehensive error boundaries and handling

## 🛠 Tech Stack

- **Expo** ~51.0.0
- **React Native** 0.74.0
- **TypeScript** ~5.3.3
- **Expo Router** ~3.5.0 (File-based routing)
- **React Query** (@tanstack/react-query) for data fetching
- **Zustand** for state management
- **Zod** for validation
- **React Hook Form** for form handling
- **Axios** for API calls
- **React Native Reanimated** for animations
- **React Native Gesture Handler** for gestures

## 📁 Project Structure

```
logistics-mobile-app/
├── app/                    # Expo Router screens
│   ├── (tabs)/            # Tab navigation screens
│   │   ├── index.tsx      # Dashboard
│   │   ├── shipments.tsx  # Shipments list
│   │   ├── tracking.tsx   # Tracking search
│   │   └── alerts.tsx     # Alerts list
│   ├── shipment/[id].tsx  # Shipment details
│   ├── quote/create.tsx   # Create quote
│   └── _layout.tsx        # Root layout
├── components/            # Reusable components
│   ├── ui/                # UI components (Button, Input, Card)
│   ├── shipment/          # Shipment-specific components
│   └── tracking/          # Tracking components
├── contexts/              # React contexts
│   └── theme-context.tsx  # Theme provider
├── services/              # API services
│   ├── quotes-service.ts
│   ├── bookings-service.ts
│   ├── shipments-service.ts
│   └── ...
├── hooks/                 # Custom React hooks
│   ├── use-quotes.ts
│   ├── use-shipments.ts
│   ├── use-tracking.ts
│   ├── use-debounce.ts
│   └── use-network-status.ts
├── store/                 # Zustand stores
│   └── auth-store.ts
├── types/                 # TypeScript types
│   └── index.ts
└── utils/                 # Utilities
    ├── api-client.ts
    ├── config.ts
    └── error-handler.ts
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Expo CLI: `npm install -g expo-cli`
- iOS Simulator (for Mac) or Android Emulator

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure API URL in `app.json`:
```json
{
  "extra": {
    "apiUrl": "http://localhost:8030"
  }
}
```

Or set environment variable:
```bash
export EXPO_PUBLIC_API_URL=http://localhost:8030
```

3. Start the development server:
```bash
npm start
```

4. Run on iOS:
```bash
npm run ios
```

5. Run on Android:
```bash
npm run android
```

## ✨ Key Features

### Dark Mode
- Automatic system theme detection
- Manual theme toggle support
- Consistent theming across all components

### Animations
- Smooth button press animations
- Card interaction feedback
- Screen transitions
- Loading state animations

### Error Handling
- Global error boundary
- API error formatting
- Network error detection
- User-friendly error messages

### Performance
- React Query caching (5-minute stale time)
- Automatic background refetching
- Optimized re-renders with memoization
- Skeleton loading states

### Accessibility
- Proper accessibility labels
- Screen reader support
- Keyboard navigation
- High contrast support

## 🔌 API Integration

The app is fully integrated with the Logistics AI Platform backend API. All endpoints are mapped:

- `/forwarding/quotes` - Quote management
- `/forwarding/bookings` - Booking management
- `/forwarding/shipments` - Shipment management
- `/forwarding/containers` - Container management
- `/tracking/*` - Tracking endpoints
- `/invoices` - Invoice management
- `/documents` - Document management
- `/alerts` - Alert management
- `/insurance` - Insurance management
- `/reports` - Reports and dashboard

## 🧪 Development

### Type Checking
```bash
npm run type-check
```

### Linting
```bash
npm run lint
```

### Testing
```bash
npm test
```

## 📦 Building for Production

### iOS
```bash
eas build --platform ios
```

### Android
```bash
eas build --platform android
```

## 🔐 Environment Variables

Create a `.env` file:
```
EXPO_PUBLIC_API_URL=http://localhost:8030
```

## 📝 Recent Improvements

See [IMPROVEMENTS.md](./IMPROVEMENTS.md) for a detailed list of recent enhancements.

## 📄 License

Part of the Blatam Academy system.
