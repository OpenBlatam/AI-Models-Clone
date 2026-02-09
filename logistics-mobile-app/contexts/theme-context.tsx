import React, { createContext, useContext, useEffect, useState } from 'react';
import { useColorScheme } from 'react-native';
import { Colors } from '@/constants/colors';

interface Theme {
  colors: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    error: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
    border: string;
  };
  isDark: boolean;
}

const lightTheme: Theme = {
  colors: {
    primary: Colors.primary,
    secondary: Colors.secondary,
    success: Colors.success,
    warning: Colors.warning,
    error: Colors.error,
    background: Colors.background,
    surface: Colors.surface,
    text: Colors.text,
    textSecondary: Colors.textSecondary,
    border: Colors.border,
  },
  isDark: false,
};

const darkTheme: Theme = {
  colors: {
    primary: '#0A84FF',
    secondary: '#5E5CE6',
    success: '#30D158',
    warning: '#FF9F0A',
    error: '#FF453A',
    background: '#000000',
    surface: '#1C1C1E',
    text: '#FFFFFF',
    textSecondary: '#98989D',
    border: '#38383A',
  },
  isDark: true,
};

interface ThemeContextValue {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (isDark: boolean) => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const systemColorScheme = useColorScheme();
  const [isDark, setIsDark] = useState(systemColorScheme === 'dark');

  useEffect(() => {
    if (systemColorScheme) {
      setIsDark(systemColorScheme === 'dark');
    }
  }, [systemColorScheme]);

  function toggleTheme() {
    setIsDark((prev) => !prev);
  }

  function setTheme(dark: boolean) {
    setIsDark(dark);
  }

  const theme = isDark ? darkTheme : lightTheme;

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}


