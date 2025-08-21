# 🚀 Blatam Academy

A modern, high-performance React Native learning management application built with cutting-edge technologies and best practices.

## ✨ Features

### 🎓 Learning Management
- **Course Management**: Create, edit, and organize courses with rich content
- **Progress Tracking**: Monitor student progress with detailed analytics
- **Interactive Lessons**: Engaging multimedia content with quizzes and assessments
- **Instructor Dashboard**: Comprehensive tools for course management and student monitoring

### 🌍 Internationalization (i18n)
- **Multi-language Support**: English, Spanish, French, German, and more
- **RTL Support**: Full right-to-left language support (Arabic ready)
- **Dynamic Language Switching**: Real-time language changes without app restart
- **Device Language Detection**: Automatic detection of user's preferred language
- **Persistent Language Storage**: Language preferences saved locally
- **Performance Optimized**: Lazy loading of translation resources

### ⚡ Performance Optimizations
- **Performance Monitoring**: Real-time performance tracking and bottleneck detection
- **Optimized Components**: High-performance list rendering with FlashList
- **Image Optimization**: Fast image loading with react-native-fast-image
- **Memory Management**: Efficient state management with Zustand
- **Caching Strategy**: Smart data caching with React Query
- **Bundle Optimization**: Code splitting and lazy loading

### 🎨 Modern UI/UX
- **Responsive Design**: Adapts to all screen sizes and orientations
- **Accessibility**: Full accessibility support for screen readers
- **Dark/Light Mode**: Theme switching with system preference detection
- **Smooth Animations**: Fluid transitions and micro-interactions
- **Error Handling**: Graceful error boundaries and user-friendly error messages

### 📊 Analytics & Monitoring
- **User Analytics**: Track user behavior and feature usage
- **Performance Metrics**: Monitor app performance and identify bottlenecks
- **Error Tracking**: Comprehensive error reporting and debugging
- **Session Management**: Detailed session tracking and analysis

## 🛠 Technology Stack

### Core Framework
- **React Native**: Cross-platform mobile development
- **Expo**: Development platform and build tools
- **TypeScript**: Type-safe development with strict configuration

### State Management & Data
- **Zustand**: Lightweight global state management
- **React Query**: Server state management and caching
- **AsyncStorage**: Local data persistence

### Performance Libraries
- **@shopify/flash-list**: High-performance list rendering
- **react-native-fast-image**: Optimized image loading
- **react-native-skeleton-placeholder**: Loading state animations

### Internationalization
- **i18next**: Core internationalization framework
- **react-i18next**: React integration for i18next
- **expo-localization**: Device locale detection

### Development Tools
- **ESLint**: Code linting and style enforcement
- **Prettier**: Code formatting
- **Metro**: JavaScript bundler
- **Babel**: JavaScript compiler

## 📁 Project Structure

```
blatam-academy/
├── app/                          # Expo Router screens
│   ├── (auth)/                   # Authentication screens
│   ├── (modals)/                 # Modal screens
│   ├── (tabs)/                   # Tab navigation screens
│   └── _layout.tsx              # Root layout
├── components/                   # Reusable UI components
│   ├── data-display/            # Data visualization components
│   ├── i18n-components/         # Internationalization components
│   ├── overlays/                # Modal and overlay components
│   └── OptimizedImage.tsx       # Optimized image component
├── hooks/                       # Custom React hooks
│   ├── i18n-hooks/             # Internationalization hooks
│   └── data-hooks/             # Data management hooks
├── lib/                         # Core libraries and configurations
├── utils/                       # Utility functions
│   ├── i18n/                   # Internationalization utilities
│   │   ├── translations/       # Translation files
│   │   └── i18nConfig.ts      # i18n configuration
│   ├── performance/            # Performance monitoring
│   ├── error-handling/         # Error boundary components
│   └── analytics/              # Analytics service
├── app.json                     # Expo configuration
├── eas.json                     # EAS Build configuration
├── metro.config.js              # Metro bundler configuration
├── babel.config.js              # Babel configuration
├── tsconfig.json                # TypeScript configuration
└── package.json                 # Dependencies and scripts
```

## 🌍 Internationalization (i18n)

### Supported Languages
- 🇺🇸 English (en)
- 🇪🇸 Spanish (es)
- 🇫🇷 French (fr)
- 🇩🇪 German (de)
- 🇵🇹 Portuguese (pt)
- 🇸🇦 Arabic (ar) - RTL support
- 🇨🇳 Chinese (zh)
- 🇯🇵 Japanese (ja)
- 🇰🇷 Korean (ko)
- 🇷🇺 Russian (ru)

### Usage

#### Basic Translation
```tsx
import { useI18n } from '../hooks/i18n-hooks/useI18n';

const MyComponent = () => {
  const { t } = useI18n();
  return <Text>{t('common.loading')}</Text>;
};
```

#### Optimized Translated Text Component
```tsx
import { OptimizedTranslatedText } from '../components/i18n-components/OptimizedTranslatedText';

const MyComponent = () => {
  return (
    <OptimizedTranslatedText
      translationKey="auth.welcome"
      values={{ name: 'John' }}
    />
  );
};
```

#### Language Selector
```tsx
import { OptimizedLanguageSelector } from '../components/i18n-components/OptimizedLanguageSelector';

const SettingsScreen = () => {
  const handleLanguageChange = (languageCode: string) => {
    console.log('Language changed to:', languageCode);
  };

  return (
    <OptimizedLanguageSelector
      onLanguageChange={handleLanguageChange}
      showNativeNames={true}
      showFlags={true}
    />
  );
};
```

### Adding New Languages

1. Create a new translation file in `utils/i18n/translations/`:
```typescript
// utils/i18n/translations/it.ts
export default {
  common: {
    loading: 'Caricamento...',
    // ... other translations
  },
  // ... other sections
};
```

2. Add the language to the supported languages in `utils/i18n/i18nConfig.ts`:
```typescript
const SUPPORTED_LANGUAGES: LanguageConfig[] = [
  // ... existing languages
  {
    code: 'it',
    name: 'Italian',
    nativeName: 'Italiano',
    direction: 'ltr',
    isRTL: false,
  },
];
```

## ⚡ Performance Features

### Performance Monitoring
```tsx
import { measureAsync, measureSync } from '../utils/performance/PerformanceMonitor';

// Measure async operations
const data = await measureAsync('fetch_courses', async () => {
  return await api.getCourses();
});

// Measure sync operations
const result = measureSync('process_data', () => {
  return processData(rawData);
});
```

### Optimized Components
- **FlashList**: High-performance list rendering for large datasets
- **FastImage**: Optimized image loading with caching
- **Skeleton Placeholder**: Smooth loading states
- **Memoized Components**: React.memo for performance optimization

## 🛡 Error Handling

### Error Boundary
```tsx
import { ErrorBoundary } from '../utils/error-handling/ErrorBoundary';

const App = () => {
  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        console.error('App error:', error, errorInfo);
      }}
    >
      <YourApp />
    </ErrorBoundary>
  );
};
```

### Analytics Integration
```tsx
import { trackEvent, trackScreen, trackError } from '../utils/analytics/AnalyticsService';

// Track user actions
trackEvent('course_enrolled', { courseId: '123', userId: '456' });

// Track screen views
trackScreen('CourseDetails', { courseId: '123' });

// Track errors
try {
  // Some operation
} catch (error) {
  trackError(error, { context: 'course_enrollment' });
}
```

## 🚀 Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- Expo CLI
- iOS Simulator (for iOS development)
- Android Studio (for Android development)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/blatam-academy.git
cd blatam-academy
```

2. **Install dependencies**
```bash
npm install
```

3. **Start the development server**
```bash
npm start
```

4. **Run on device/simulator**
```bash
# iOS
npm run ios

# Android
npm run android
```

## 📱 Building & Deployment

### Development Build
```bash
eas build --profile development --platform all
```

### Production Build
```bash
eas build --profile production --platform all
```

### Submit to App Stores
```bash
# iOS App Store
eas submit --platform ios

# Google Play Store
eas submit --platform android
```

## 🧪 Testing

### Unit Tests
```bash
npm test
```

### E2E Tests
```bash
npm run test:e2e
```

### Performance Tests
```bash
npm run test:performance
```

## 📊 Performance Monitoring

The app includes comprehensive performance monitoring:

- **Real-time Metrics**: Track component render times and user interactions
- **Memory Usage**: Monitor memory consumption and leaks
- **Network Performance**: Track API call performance
- **Bundle Analysis**: Analyze JavaScript bundle size and optimization

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
API_BASE_URL=https://api.blatam-academy.com
ANALYTICS_KEY=your_analytics_key
SENTRY_DSN=your_sentry_dsn
```

### Metro Configuration
The Metro bundler is configured for optimal performance:
- **Hermes Engine**: JavaScript engine optimization
- **Bundle Splitting**: Code splitting for faster loading
- **Asset Optimization**: Image and font optimization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow TypeScript strict mode
- Use functional components with hooks
- Implement proper error boundaries
- Add comprehensive tests
- Follow accessibility guidelines
- Optimize for performance

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.blatam-academy.com](https://docs.blatam-academy.com)
- **Issues**: [GitHub Issues](https://github.com/your-username/blatam-academy/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/blatam-academy/discussions)
- **Email**: support@blatam-academy.com

## 🙏 Acknowledgments

- **Expo Team**: For the amazing development platform
- **React Native Community**: For the excellent ecosystem
- **i18next Team**: For the robust internationalization framework
- **Shopify**: For the high-performance FlashList component

---

**Built with ❤️ by the Blatam Academy Team**
