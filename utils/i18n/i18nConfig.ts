import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Localization from 'expo-localization';
import { Platform } from 'react-native';

// ============================================================================
// TYPES
// ============================================================================

interface LanguageConfig {
  code: string;
  name: string;
  nativeName: string;
  direction: 'ltr' | 'rtl';
  isRTL: boolean;
}

interface I18nConfig {
  fallbackLng: string;
  supportedLngs: string[];
  debug: boolean;
  interpolation: {
    escapeValue: boolean;
  };
  react: {
    useSuspense: boolean;
  };
  resources: Record<string, any>;
}

// ============================================================================
// STATIC CONTENT
// ============================================================================

const SUPPORTED_LANGUAGES: Record<string, LanguageConfig> = {
  en: {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    direction: 'ltr',
    isRTL: false,
  },
  es: {
    code: 'es',
    name: 'Spanish',
    nativeName: 'Español',
    direction: 'ltr',
    isRTL: false,
  },
  fr: {
    code: 'fr',
    name: 'French',
    nativeName: 'Français',
    direction: 'ltr',
    isRTL: false,
  },
  de: {
    code: 'de',
    name: 'German',
    nativeName: 'Deutsch',
    direction: 'ltr',
    isRTL: false,
  },
  pt: {
    code: 'pt',
    name: 'Portuguese',
    nativeName: 'Português',
    direction: 'ltr',
    isRTL: false,
  },
  ar: {
    code: 'ar',
    name: 'Arabic',
    nativeName: 'العربية',
    direction: 'rtl',
    isRTL: true,
  },
  zh: {
    code: 'zh',
    name: 'Chinese',
    nativeName: '中文',
    direction: 'ltr',
    isRTL: false,
  },
  ja: {
    code: 'ja',
    name: 'Japanese',
    nativeName: '日本語',
    direction: 'ltr',
    isRTL: false,
  },
  ko: {
    code: 'ko',
    name: 'Korean',
    nativeName: '한국어',
    direction: 'ltr',
    isRTL: false,
  },
  ru: {
    code: 'ru',
    name: 'Russian',
    nativeName: 'Русский',
    direction: 'ltr',
    isRTL: false,
  },
} as const;

const STORAGE_KEYS = {
  LANGUAGE: '@i18n_language',
  DIRECTION: '@i18n_direction',
} as const;

const DEFAULT_CONFIG: I18nConfig = {
  fallbackLng: 'en',
  supportedLngs: Object.keys(SUPPORTED_LANGUAGES),
  debug: __DEV__,
  interpolation: {
    escapeValue: false,
  },
  react: {
    useSuspense: false,
  },
  resources: {},
} as const;

// ============================================================================
// HELPERS
// ============================================================================

const detectDeviceLanguage = (): string => {
  try {
    const deviceLocale = Localization.locale;
    const languageCode = deviceLocale.split('-')[0];
    
    if (SUPPORTED_LANGUAGES[languageCode]) {
      return languageCode;
    }
    
    // Fallback to English if device language not supported
    return DEFAULT_CONFIG.fallbackLng;
  } catch (error) {
    console.warn('Failed to detect device language:', error);
    return DEFAULT_CONFIG.fallbackLng;
  }
};

const loadLanguageFromStorage = async (): Promise<string> => {
  try {
    const storedLanguage = await AsyncStorage.getItem(STORAGE_KEYS.LANGUAGE);
    return storedLanguage && SUPPORTED_LANGUAGES[storedLanguage] 
      ? storedLanguage 
      : detectDeviceLanguage();
  } catch (error) {
    console.warn('Failed to load language from storage:', error);
    return detectDeviceLanguage();
  }
};

const saveLanguageToStorage = async (language: string): Promise<void> => {
  try {
    await AsyncStorage.setItem(STORAGE_KEYS.LANGUAGE, language);
    await AsyncStorage.setItem(STORAGE_KEYS.DIRECTION, SUPPORTED_LANGUAGES[language].direction);
  } catch (error) {
    console.warn('Failed to save language to storage:', error);
  }
};

const loadTranslationResources = async (language: string): Promise<any> => {
  try {
    // Dynamic import for better performance
    const module = await import(`./translations/${language}.ts`);
    return module.default;
  } catch (error) {
    console.warn(`Failed to load translations for ${language}:`, error);
    // Fallback to English
    const fallbackModule = await import('./translations/en.ts');
    return fallbackModule.default;
  }
};

// ============================================================================
// I18N INITIALIZATION
// ============================================================================

const initializeI18n = async (): Promise<void> => {
  try {
    const detectedLanguage = await loadLanguageFromStorage();
    
    // Load initial resources
    const initialResources = await loadTranslationResources(detectedLanguage);
    
    await i18n
      .use(initReactI18next)
      .init({
        ...DEFAULT_CONFIG,
        lng: detectedLanguage,
        resources: {
          [detectedLanguage]: initialResources,
        },
        backend: {
          loadPath: '{{lng}}',
          addPath: '{{lng}}',
        },
        detection: {
          order: ['localStorage', 'navigator'],
          caches: ['localStorage'],
        },
      });
    
    // Set up language change listener
    i18n.on('languageChanged', async (newLanguage: string) => {
      try {
        await saveLanguageToStorage(newLanguage);
        
        // Load new language resources if not already loaded
        if (!i18n.hasResourceBundle(newLanguage, 'translation')) {
          const newResources = await loadTranslationResources(newLanguage);
          i18n.addResourceBundle(newLanguage, 'translation', newResources, true, true);
        }
      } catch (error) {
        console.warn('Failed to handle language change:', error);
      }
    });
    
  } catch (error) {
    console.error('Failed to initialize i18n:', error);
    // Fallback initialization
    await i18n.use(initReactI18next).init(DEFAULT_CONFIG);
  }
};

// ============================================================================
// LANGUAGE MANAGEMENT
// ============================================================================

const changeLanguage = async (languageCode: string): Promise<boolean> => {
  try {
    if (!SUPPORTED_LANGUAGES[languageCode]) {
      console.warn(`Unsupported language: ${languageCode}`);
      return false;
    }
    
    await i18n.changeLanguage(languageCode);
    return true;
  } catch (error) {
    console.warn('Failed to change language:', error);
    return false;
  }
};

const getCurrentLanguage = (): string => {
  return i18n.language || DEFAULT_CONFIG.fallbackLng;
};

const getLanguageConfig = (languageCode: string): LanguageConfig | null => {
  return SUPPORTED_LANGUAGES[languageCode] || null;
};

const getAllLanguages = (): LanguageConfig[] => {
  return Object.values(SUPPORTED_LANGUAGES);
};

const isRTL = (): boolean => {
  const currentLanguage = getCurrentLanguage();
  const config = getLanguageConfig(currentLanguage);
  return config?.isRTL || false;
};

const getTextDirection = (): 'ltr' | 'rtl' => {
  const currentLanguage = getCurrentLanguage();
  const config = getLanguageConfig(currentLanguage);
  return config?.direction || 'ltr';
};

// ============================================================================
// PERFORMANCE OPTIMIZATIONS
// ============================================================================

const preloadLanguage = async (languageCode: string): Promise<void> => {
  try {
    if (!SUPPORTED_LANGUAGES[languageCode]) return;
    
    const resources = await loadTranslationResources(languageCode);
    i18n.addResourceBundle(languageCode, 'translation', resources, true, true);
  } catch (error) {
    console.warn(`Failed to preload language ${languageCode}:`, error);
  }
};

const preloadAllLanguages = async (): Promise<void> => {
  const preloadPromises = Object.keys(SUPPORTED_LANGUAGES).map(preloadLanguage);
  await Promise.allSettled(preloadPromises);
};

// ============================================================================
// EXPORTS
// ============================================================================

export {
  i18n,
  initializeI18n,
  changeLanguage,
  getCurrentLanguage,
  getLanguageConfig,
  getAllLanguages,
  isRTL,
  getTextDirection,
  preloadLanguage,
  preloadAllLanguages,
  SUPPORTED_LANGUAGES,
  STORAGE_KEYS,
  DEFAULT_CONFIG,
};

export type { LanguageConfig, I18nConfig };
