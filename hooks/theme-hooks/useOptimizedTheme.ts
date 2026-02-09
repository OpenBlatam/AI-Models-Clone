import { useColorScheme } from 'react-native';
import { useMemo, useCallback, createContext, useContext, useState, useEffect } from 'react';

// ============================================================================
// TYPES
// ============================================================================

export interface ThemeColors {
  // Primary colors
  primary: string;
  primaryLight: string;
  primaryDark: string;
  primaryContrast: string;
  
  // Secondary colors
  secondary: string;
  secondaryLight: string;
  secondaryDark: string;
  secondaryContrast: string;
  
  // Background colors
  background: string;
  backgroundSecondary: string;
  backgroundTertiary: string;
  surface: string;
  surfaceSecondary: string;
  
  // Text colors
  text: string;
  textSecondary: string;
  textTertiary: string;
  textInverse: string;
  textInverseSecondary: string;
  
  // Status colors
  success: string;
  successLight: string;
  successDark: string;
  warning: string;
  warningLight: string;
  warningDark: string;
  error: string;
  errorLight: string;
  errorDark: string;
  info: string;
  infoLight: string;
  infoDark: string;
  
  // Border colors
  border: string;
  borderSecondary: string;
  borderTertiary: string;
  
  // Shadow colors
  shadow: string;
  shadowLight: string;
  shadowDark: string;
  
  // Overlay colors
  overlay: string;
  overlayLight: string;
  overlayDark: string;
  
  // Special colors
  accent: string;
  highlight: string;
  muted: string;
  disabled: string;
}

export interface ThemeSpacing {
  xs: number;
  sm: number;
  md: number;
  lg: number;
  xl: number;
  xxl: number;
  xxxl: number;
}

export interface ThemeBorderRadius {
  none: number;
  xs: number;
  sm: number;
  md: number;
  lg: number;
  xl: number;
  xxl: number;
  round: number;
}

export interface ThemeTypography {
  h1: {
    fontSize: number;
    fontWeight: string;
    lineHeight: number;
    letterSpacing: number;
  };
  h2: {
    fontSize: number;
    fontWeight: string;
    lineHeight: number;
    letterSpacing: number;
  };
  h3: {
    fontSize: number;
    fontWeight: string;
    lineHeight: number;
    letterSpacing: number;
  };
  h4: {
    fontSize: number;
    fontWeight: string;
    lineHeight: number;
    letterSpacing: number;
  };
  h5: {
    fontSize: number;
    fontWeight: string;
    lineHeight: number;
    letterSpacing: number;
  };
  h6: {
    fontSize: number;
    fontWeight: string;
    lineHeight: number;
    letterSpacing: number;
  };
  body: {
    fontSize: number;
    fontWeight: string;
    lineHeight: number;
    letterSpacing: number;
  };
  bodySmall: {
    fontSize: number;
    fontWeight: string;
    lineHeight: number;
    letterSpacing: number;
  };
  bodyLarge: {
    fontSize: number;
    fontWeight: string;
    lineHeight: number;
    letterSpacing: number;
  };
  caption: {
    fontSize: number;
    fontWeight: string;
    lineHeight: number;
    letterSpacing: number;
  };
  button: {
    fontSize: number;
    fontWeight: string;
    lineHeight: number;
    letterSpacing: number;
  };
  buttonSmall: {
    fontSize: number;
    fontWeight: string;
    lineHeight: number;
    letterSpacing: number;
  };
  buttonLarge: {
    fontSize: number;
    fontWeight: string;
    lineHeight: number;
    letterSpacing: number;
  };
}

export interface ThemeShadows {
  none: {
    shadowColor: string;
    shadowOffset: { width: number; height: number };
    shadowOpacity: number;
    shadowRadius: number;
    elevation: number;
  };
  sm: {
    shadowColor: string;
    shadowOffset: { width: number; height: number };
    shadowOpacity: number;
    shadowRadius: number;
    elevation: number;
  };
  md: {
    shadowColor: string;
    shadowOffset: { width: number; height: number };
    shadowOpacity: number;
    shadowRadius: number;
    elevation: number;
  };
  lg: {
    shadowColor: string;
    shadowOffset: { width: number; height: number };
    shadowOpacity: number;
    shadowRadius: number;
    elevation: number;
  };
  xl: {
    shadowColor: string;
    shadowOffset: { width: number; height: number };
    shadowOpacity: number;
    shadowRadius: number;
    elevation: number;
  };
}

export interface Theme {
  colors: ThemeColors;
  spacing: ThemeSpacing;
  borderRadius: ThemeBorderRadius;
  typography: ThemeTypography;
  shadows: ThemeShadows;
  isDark: boolean;
}

export interface ThemeContextType {
  theme: Theme;
  isDark: boolean;
  toggleTheme: () => void;
  setTheme: (isDark: boolean) => void;
  setCustomTheme: (customTheme: Partial<Theme>) => void;
}

// ============================================================================
// STATIC CONTENT
// ============================================================================

const LIGHT_COLORS: ThemeColors = {
  // Primary colors
  primary: '#007AFF',
  primaryLight: '#4DA3FF',
  primaryDark: '#0056CC',
  primaryContrast: '#FFFFFF',
  
  // Secondary colors
  secondary: '#5856D6',
  secondaryLight: '#7B7AFF',
  secondaryDark: '#3F3D99',
  secondaryContrast: '#FFFFFF',
  
  // Background colors
  background: '#FFFFFF',
  backgroundSecondary: '#F2F2F7',
  backgroundTertiary: '#E5E5EA',
  surface: '#FFFFFF',
  surfaceSecondary: '#F8F9FA',
  
  // Text colors
  text: '#000000',
  textSecondary: '#6C6C70',
  textTertiary: '#8E8E93',
  textInverse: '#FFFFFF',
  textInverseSecondary: '#F2F2F7',
  
  // Status colors
  success: '#34C759',
  successLight: '#69DB7C',
  successDark: '#28A745',
  warning: '#FF9500',
  warningLight: '#FFB84D',
  warningDark: '#E6850E',
  error: '#FF3B30',
  errorLight: '#FF6B6B',
  errorDark: '#D70015',
  info: '#5AC8FA',
  infoLight: '#8EDDFF',
  infoDark: '#007AFF',
  
  // Border colors
  border: '#E5E5EA',
  borderSecondary: '#F2F2F7',
  borderTertiary: '#F8F9FA',
  
  // Shadow colors
  shadow: '#000000',
  shadowLight: '#000000',
  shadowDark: '#000000',
  
  // Overlay colors
  overlay: 'rgba(0, 0, 0, 0.5)',
  overlayLight: 'rgba(0, 0, 0, 0.3)',
  overlayDark: 'rgba(0, 0, 0, 0.7)',
  
  // Special colors
  accent: '#FF9500',
  highlight: '#FFF3CD',
  muted: '#6C757D',
  disabled: '#E5E5EA',
};

const DARK_COLORS: ThemeColors = {
  // Primary colors
  primary: '#0A84FF',
  primaryLight: '#4DA3FF',
  primaryDark: '#0056CC',
  primaryContrast: '#FFFFFF',
  
  // Secondary colors
  secondary: '#5E5CE6',
  secondaryLight: '#7B7AFF',
  secondaryDark: '#3F3D99',
  secondaryContrast: '#FFFFFF',
  
  // Background colors
  background: '#000000',
  backgroundSecondary: '#1C1C1E',
  backgroundTertiary: '#2C2C2E',
  surface: '#1C1C1E',
  surfaceSecondary: '#2C2C2E',
  
  // Text colors
  text: '#FFFFFF',
  textSecondary: '#8E8E93',
  textTertiary: '#6C6C70',
  textInverse: '#000000',
  textInverseSecondary: '#1C1C1E',
  
  // Status colors
  success: '#30D158',
  successLight: '#69DB7C',
  successDark: '#28A745',
  warning: '#FF9F0A',
  warningLight: '#FFB84D',
  warningDark: '#E6850E',
  error: '#FF453A',
  errorLight: '#FF6B6B',
  errorDark: '#D70015',
  info: '#64D2FF',
  infoLight: '#8EDDFF',
  infoDark: '#007AFF',
  
  // Border colors
  border: '#3A3A3C',
  borderSecondary: '#2C2C2E',
  borderTertiary: '#1C1C1E',
  
  // Shadow colors
  shadow: '#000000',
  shadowLight: '#000000',
  shadowDark: '#000000',
  
  // Overlay colors
  overlay: 'rgba(255, 255, 255, 0.1)',
  overlayLight: 'rgba(255, 255, 255, 0.05)',
  overlayDark: 'rgba(255, 255, 255, 0.2)',
  
  // Special colors
  accent: '#FF9F0A',
  highlight: '#2C2C2E',
  muted: '#8E8E93',
  disabled: '#3A3A3C',
};

const SPACING: ThemeSpacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
  xxxl: 64,
};

const BORDER_RADIUS: ThemeBorderRadius = {
  none: 0,
  xs: 2,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  xxl: 24,
  round: 999,
};

const TYPOGRAPHY: ThemeTypography = {
  h1: {
    fontSize: 32,
    fontWeight: '700',
    lineHeight: 40,
    letterSpacing: -0.5,
  },
  h2: {
    fontSize: 28,
    fontWeight: '600',
    lineHeight: 36,
    letterSpacing: -0.25,
  },
  h3: {
    fontSize: 24,
    fontWeight: '600',
    lineHeight: 32,
    letterSpacing: 0,
  },
  h4: {
    fontSize: 20,
    fontWeight: '600',
    lineHeight: 28,
    letterSpacing: 0.15,
  },
  h5: {
    fontSize: 18,
    fontWeight: '500',
    lineHeight: 24,
    letterSpacing: 0.15,
  },
  h6: {
    fontSize: 16,
    fontWeight: '500',
    lineHeight: 24,
    letterSpacing: 0.15,
  },
  body: {
    fontSize: 16,
    fontWeight: '400',
    lineHeight: 24,
    letterSpacing: 0.5,
  },
  bodySmall: {
    fontSize: 14,
    fontWeight: '400',
    lineHeight: 20,
    letterSpacing: 0.25,
  },
  bodyLarge: {
    fontSize: 18,
    fontWeight: '400',
    lineHeight: 28,
    letterSpacing: 0.15,
  },
  caption: {
    fontSize: 12,
    fontWeight: '400',
    lineHeight: 16,
    letterSpacing: 0.4,
  },
  button: {
    fontSize: 16,
    fontWeight: '600',
    lineHeight: 24,
    letterSpacing: 0.1,
  },
  buttonSmall: {
    fontSize: 14,
    fontWeight: '600',
    lineHeight: 20,
    letterSpacing: 0.1,
  },
  buttonLarge: {
    fontSize: 18,
    fontWeight: '600',
    lineHeight: 28,
    letterSpacing: 0.1,
  },
};

const createShadows = (shadowColor: string): ThemeShadows => ({
  none: {
    shadowColor,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0,
    shadowRadius: 0,
    elevation: 0,
  },
  sm: {
    shadowColor,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  lg: {
    shadowColor,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
  xl: {
    shadowColor,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 6,
  },
});

// ============================================================================
// THEME CREATION
// ============================================================================

const createLightTheme = (): Theme => ({
  colors: LIGHT_COLORS,
  spacing: SPACING,
  borderRadius: BORDER_RADIUS,
  typography: TYPOGRAPHY,
  shadows: createShadows(LIGHT_COLORS.shadow),
  isDark: false,
});

const createDarkTheme = (): Theme => ({
  colors: DARK_COLORS,
  spacing: SPACING,
  borderRadius: BORDER_RADIUS,
  typography: TYPOGRAPHY,
  shadows: createShadows(DARK_COLORS.shadow),
  isDark: true,
});

// ============================================================================
// CONTEXT
// ============================================================================

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// ============================================================================
// HOOK
// ============================================================================

export function useOptimizedTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useOptimizedTheme must be used within a ThemeProvider');
  }
  return context;
}

// ============================================================================
// PROVIDER
// ============================================================================

interface ThemeProviderProps {
  children: React.ReactNode;
  initialTheme?: 'light' | 'dark' | 'system';
}

export function ThemeProvider({ children, initialTheme = 'system' }: ThemeProviderProps): JSX.Element {
  const systemColorScheme = useColorScheme();
  const [isDark, setIsDark] = useState(() => {
    if (initialTheme === 'system') {
      return systemColorScheme === 'dark';
    }
    return initialTheme === 'dark';
  });

  // Update theme when system preference changes
  useEffect(() => {
    if (initialTheme === 'system') {
      setIsDark(systemColorScheme === 'dark');
    }
  }, [systemColorScheme, initialTheme]);

  // Memoized theme object for performance
  const theme = useMemo(() => {
    return isDark ? createDarkTheme() : createLightTheme();
  }, [isDark]);

  // Memoized theme toggle function
  const toggleTheme = useCallback(() => {
    setIsDark(prev => !prev);
  }, []);

  // Memoized theme setter function
  const setTheme = useCallback((darkMode: boolean) => {
    setIsDark(darkMode);
  }, []);

  // Memoized custom theme setter function
  const setCustomTheme = useCallback((customTheme: Partial<Theme>) => {
    // This would allow for custom theme overrides
    // Implementation depends on your needs
    console.log('Custom theme override:', customTheme);
  }, []);

  // Memoized context value
  const contextValue = useMemo<ThemeContextType>(() => ({
    theme,
    isDark,
    toggleTheme,
    setTheme,
    setCustomTheme,
  }), [theme, isDark, toggleTheme, setTheme, setCustomTheme]);

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export function getThemeColors(isDark: boolean): ThemeColors {
  return isDark ? DARK_COLORS : LIGHT_COLORS;
}

export function getThemeSpacing(): ThemeSpacing {
  return SPACING;
}

export function getThemeBorderRadius(): ThemeBorderRadius {
  return BORDER_RADIUS;
}

export function getThemeTypography(): ThemeTypography {
  return TYPOGRAPHY;
}

export function getThemeShadows(isDark: boolean): ThemeShadows {
  return createShadows(isDark ? DARK_COLORS.shadow : LIGHT_COLORS.shadow);
} 
  backgroundSecondary: '#F2F2F7',
  backgroundTertiary: '#E5E5EA',
  surface: '#FFFFFF',
  surfaceSecondary: '#F8F9FA',
  
  // Text colors
  text: '#000000',
  textSecondary: '#6C6C70',
  textTertiary: '#8E8E93',
  textInverse: '#FFFFFF',
  textInverseSecondary: '#F2F2F7',
  
  // Status colors
  success: '#34C759',
  successLight: '#69DB7C',
  successDark: '#28A745',
  warning: '#FF9500',
  warningLight: '#FFB84D',
  warningDark: '#E6850E',
  error: '#FF3B30',
  errorLight: '#FF6B6B',
  errorDark: '#D70015',
  info: '#5AC8FA',
  infoLight: '#8EDDFF',
  infoDark: '#007AFF',
  
  // Border colors
  border: '#E5E5EA',
  borderSecondary: '#F2F2F7',
  borderTertiary: '#F8F9FA',
  
  // Shadow colors
  shadow: '#000000',
  shadowLight: '#000000',
  shadowDark: '#000000',
  
  // Overlay colors
  overlay: 'rgba(0, 0, 0, 0.5)',
  overlayLight: 'rgba(0, 0, 0, 0.3)',
  overlayDark: 'rgba(0, 0, 0, 0.7)',
  
  // Special colors
  accent: '#FF9500',
  highlight: '#FFF3CD',
  muted: '#6C757D',
  disabled: '#E5E5EA',
};

const DARK_COLORS: ThemeColors = {
  // Primary colors
  primary: '#0A84FF',
  primaryLight: '#4DA3FF',
  primaryDark: '#0056CC',
  primaryContrast: '#FFFFFF',
  
  // Secondary colors
  secondary: '#5E5CE6',
  secondaryLight: '#7B7AFF',
  secondaryDark: '#3F3D99',
  secondaryContrast: '#FFFFFF',
  
  // Background colors
  background: '#000000',
  backgroundSecondary: '#1C1C1E',
  backgroundTertiary: '#2C2C2E',
  surface: '#1C1C1E',
  surfaceSecondary: '#2C2C2E',
  
  // Text colors
  text: '#FFFFFF',
  textSecondary: '#8E8E93',
  textTertiary: '#6C6C70',
  textInverse: '#000000',
  textInverseSecondary: '#1C1C1E',
  
  // Status colors
  success: '#30D158',
  successLight: '#69DB7C',
  successDark: '#28A745',
  warning: '#FF9F0A',
  warningLight: '#FFB84D',
  warningDark: '#E6850E',
  error: '#FF453A',
  errorLight: '#FF6B6B',
  errorDark: '#D70015',
  info: '#64D2FF',
  infoLight: '#8EDDFF',
  infoDark: '#007AFF',
  
  // Border colors
  border: '#3A3A3C',
  borderSecondary: '#2C2C2E',
  borderTertiary: '#1C1C1E',
  
  // Shadow colors
  shadow: '#000000',
  shadowLight: '#000000',
  shadowDark: '#000000',
  
  // Overlay colors
  overlay: 'rgba(255, 255, 255, 0.1)',
  overlayLight: 'rgba(255, 255, 255, 0.05)',
  overlayDark: 'rgba(255, 255, 255, 0.2)',
  
  // Special colors
  accent: '#FF9F0A',
  highlight: '#2C2C2E',
  muted: '#8E8E93',
  disabled: '#3A3A3C',
};

const SPACING: ThemeSpacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
  xxxl: 64,
};

const BORDER_RADIUS: ThemeBorderRadius = {
  none: 0,
  xs: 2,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  xxl: 24,
  round: 999,
};

const TYPOGRAPHY: ThemeTypography = {
  h1: {
    fontSize: 32,
    fontWeight: '700',
    lineHeight: 40,
    letterSpacing: -0.5,
  },
  h2: {
    fontSize: 28,
    fontWeight: '600',
    lineHeight: 36,
    letterSpacing: -0.25,
  },
  h3: {
    fontSize: 24,
    fontWeight: '600',
    lineHeight: 32,
    letterSpacing: 0,
  },
  h4: {
    fontSize: 20,
    fontWeight: '600',
    lineHeight: 28,
    letterSpacing: 0.15,
  },
  h5: {
    fontSize: 18,
    fontWeight: '500',
    lineHeight: 24,
    letterSpacing: 0.15,
  },
  h6: {
    fontSize: 16,
    fontWeight: '500',
    lineHeight: 24,
    letterSpacing: 0.15,
  },
  body: {
    fontSize: 16,
    fontWeight: '400',
    lineHeight: 24,
    letterSpacing: 0.5,
  },
  bodySmall: {
    fontSize: 14,
    fontWeight: '400',
    lineHeight: 20,
    letterSpacing: 0.25,
  },
  bodyLarge: {
    fontSize: 18,
    fontWeight: '400',
    lineHeight: 28,
    letterSpacing: 0.15,
  },
  caption: {
    fontSize: 12,
    fontWeight: '400',
    lineHeight: 16,
    letterSpacing: 0.4,
  },
  button: {
    fontSize: 16,
    fontWeight: '600',
    lineHeight: 24,
    letterSpacing: 0.1,
  },
  buttonSmall: {
    fontSize: 14,
    fontWeight: '600',
    lineHeight: 20,
    letterSpacing: 0.1,
  },
  buttonLarge: {
    fontSize: 18,
    fontWeight: '600',
    lineHeight: 28,
    letterSpacing: 0.1,
  },
};

const createShadows = (shadowColor: string): ThemeShadows => ({
  none: {
    shadowColor,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0,
    shadowRadius: 0,
    elevation: 0,
  },
  sm: {
    shadowColor,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  lg: {
    shadowColor,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
  xl: {
    shadowColor,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 6,
  },
});

// ============================================================================
// THEME CREATION
// ============================================================================

const createLightTheme = (): Theme => ({
  colors: LIGHT_COLORS,
  spacing: SPACING,
  borderRadius: BORDER_RADIUS,
  typography: TYPOGRAPHY,
  shadows: createShadows(LIGHT_COLORS.shadow),
  isDark: false,
});

const createDarkTheme = (): Theme => ({
  colors: DARK_COLORS,
  spacing: SPACING,
  borderRadius: BORDER_RADIUS,
  typography: TYPOGRAPHY,
  shadows: createShadows(DARK_COLORS.shadow),
  isDark: true,
});

// ============================================================================
// CONTEXT
// ============================================================================

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// ============================================================================
// HOOK
// ============================================================================

export function useOptimizedTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useOptimizedTheme must be used within a ThemeProvider');
  }
  return context;
}

// ============================================================================
// PROVIDER
// ============================================================================

interface ThemeProviderProps {
  children: React.ReactNode;
  initialTheme?: 'light' | 'dark' | 'system';
}

export function ThemeProvider({ children, initialTheme = 'system' }: ThemeProviderProps): JSX.Element {
  const systemColorScheme = useColorScheme();
  const [isDark, setIsDark] = useState(() => {
    if (initialTheme === 'system') {
      return systemColorScheme === 'dark';
    }
    return initialTheme === 'dark';
  });

  // Update theme when system preference changes
  useEffect(() => {
    if (initialTheme === 'system') {
      setIsDark(systemColorScheme === 'dark');
    }
  }, [systemColorScheme, initialTheme]);

  // Memoized theme object for performance
  const theme = useMemo(() => {
    return isDark ? createDarkTheme() : createLightTheme();
  }, [isDark]);

  // Memoized theme toggle function
  const toggleTheme = useCallback(() => {
    setIsDark(prev => !prev);
  }, []);

  // Memoized theme setter function
  const setTheme = useCallback((darkMode: boolean) => {
    setIsDark(darkMode);
  }, []);

  // Memoized custom theme setter function
  const setCustomTheme = useCallback((customTheme: Partial<Theme>) => {
    // This would allow for custom theme overrides
    // Implementation depends on your needs
    console.log('Custom theme override:', customTheme);
  }, []);

  // Memoized context value
  const contextValue = useMemo<ThemeContextType>(() => ({
    theme,
    isDark,
    toggleTheme,
    setTheme,
    setCustomTheme,
  }), [theme, isDark, toggleTheme, setTheme, setCustomTheme]);

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export function getThemeColors(isDark: boolean): ThemeColors {
  return isDark ? DARK_COLORS : LIGHT_COLORS;
}

export function getThemeSpacing(): ThemeSpacing {
  return SPACING;
}

export function getThemeBorderRadius(): ThemeBorderRadius {
  return BORDER_RADIUS;
}

export function getThemeTypography(): ThemeTypography {
  return TYPOGRAPHY;
}

export function getThemeShadows(isDark: boolean): ThemeShadows {
  return createShadows(isDark ? DARK_COLORS.shadow : LIGHT_COLORS.shadow);
} 