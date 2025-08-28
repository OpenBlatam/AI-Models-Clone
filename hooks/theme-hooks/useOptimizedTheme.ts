import { useState, useCallback, useMemo, useEffect } from 'react';
import { useColorScheme } from 'react-native';
import { useOptimizedStorage } from './useOptimizedStorage';

type ThemeMode = 'light' | 'dark' | 'system';
type ColorPalette = 'blue' | 'green' | 'purple' | 'orange' | 'red';

interface ThemeColors {
  primary: string;
  secondary: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  border: string;
  error: string;
  success: string;
  warning: string;
  info: string;
}

interface ThemeConfig {
  mode: ThemeMode;
  palette: ColorPalette;
  isHighContrast: boolean;
  isReducedMotion: boolean;
}

const lightColors: Record<ColorPalette, ThemeColors> = {
  blue: {
    primary: '#007AFF',
    secondary: '#5AC8FA',
    background: '#FFFFFF',
    surface: '#F2F2F7',
    text: '#000000',
    textSecondary: '#8E8E93',
    border: '#C6C6C8',
    error: '#FF3B30',
    success: '#34C759',
    warning: '#FF9500',
    info: '#5AC8FA',
  },
  green: {
    primary: '#34C759',
    secondary: '#30D158',
    background: '#FFFFFF',
    surface: '#F2F2F7',
    text: '#000000',
    textSecondary: '#8E8E93',
    border: '#C6C6C8',
    error: '#FF3B30',
    success: '#34C759',
    warning: '#FF9500',
    info: '#5AC8FA',
  },
  purple: {
    primary: '#AF52DE',
    secondary: '#BF5AF2',
    background: '#FFFFFF',
    surface: '#F2F2F7',
    text: '#000000',
    textSecondary: '#8E8E93',
    border: '#C6C6C8',
    error: '#FF3B30',
    success: '#34C759',
    warning: '#FF9500',
    info: '#5AC8FA',
  },
  orange: {
    primary: '#FF9500',
    secondary: '#FFB340',
    background: '#FFFFFF',
    surface: '#F2F2F7',
    text: '#000000',
    textSecondary: '#8E8E93',
    border: '#C6C6C8',
    error: '#FF3B30',
    success: '#34C759',
    warning: '#FF9500',
    info: '#5AC8FA',
  },
  red: {
    primary: '#FF3B30',
    secondary: '#FF6961',
    background: '#FFFFFF',
    surface: '#F2F2F7',
    text: '#000000',
    textSecondary: '#8E8E93',
    border: '#C6C6C8',
    error: '#FF3B30',
    success: '#34C759',
    warning: '#FF9500',
    info: '#5AC8FA',
  },
};

const darkColors: Record<ColorPalette, ThemeColors> = {
  blue: {
    primary: '#0A84FF',
    secondary: '#64D2FF',
    background: '#000000',
    surface: '#1C1C1E',
    text: '#FFFFFF',
    textSecondary: '#8E8E93',
    border: '#38383A',
    error: '#FF453A',
    success: '#32D74B',
    warning: '#FF9F0A',
    info: '#64D2FF',
  },
  green: {
    primary: '#32D74B',
    secondary: '#30D158',
    background: '#000000',
    surface: '#1C1C1E',
    text: '#FFFFFF',
    textSecondary: '#8E8E93',
    border: '#38383A',
    error: '#FF453A',
    success: '#32D74B',
    warning: '#FF9F0A',
    info: '#64D2FF',
  },
  purple: {
    primary: '#BF5AF2',
    secondary: '#DA8FFF',
    background: '#000000',
    surface: '#1C1C1E',
    text: '#FFFFFF',
    textSecondary: '#8E8E93',
    border: '#38383A',
    error: '#FF453A',
    success: '#32D74B',
    warning: '#FF9F0A',
    info: '#64D2FF',
  },
  orange: {
    primary: '#FF9F0A',
    secondary: '#FFB340',
    background: '#000000',
    surface: '#1C1C1E',
    text: '#FFFFFF',
    textSecondary: '#8E8E93',
    border: '#38383A',
    error: '#FF453A',
    success: '#32D74B',
    warning: '#FF9F0A',
    info: '#64D2FF',
  },
  red: {
    primary: '#FF453A',
    secondary: '#FF6961',
    background: '#000000',
    surface: '#1C1C1E',
    text: '#FFFFFF',
    textSecondary: '#8E8E93',
    border: '#38383A',
    error: '#FF453A',
    success: '#32D74B',
    warning: '#FF9F0A',
    info: '#64D2FF',
  },
};

export const useOptimizedTheme = () => {
  const systemColorScheme = useColorScheme();
  const { value: storedConfig, setValue: setStoredConfig } = useOptimizedStorage<ThemeConfig>('theme-config', {
    defaultValue: {
      mode: 'system',
      palette: 'blue',
      isHighContrast: false,
      isReducedMotion: false,
    },
  });

  const [config, setConfig] = useState<ThemeConfig>(storedConfig || {
    mode: 'system',
    palette: 'blue',
    isHighContrast: false,
    isReducedMotion: false,
  });

  const effectiveMode = useMemo(() => {
    if (config.mode === 'system') {
      return systemColorScheme || 'light';
    }
    return config.mode;
  }, [config.mode, systemColorScheme]);

  const colors = useMemo(() => {
    const colorPalette = effectiveMode === 'dark' ? darkColors : lightColors;
    return colorPalette[config.palette];
  }, [effectiveMode, config.palette]);

  const updateConfig = useCallback((newConfig: Partial<ThemeConfig>) => {
    const updatedConfig = { ...config, ...newConfig };
    setConfig(updatedConfig);
    setStoredConfig(updatedConfig);
  }, [config, setStoredConfig]);

  const setMode = useCallback((mode: ThemeMode) => {
    updateConfig({ mode });
  }, [updateConfig]);

  const setPalette = useCallback((palette: ColorPalette) => {
    updateConfig({ palette });
  }, [updateConfig]);

  const toggleHighContrast = useCallback(() => {
    updateConfig({ isHighContrast: !config.isHighContrast });
  }, [config.isHighContrast, updateConfig]);

  const toggleReducedMotion = useCallback(() => {
    updateConfig({ isReducedMotion: !config.isReducedMotion });
  }, [config.isReducedMotion, updateConfig]);

  const resetTheme = useCallback(() => {
    const defaultConfig: ThemeConfig = {
      mode: 'system',
      palette: 'blue',
      isHighContrast: false,
      isReducedMotion: false,
    };
    setConfig(defaultConfig);
    setStoredConfig(defaultConfig);
  }, [setStoredConfig]);

  useEffect(() => {
    if (storedConfig) {
      setConfig(storedConfig);
    }
  }, [storedConfig]);

  return {
    colors,
    config,
    effectiveMode,
    setMode,
    setPalette,
    toggleHighContrast,
    toggleReducedMotion,
    resetTheme,
    isDark: effectiveMode === 'dark',
    isLight: effectiveMode === 'light',
  };
}; 