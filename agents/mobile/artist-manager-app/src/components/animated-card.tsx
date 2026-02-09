import { ReactNode, useEffect } from 'react';
import { View, StyleSheet, ViewStyle, Pressable } from 'react-native';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
} from 'react-native-reanimated';
import { useCallback } from 'react';
import { Colors } from '@/constants/colors';
import { useColorScheme } from '@/hooks/use-color-scheme';

interface AnimatedCardProps {
  children: ReactNode;
  style?: ViewStyle;
  padding?: number;
  onPress?: () => void;
  delay?: number;
}

const AnimatedView = Animated.createAnimatedComponent(View);
const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

export function AnimatedCard({ children, style, padding = 16, onPress, delay = 0 }: AnimatedCardProps) {
  const { isDark } = useColorScheme();
  const colors = isDark ? Colors.dark : Colors.light;
  const opacity = useSharedValue(0);
  const translateY = useSharedValue(20);
  const scale = useSharedValue(0.95);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [{ translateY: translateY.value }, { scale: scale.value }],
  }));

  const handlePressIn = useCallback(() => {
    if (onPress) {
      scale.value = withSpring(0.98);
    }
  }, [onPress, scale]);

  const handlePressOut = useCallback(() => {
    if (onPress) {
      scale.value = withSpring(1);
    }
  }, [onPress, scale]);

  const pressStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  useEffect(() => {
    const timer = setTimeout(() => {
      opacity.value = withTiming(1, { duration: 300 });
      translateY.value = withSpring(0, { damping: 15, stiffness: 100 });
      scale.value = withSpring(1, { damping: 15, stiffness: 100 });
    }, delay);

    return () => clearTimeout(timer);
  }, [delay, opacity, translateY, scale]);

  const cardStyle = [
    styles.card,
    {
      backgroundColor: colors.card,
      borderColor: colors.border,
      padding,
    },
    animatedStyle,
    onPress && pressStyle,
    style,
  ];

  if (onPress) {
    return (
      <AnimatedPressable style={cardStyle} onPress={onPress} onPressIn={handlePressIn} onPressOut={handlePressOut}>
        {children}
      </AnimatedPressable>
    );
  }

  return <AnimatedView style={cardStyle}>{children}</AnimatedView>;
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 12,
    borderWidth: 1,
    marginVertical: 8,
    marginHorizontal: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
});

