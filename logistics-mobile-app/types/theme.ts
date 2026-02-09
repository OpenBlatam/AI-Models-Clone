// Theme Types

export interface ColorPalette {
  primary: string;
  primaryDark: string;
  primaryLight: string;
  secondary: string;
  secondaryDark: string;
  secondaryLight: string;
  success: string;
  successDark: string;
  successLight: string;
  warning: string;
  warningDark: string;
  warningLight: string;
  error: string;
  errorDark: string;
  errorLight: string;
  info: string;
  infoDark: string;
  infoLight: string;
  background: string;
  surface: string;
  surfaceSecondary: string;
  text: string;
  textSecondary: string;
  textTertiary: string;
  border: string;
  divider: string;
  overlay: string;
  overlayLight: string;
  overlayDark: string;
  transparent: string;
}

export interface Theme {
  colors: ColorPalette;
  spacing: {
    xs: number;
    sm: number;
    md: number;
    lg: number;
    xl: number;
    xxl: number;
    xxxl: number;
  };
  typography: {
    fontSize: {
      xs: number;
      sm: number;
      md: number;
      lg: number;
      xl: number;
      xxl: number;
      xxxl: number;
      h1: number;
      h2: number;
      h3: number;
      h4: number;
      h5: number;
      h6: number;
    };
    fontWeight: {
      light: string;
      normal: string;
      medium: string;
      semibold: string;
      bold: string;
      extrabold: string;
    };
    lineHeight: {
      tight: number;
      normal: number;
      relaxed: number;
      loose: number;
    };
  };
  borderRadius: {
    xs: number;
    sm: number;
    md: number;
    lg: number;
    xl: number;
    full: number;
  };
  shadows: {
    none: object;
    low: object;
    medium: object;
    high: object;
    veryHigh: object;
  };
  isDark: boolean;
}

export interface ThemeContextValue {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (isDark: boolean) => void;
}

export type ThemeMode = 'light' | 'dark' | 'auto';

