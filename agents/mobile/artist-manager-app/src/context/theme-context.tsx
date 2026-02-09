import { createContext, useContext, ReactNode } from 'react';
import { useColorScheme as useRNColorScheme } from 'react-native';
import { Colors } from '@/constants/colors';

interface ThemeContextValue {
  isDark: boolean;
  colorScheme: 'light' | 'dark';
  colors: typeof Colors.light | typeof Colors.dark;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const systemColorScheme = useRNColorScheme();
  const isDark = systemColorScheme === 'dark';
  const colorScheme = systemColorScheme ?? 'light';
  const colors = isDark ? Colors.dark : Colors.light;

  return (
    <ThemeContext.Provider value={{ isDark, colorScheme, colors }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}


