import { ActivityIndicator, View, StyleSheet, Text } from 'react-native';
import { Colors } from '@/constants/colors';
import { useColorScheme } from '@/hooks/use-color-scheme';

interface LoadingSpinnerProps {
  size?: 'small' | 'large';
  fullScreen?: boolean;
  message?: string;
  accessibilityLabel?: string;
}

export function LoadingSpinner({
  size = 'large',
  fullScreen = false,
  message,
  accessibilityLabel,
}: LoadingSpinnerProps) {
  const { isDark } = useColorScheme();
  const colors = isDark ? Colors.dark : Colors.light;

  const containerStyle = fullScreen ? styles.fullScreen : styles.container;

  return (
    <View
      style={containerStyle}
      accessibilityRole="progressbar"
      accessibilityLabel={accessibilityLabel || message || 'Loading'}
      accessibilityLiveRegion="polite"
    >
      <ActivityIndicator size={size} color={colors.primary} />
      {message && (
        <Text style={[styles.message, { color: colors.icon }]}>{message}</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  fullScreen: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  message: {
    marginTop: 12,
    fontSize: 14,
    textAlign: 'center',
  },
});

