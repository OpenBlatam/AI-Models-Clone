import React, { useCallback, useMemo } from 'react';
import { View, TouchableOpacity, Text, StyleSheet } from 'react-native';

interface TestComponentProps {
  title: string;
  onPress?: () => void;
  isEnabled?: boolean;
  testID?: string;
}

export const TestComponent: React.FC<TestComponentProps> = React.memo(({
  title,
  onPress,
  isEnabled = true,
  testID,
}) => {
  const handlePress = useCallback(() => {
    if (isEnabled && onPress) {
      onPress();
    }
  }, [isEnabled, onPress]);

  const buttonStyle = useMemo(() => [
    styles.button,
    !isEnabled && styles.buttonDisabled,
  ], [isEnabled]);

  const textStyle = useMemo(() => [
    styles.text,
    !isEnabled && styles.textDisabled,
  ], [isEnabled]);

  return (
    <TouchableOpacity
      style={buttonStyle}
      onPress={handlePress}
      disabled={!isEnabled}
      testID={testID}
      accessible={true}
      accessibilityRole="button"
      accessibilityLabel={title}
      accessibilityState={{ disabled: !isEnabled }}
    >
      <Text style={textStyle}>{title}</Text>
    </TouchableOpacity>
  );
});

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#C7C7CC',
  },
  text: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  textDisabled: {
    color: '#8E8E93',
  },
}); 