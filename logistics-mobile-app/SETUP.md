# Setup Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Update `EXPO_PUBLIC_API_URL` with your backend URL

3. **Start Development Server**
   ```bash
   npm start
   ```

4. **Run on Device/Simulator**
   - Press `i` for iOS simulator
   - Press `a` for Android emulator
   - Scan QR code with Expo Go app on physical device

## Project Structure

```
logistics-mobile-app/
├── app/                 # Expo Router screens
├── components/         # Reusable components
├── services/           # API services
├── hooks/              # Custom hooks
├── store/              # State management
├── types/              # TypeScript types
└── utils/              # Utilities
```

## Key Files

- `app/_layout.tsx` - Root layout with providers
- `app/(tabs)/_layout.tsx` - Tab navigation
- `utils/api-client.ts` - API client configuration
- `services/` - All API service modules
- `types/index.ts` - TypeScript type definitions

## API Configuration

Update the API URL in:
- `app.json` → `extra.apiUrl`
- `.env` → `EXPO_PUBLIC_API_URL`

## Development Tips

1. **Type Checking**: Run `npm run type-check` before committing
2. **Linting**: Run `npm run lint` to check code quality
3. **Hot Reload**: Changes are automatically reflected
4. **Debugging**: Use React Native Debugger or Flipper

## Common Issues

### Metro bundler cache
```bash
npx expo start --clear
```

### Node modules issues
```bash
rm -rf node_modules
npm install
```

### TypeScript errors
```bash
npm run type-check
```


