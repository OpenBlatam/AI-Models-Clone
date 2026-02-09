import { useColorScheme as useRNColorScheme } from 'react-native';
import { useMemo } from 'react';

export function useColorScheme() {
  const systemColorScheme = useRNColorScheme();
  
  return useMemo(
    () => ({
      isDark: systemColorScheme === 'dark',
      colorScheme: systemColorScheme ?? 'light',
    }),
    [systemColorScheme]
  );
}


