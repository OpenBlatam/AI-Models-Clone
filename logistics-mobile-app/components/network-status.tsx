import React, { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Animated, { useSharedValue, useAnimatedStyle, withSpring, withTiming } from 'react-native-reanimated';
import { useNetworkStatus } from '@/hooks/use-network-status';
import { useTheme } from '@/contexts/theme-context';

export function NetworkStatus() {
  const { isConnected } = useNetworkStatus();
  const { theme } = useTheme();
  const translateY = useSharedValue(-100);
  const opacity = useSharedValue(0);

  useEffect(() => {
    if (isConnected === false) {
      translateY.value = withSpring(0);
      opacity.value = withTiming(1);
    } else {
      translateY.value = withSpring(-100);
      opacity.value = withTiming(0);
    }
  }, [isConnected]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: translateY.value }],
    opacity: opacity.value,
  }));

  if (isConnected !== false) {
    return null;
  }

  return (
    <Animated.View
      style={[
        styles.container,
        {
          backgroundColor: theme.colors.error,
        },
        animatedStyle,
      ]}
    >
      <Text style={styles.text}>No internet connection</Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    paddingVertical: 12,
    paddingHorizontal: 16,
    zIndex: 1000,
  },
  text: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
});


