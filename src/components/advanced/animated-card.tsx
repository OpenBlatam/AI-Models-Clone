import React, { useRef, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ViewStyle,
  TextStyle,
  TouchableOpacity,
  useWindowDimensions,
} from 'react-native';
import { useColorScheme } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  withSequence,
  withDelay,
  runOnJS,
  interpolate,
  Extrapolate,
} from 'react-native-reanimated';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import { Ionicons } from '@expo/vector-icons';

// ============================================================================
// TYPES
// ============================================================================

interface AnimatedCardProps {
  title: string;
  subtitle?: string;
  content?: string;
  icon?: keyof typeof Ionicons.glyphMap;
  variant?: 'default' | 'elevated' | 'outlined' | 'filled';
  size?: 'small' | 'medium' | 'large';
  onPress?: () => void;
  onLongPress?: () => void;
  style?: ViewStyle;
  contentStyle?: ViewStyle;
  titleStyle?: TextStyle;
  subtitleStyle?: TextStyle;
  contentStyle?: TextStyle;
  // Animation props
  enableHover?: boolean;
  enablePress?: boolean;
  enableLongPress?: boolean;
  enableSwipe?: boolean;
  animationDuration?: number;
  springConfig?: {
    damping?: number;
    stiffness?: number;
    mass?: number;
  };
  // Accessibility
  accessibilityLabel?: string;
  accessibilityHint?: string;
  accessibilityRole?: 'button' | 'link' | 'menuitem' | 'tab';
  // Content
  children?: React.ReactNode;
  footer?: React.ReactNode;
  header?: React.ReactNode;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const CARD_VARIANTS = {
  default: {
    backgroundColor: 'transparent',
    borderWidth: 0,
    shadowOpacity: 0,
  },
  elevated: {
    backgroundColor: 'transparent',
    borderWidth: 0,
    shadowOpacity: 0.1,
  },
  outlined: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    shadowOpacity: 0,
  },
  filled: {
    backgroundColor: 'transparent',
    borderWidth: 0,
    shadowOpacity: 0.05,
  },
};

const CARD_SIZES = {
  small: {
    padding: 12,
    borderRadius: 8,
    minHeight: 80,
  },
  medium: {
    padding: 16,
    borderRadius: 12,
    minHeight: 120,
  },
  large: {
    padding: 20,
    borderRadius: 16,
    minHeight: 160,
  },
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const AnimatedCard = React.memo<AnimatedCardProps>(({
  title,
  subtitle,
  content,
  icon,
  variant = 'default',
  size = 'medium',
  onPress,
  onLongPress,
  style,
  contentStyle,
  titleStyle,
  subtitleStyle,
  contentStyle: textContentStyle,
  enableHover = true,
  enablePress = true,
  enableLongPress = true,
  enableSwipe = false,
  animationDuration = 200,
  springConfig = { damping: 15, stiffness: 150, mass: 1 },
  accessibilityLabel,
  accessibilityHint,
  accessibilityRole = 'button',
  children,
  footer,
  header,
}) => {
  const colorScheme = useColorScheme();
  const { width } = useWindowDimensions();
  const isDark = colorScheme === 'dark';

  // ============================================================================
  // ANIMATED VALUES
  // ============================================================================

  const scale = useSharedValue(1);
  const translateY = useSharedValue(0);
  const translateX = useSharedValue(0);
  const rotation = useSharedValue(0);
  const opacity = useSharedValue(1);
  const shadowOpacity = useSharedValue(0);

  // ============================================================================
  // GESTURES
  // ============================================================================

  const tapGesture = Gesture.Tap()
    .onBegin(() => {
      if (enablePress) {
        scale.value = withSpring(0.95, springConfig);
        translateY.value = withSpring(2, springConfig);
        shadowOpacity.value = withTiming(0.2, { duration: animationDuration });
      }
    })
    .onFinalize(() => {
      if (enablePress) {
        scale.value = withSpring(1, springConfig);
        translateY.value = withSpring(0, springConfig);
        shadowOpacity.value = withTiming(0, { duration: animationDuration });
        if (onPress) {
          runOnJS(onPress)();
        }
      }
    });

  const longPressGesture = Gesture.LongPress()
    .minDuration(500)
    .onStart(() => {
      if (enableLongPress) {
        scale.value = withSequence(
          withSpring(0.9, springConfig),
          withSpring(1.05, springConfig),
          withSpring(1, springConfig)
        );
        rotation.value = withSequence(
          withTiming(-5, { duration: 100 }),
          withTiming(5, { duration: 100 }),
          withTiming(0, { duration: 100 })
        );
        if (onLongPress) {
          runOnJS(onLongPress)();
        }
      }
    });

  const panGesture = Gesture.Pan()
    .enabled(enableSwipe)
    .onUpdate((event) => {
      if (enableSwipe) {
        translateX.value = event.translationX;
        translateY.value = event.translationY;
        rotation.value = interpolate(
          event.translationX,
          [-width / 2, 0, width / 2],
          [-15, 0, 15],
          Extrapolate.CLAMP
        );
      }
    })
    .onEnd((event) => {
      if (enableSwipe) {
        const shouldDismiss = Math.abs(event.translationX) > width / 3;
        
        if (shouldDismiss) {
          translateX.value = withTiming(
            event.translationX > 0 ? width : -width,
            { duration: animationDuration }
          );
          opacity.value = withTiming(0, { duration: animationDuration });
        } else {
          translateX.value = withSpring(0, springConfig);
          translateY.value = withSpring(0, springConfig);
          rotation.value = withSpring(0, springConfig);
        }
      }
    });

  const composedGesture = Gesture.Simultaneous(
    tapGesture,
    longPressGesture,
    panGesture
  );

  // ============================================================================
  // ANIMATED STYLES
  // ============================================================================

  const animatedCardStyle = useAnimatedStyle(() => {
    const variantStyle = CARD_VARIANTS[variant];
    const sizeStyle = CARD_SIZES[size];
    
    return {
      transform: [
        { scale: scale.value },
        { translateY: translateY.value },
        { translateX: translateX.value },
        { rotate: `${rotation.value}deg` },
      ],
      opacity: opacity.value,
      shadowOpacity: shadowOpacity.value,
    };
  });

  const animatedContentStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
  }));

  // ============================================================================
  // MEMOIZED STYLES
  // ============================================================================

  const cardStyle = useMemo(() => {
    const variantStyle = CARD_VARIANTS[variant];
    const sizeStyle = CARD_SIZES[size];
    
    return [
      styles.card,
      {
        backgroundColor: isDark ? '#1C1C1E' : '#FFFFFF',
        borderColor: isDark ? '#3A3A3C' : '#E5E5EA',
        ...variantStyle,
        ...sizeStyle,
      },
      style,
    ];
  }, [variant, size, isDark, style]);

  const textStyles = useMemo(() => ({
    title: [
      styles.title,
      {
        color: isDark ? '#FFFFFF' : '#000000',
        fontSize: size === 'small' ? 16 : size === 'medium' ? 18 : 20,
      },
      titleStyle,
    ],
    subtitle: [
      styles.subtitle,
      {
        color: isDark ? '#8E8E93' : '#6C6C70',
        fontSize: size === 'small' ? 12 : size === 'medium' ? 14 : 16,
      },
      subtitleStyle,
    ],
    content: [
      styles.content,
      {
        color: isDark ? '#8E8E93' : '#6C6C70',
        fontSize: size === 'small' ? 12 : size === 'medium' ? 14 : 16,
      },
      textContentStyle,
    ],
  }), [size, isDark, titleStyle, subtitleStyle, textContentStyle]);

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <GestureDetector gesture={composedGesture}>
      <Animated.View style={[cardStyle, animatedCardStyle]}>
        {/* Header */}
        {header && (
          <Animated.View style={[styles.header, animatedContentStyle]}>
            {header}
          </Animated.View>
        )}

        {/* Content */}
        <Animated.View style={[styles.contentContainer, contentStyle, animatedContentStyle]}>
          {/* Icon */}
          {icon && (
            <View style={styles.iconContainer}>
              <Ionicons
                name={icon}
                size={size === 'small' ? 20 : size === 'medium' ? 24 : 28}
                color={isDark ? '#007AFF' : '#007AFF'}
              />
            </View>
          )}

          {/* Text Content */}
          <View style={styles.textContainer}>
            <Text style={textStyles.title} numberOfLines={2}>
              {title}
            </Text>
            
            {subtitle && (
              <Text style={textStyles.subtitle} numberOfLines={1}>
                {subtitle}
              </Text>
            )}
            
            {content && (
              <Text style={textStyles.content} numberOfLines={3}>
                {content}
              </Text>
            )}
          </View>

          {/* Children */}
          {children && (
            <View style={styles.childrenContainer}>
              {children}
            </View>
          )}
        </Animated.View>

        {/* Footer */}
        {footer && (
          <Animated.View style={[styles.footer, animatedContentStyle]}>
            {footer}
          </Animated.View>
        )}
      </Animated.View>
    </GestureDetector>
  );
});

AnimatedCard.displayName = 'AnimatedCard';

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  card: {
    shadowColor: '#000000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowRadius: 4,
    elevation: 2,
  },
  header: {
    marginBottom: 12,
  },
  contentContainer: {
    flex: 1,
  },
  iconContainer: {
    marginBottom: 8,
  },
  textContainer: {
    flex: 1,
  },
  title: {
    fontWeight: '600',
    marginBottom: 4,
  },
  subtitle: {
    fontWeight: '500',
    marginBottom: 8,
  },
  content: {
    lineHeight: 20,
  },
  childrenContainer: {
    marginTop: 12,
  },
  footer: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0, 0, 0, 0.1)',
  },
});

// ============================================================================
// SPECIALIZED COMPONENTS
// ============================================================================

export const ElevatedCard = React.memo<Omit<AnimatedCardProps, 'variant'>>((props) => (
  <AnimatedCard {...props} variant="elevated" />
));

export const OutlinedCard = React.memo<Omit<AnimatedCardProps, 'variant'>>((props) => (
  <AnimatedCard {...props} variant="outlined" />
));

export const FilledCard = React.memo<Omit<AnimatedCardProps, 'variant'>>((props) => (
  <AnimatedCard {...props} variant="filled" />
));

export const SmallCard = React.memo<Omit<AnimatedCardProps, 'size'>>((props) => (
  <AnimatedCard {...props} size="small" />
));

export const LargeCard = React.memo<Omit<AnimatedCardProps, 'size'>>((props) => (
  <AnimatedCard {...props} size="large" />
));
import {
  View,
  Text,
  StyleSheet,
  ViewStyle,
  TextStyle,
  TouchableOpacity,
  useWindowDimensions,
} from 'react-native';
import { useColorScheme } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  withSequence,
  withDelay,
  runOnJS,
  interpolate,
  Extrapolate,
} from 'react-native-reanimated';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import { Ionicons } from '@expo/vector-icons';

// ============================================================================
// TYPES
// ============================================================================

interface AnimatedCardProps {
  title: string;
  subtitle?: string;
  content?: string;
  icon?: keyof typeof Ionicons.glyphMap;
  variant?: 'default' | 'elevated' | 'outlined' | 'filled';
  size?: 'small' | 'medium' | 'large';
  onPress?: () => void;
  onLongPress?: () => void;
  style?: ViewStyle;
  contentStyle?: ViewStyle;
  titleStyle?: TextStyle;
  subtitleStyle?: TextStyle;
  contentStyle?: TextStyle;
  // Animation props
  enableHover?: boolean;
  enablePress?: boolean;
  enableLongPress?: boolean;
  enableSwipe?: boolean;
  animationDuration?: number;
  springConfig?: {
    damping?: number;
    stiffness?: number;
    mass?: number;
  };
  // Accessibility
  accessibilityLabel?: string;
  accessibilityHint?: string;
  accessibilityRole?: 'button' | 'link' | 'menuitem' | 'tab';
  // Content
  children?: React.ReactNode;
  footer?: React.ReactNode;
  header?: React.ReactNode;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const CARD_VARIANTS = {
  default: {
    backgroundColor: 'transparent',
    borderWidth: 0,
    shadowOpacity: 0,
  },
  elevated: {
    backgroundColor: 'transparent',
    borderWidth: 0,
    shadowOpacity: 0.1,
  },
  outlined: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    shadowOpacity: 0,
  },
  filled: {
    backgroundColor: 'transparent',
    borderWidth: 0,
    shadowOpacity: 0.05,
  },
};

const CARD_SIZES = {
  small: {
    padding: 12,
    borderRadius: 8,
    minHeight: 80,
  },
  medium: {
    padding: 16,
    borderRadius: 12,
    minHeight: 120,
  },
  large: {
    padding: 20,
    borderRadius: 16,
    minHeight: 160,
  },
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const AnimatedCard = React.memo<AnimatedCardProps>(({
  title,
  subtitle,
  content,
  icon,
  variant = 'default',
  size = 'medium',
  onPress,
  onLongPress,
  style,
  contentStyle,
  titleStyle,
  subtitleStyle,
  contentStyle: textContentStyle,
  enableHover = true,
  enablePress = true,
  enableLongPress = true,
  enableSwipe = false,
  animationDuration = 200,
  springConfig = { damping: 15, stiffness: 150, mass: 1 },
  accessibilityLabel,
  accessibilityHint,
  accessibilityRole = 'button',
  children,
  footer,
  header,
}) => {
  const colorScheme = useColorScheme();
  const { width } = useWindowDimensions();
  const isDark = colorScheme === 'dark';

  // ============================================================================
  // ANIMATED VALUES
  // ============================================================================

  const scale = useSharedValue(1);
  const translateY = useSharedValue(0);
  const translateX = useSharedValue(0);
  const rotation = useSharedValue(0);
  const opacity = useSharedValue(1);
  const shadowOpacity = useSharedValue(0);

  // ============================================================================
  // GESTURES
  // ============================================================================

  const tapGesture = Gesture.Tap()
    .onBegin(() => {
      if (enablePress) {
        scale.value = withSpring(0.95, springConfig);
        translateY.value = withSpring(2, springConfig);
        shadowOpacity.value = withTiming(0.2, { duration: animationDuration });
      }
    })
    .onFinalize(() => {
      if (enablePress) {
        scale.value = withSpring(1, springConfig);
        translateY.value = withSpring(0, springConfig);
        shadowOpacity.value = withTiming(0, { duration: animationDuration });
        if (onPress) {
          runOnJS(onPress)();
        }
      }
    });

  const longPressGesture = Gesture.LongPress()
    .minDuration(500)
    .onStart(() => {
      if (enableLongPress) {
        scale.value = withSequence(
          withSpring(0.9, springConfig),
          withSpring(1.05, springConfig),
          withSpring(1, springConfig)
        );
        rotation.value = withSequence(
          withTiming(-5, { duration: 100 }),
          withTiming(5, { duration: 100 }),
          withTiming(0, { duration: 100 })
        );
        if (onLongPress) {
          runOnJS(onLongPress)();
        }
      }
    });

  const panGesture = Gesture.Pan()
    .enabled(enableSwipe)
    .onUpdate((event) => {
      if (enableSwipe) {
        translateX.value = event.translationX;
        translateY.value = event.translationY;
        rotation.value = interpolate(
          event.translationX,
          [-width / 2, 0, width / 2],
          [-15, 0, 15],
          Extrapolate.CLAMP
        );
      }
    })
    .onEnd((event) => {
      if (enableSwipe) {
        const shouldDismiss = Math.abs(event.translationX) > width / 3;
        
        if (shouldDismiss) {
          translateX.value = withTiming(
            event.translationX > 0 ? width : -width,
            { duration: animationDuration }
          );
          opacity.value = withTiming(0, { duration: animationDuration });
        } else {
          translateX.value = withSpring(0, springConfig);
          translateY.value = withSpring(0, springConfig);
          rotation.value = withSpring(0, springConfig);
        }
      }
    });

  const composedGesture = Gesture.Simultaneous(
    tapGesture,
    longPressGesture,
    panGesture
  );

  // ============================================================================
  // ANIMATED STYLES
  // ============================================================================

  const animatedCardStyle = useAnimatedStyle(() => {
    const variantStyle = CARD_VARIANTS[variant];
    const sizeStyle = CARD_SIZES[size];
    
    return {
      transform: [
        { scale: scale.value },
        { translateY: translateY.value },
        { translateX: translateX.value },
        { rotate: `${rotation.value}deg` },
      ],
      opacity: opacity.value,
      shadowOpacity: shadowOpacity.value,
    };
  });

  const animatedContentStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
  }));

  // ============================================================================
  // MEMOIZED STYLES
  // ============================================================================

  const cardStyle = useMemo(() => {
    const variantStyle = CARD_VARIANTS[variant];
    const sizeStyle = CARD_SIZES[size];
    
    return [
      styles.card,
      {
        backgroundColor: isDark ? '#1C1C1E' : '#FFFFFF',
        borderColor: isDark ? '#3A3A3C' : '#E5E5EA',
        ...variantStyle,
        ...sizeStyle,
      },
      style,
    ];
  }, [variant, size, isDark, style]);

  const textStyles = useMemo(() => ({
    title: [
      styles.title,
      {
        color: isDark ? '#FFFFFF' : '#000000',
        fontSize: size === 'small' ? 16 : size === 'medium' ? 18 : 20,
      },
      titleStyle,
    ],
    subtitle: [
      styles.subtitle,
      {
        color: isDark ? '#8E8E93' : '#6C6C70',
        fontSize: size === 'small' ? 12 : size === 'medium' ? 14 : 16,
      },
      subtitleStyle,
    ],
    content: [
      styles.content,
      {
        color: isDark ? '#8E8E93' : '#6C6C70',
        fontSize: size === 'small' ? 12 : size === 'medium' ? 14 : 16,
      },
      textContentStyle,
    ],
  }), [size, isDark, titleStyle, subtitleStyle, textContentStyle]);

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <GestureDetector gesture={composedGesture}>
      <Animated.View style={[cardStyle, animatedCardStyle]}>
        {/* Header */}
        {header && (
          <Animated.View style={[styles.header, animatedContentStyle]}>
            {header}
          </Animated.View>
        )}

        {/* Content */}
        <Animated.View style={[styles.contentContainer, contentStyle, animatedContentStyle]}>
          {/* Icon */}
          {icon && (
            <View style={styles.iconContainer}>
              <Ionicons
                name={icon}
                size={size === 'small' ? 20 : size === 'medium' ? 24 : 28}
                color={isDark ? '#007AFF' : '#007AFF'}
              />
            </View>
          )}

          {/* Text Content */}
          <View style={styles.textContainer}>
            <Text style={textStyles.title} numberOfLines={2}>
              {title}
            </Text>
            
            {subtitle && (
              <Text style={textStyles.subtitle} numberOfLines={1}>
                {subtitle}
              </Text>
            )}
            
            {content && (
              <Text style={textStyles.content} numberOfLines={3}>
                {content}
              </Text>
            )}
          </View>

          {/* Children */}
          {children && (
            <View style={styles.childrenContainer}>
              {children}
            </View>
          )}
        </Animated.View>

        {/* Footer */}
        {footer && (
          <Animated.View style={[styles.footer, animatedContentStyle]}>
            {footer}
          </Animated.View>
        )}
      </Animated.View>
    </GestureDetector>
  );
});

AnimatedCard.displayName = 'AnimatedCard';

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  card: {
    shadowColor: '#000000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowRadius: 4,
    elevation: 2,
  },
  header: {
    marginBottom: 12,
  },
  contentContainer: {
    flex: 1,
  },
  iconContainer: {
    marginBottom: 8,
  },
  textContainer: {
    flex: 1,
  },
  title: {
    fontWeight: '600',
    marginBottom: 4,
  },
  subtitle: {
    fontWeight: '500',
    marginBottom: 8,
  },
  content: {
    lineHeight: 20,
  },
  childrenContainer: {
    marginTop: 12,
  },
  footer: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0, 0, 0, 0.1)',
  },
});

// ============================================================================
// SPECIALIZED COMPONENTS
// ============================================================================

export const ElevatedCard = React.memo<Omit<AnimatedCardProps, 'variant'>>((props) => (
  <AnimatedCard {...props} variant="elevated" />
));

export const OutlinedCard = React.memo<Omit<AnimatedCardProps, 'variant'>>((props) => (
  <AnimatedCard {...props} variant="outlined" />
));

export const FilledCard = React.memo<Omit<AnimatedCardProps, 'variant'>>((props) => (
  <AnimatedCard {...props} variant="filled" />
));

export const SmallCard = React.memo<Omit<AnimatedCardProps, 'size'>>((props) => (
  <AnimatedCard {...props} size="small" />
));

export const LargeCard = React.memo<Omit<AnimatedCardProps, 'size'>>((props) => (
  <AnimatedCard {...props} size="large" />
));


