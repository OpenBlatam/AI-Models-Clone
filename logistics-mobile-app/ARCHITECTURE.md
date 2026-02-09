# Architecture Overview

## 🏗️ Architecture Pattern

The app follows a **modular, feature-based architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│  - Screens (app/)                       │
│  - Components (components/)             │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Business Logic Layer            │
│  - Hooks (hooks/)                       │
│  - Store (store/)                       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Service Layer                    │
│  - API Services (services/)              │
│  - API Client (utils/api-client.ts)     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Data Layer                      │
│  - Types (types/)                       │
│  - API Backend                          │
└─────────────────────────────────────────┘
```

## 📦 Module Structure

### Services Layer
All API interactions are abstracted into service modules:
- `quotes-service.ts` - Quote operations
- `bookings-service.ts` - Booking operations
- `shipments-service.ts` - Shipment operations
- `containers-service.ts` - Container operations
- `tracking-service.ts` - Tracking operations
- `invoices-service.ts` - Invoice operations
- `documents-service.ts` - Document operations
- `alerts-service.ts` - Alert operations
- `insurance-service.ts` - Insurance operations
- `reports-service.ts` - Report operations

### Hooks Layer
Custom React hooks for data fetching and state management:
- `use-quotes.ts` - Quote hooks with React Query
- `use-shipments.ts` - Shipment hooks with React Query
- `use-tracking.ts` - Tracking hooks with React Query
- `use-dashboard.ts` - Dashboard hooks with React Query

### Components Layer
Reusable UI components organized by feature:
- `ui/` - Base UI components (Button, Input, Card, etc.)
- `shipment/` - Shipment-specific components
- `tracking/` - Tracking-specific components

### State Management
- **Zustand**: Global state (authentication)
- **React Query**: Server state (API data, caching)

## 🔄 Data Flow

1. **User Action** → Screen Component
2. **Screen** → Custom Hook
3. **Hook** → Service
4. **Service** → API Client
5. **API Client** → Backend API
6. **Response** → React Query Cache
7. **Cache Update** → Component Re-render

## 🎯 Key Principles

1. **Separation of Concerns**: Each layer has a single responsibility
2. **Type Safety**: Full TypeScript coverage
3. **Reusability**: Components and hooks are reusable
4. **Testability**: Pure functions and isolated modules
5. **Performance**: React Query caching and optimized re-renders

## 📱 Navigation Structure

```
app/
├── _layout.tsx (Root)
├── index.tsx (Entry point)
├── (tabs)/
│   ├── _layout.tsx (Tab navigator)
│   ├── index.tsx (Dashboard)
│   ├── shipments.tsx (Shipments list)
│   ├── tracking.tsx (Tracking search)
│   └── alerts.tsx (Alerts list)
├── shipment/
│   └── [id].tsx (Shipment details)
└── quote/
    └── create.tsx (Create quote)
```

## 🔌 API Integration

All API endpoints from the backend are mapped:

### Forwarding
- `POST /forwarding/quotes` - Create quote
- `GET /forwarding/quotes/{id}` - Get quote
- `POST /forwarding/bookings` - Create booking
- `GET /forwarding/bookings/{id}` - Get booking
- `POST /forwarding/shipments` - Create shipment
- `GET /forwarding/shipments` - List shipments
- `GET /forwarding/shipments/{id}` - Get shipment
- `PATCH /forwarding/shipments/{id}/status` - Update status
- `POST /forwarding/containers` - Create container
- `GET /forwarding/containers/{id}` - Get container

### Tracking
- `GET /tracking/shipment/{id}` - Track shipment
- `GET /tracking/container/{id}` - Track container
- `GET /tracking/shipment/{id}/history` - Tracking history
- `GET /tracking/summary` - Tracking summary

### Other Services
- Invoices, Documents, Alerts, Insurance, Reports

## 🛡️ Error Handling

- Global error handling in API client
- React Query error states
- User-friendly error messages
- Retry mechanisms

## ⚡ Performance Optimizations

- React Query caching (5-minute stale time)
- Automatic background refetching
- Optimized re-renders with proper hooks
- Image optimization with expo-image
- Code splitting with dynamic imports


