import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/colors';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Button } from './button';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  retryLabel?: string;
  accessibilityLabel?: string;
}

export function ErrorMessage({
  message,
  onRetry,
  retryLabel = 'Retry',
  accessibilityLabel,
}: ErrorMessageProps) {
  const { isDark } = useColorScheme();
  const colors = isDark ? Colors.dark : Colors.light;

  return (
    <View
      style={[styles.container, { backgroundColor: colors.card }]}
      accessibilityRole="alert"
      accessibilityLabel={accessibilityLabel || message}
    >
      <Ionicons name="alert-circle" size={24} color={colors.error} style={styles.icon} />
      <Text style={[styles.message, { color: colors.text }]}>{message}</Text>
      {onRetry && (
        <Button
          title={retryLabel}
          onPress={onRetry}
          variant="primary"
          style={styles.retryButton}
          accessibilityLabel={`${retryLabel} ${message}`}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    margin: 16,
  },
  icon: {
    marginBottom: 12,
  },
  message: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 16,
  },
  retryButton: {
    marginTop: 8,
  },
});

