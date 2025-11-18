import React, { useMemo, useCallback, memo, forwardRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ViewStyle,
  TextStyle,
  Animated,
  PanGestureHandler,
  State,
  GestureHandlerRootView,
} from 'react-native';
import { useWindowDimensions } from 'react-native';
import { useColorScheme } from 'react-native';

// ============================================================================
// TYPES
// ============================================================================

interface OptimizedCardProps {
  title?: string;
  subtitle?: string;
  content?: React.ReactNode;
  children?: React.ReactNode;
  onPress?: () => void;
  onLongPress?: () => void;
  variant?: 'elevated' | 'outlined' | 'filled' | 'glass';
  size?: 'small' | 'medium' | 'large';
  isPressable?: boolean;
  isDisabled?: boolean;
  hasShadow?: boolean;
  hasBorder?: boolean;
  isFullWidth?: boolean;
  containerStyle?: ViewStyle;
  contentStyle?: ViewStyle;
  titleStyle?: TextStyle;
  subtitleStyle?: TextStyle;
  testID?: string;
  accessibilityLabel?: string;
  accessibilityHint?: string;
  elevation?: number;
  borderRadius?: number;
  backgroundColor?: string;
  borderColor?: string;
}

interface CardRef {
  animate: (animation: 'pulse' | 'shake' | 'bounce') => void;
  setElevation: (elevation: number) => void;
}

// ============================================================================
// STATIC CONTENT
// ============================================================================

const CARD_VARIANTS = {
  elevated: {
    shadowOpacity: 0.1,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 4 },
    elevation: 4,
    backgroundColor: 'transparent',
    borderWidth: 0,
  },
  outlined: {
    shadowOpacity: 0,
    shadowRadius: 0,
    shadowOffset: { width: 0, height: 0 },
    elevation: 0,
    backgroundColor: 'transparent',
    borderWidth: 1,
  },
  filled: {
    shadowOpacity: 0.05,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
    backgroundColor: '#F8F9FA',
    borderWidth: 0,
  },
  glass: {
    shadowOpacity: 0.15,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 6 },
    elevation: 6,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
} as const;

const CARD_SIZES = {
  small: {
    padding: 12,
    borderRadius: 8,
    titleFontSize: 16,
    subtitleFontSize: 14,
  },
  medium: {
    padding: 16,
    borderRadius: 12,
    titleFontSize: 18,
    subtitleFontSize: 16,
  },
  large: {
    padding: 20,
    borderRadius: 16,
    titleFontSize: 20,
    subtitleFontSize: 18,
  },
} as const;

// ============================================================================
// HELPERS
// ============================================================================

const getCardStyle = (
  props: OptimizedCardProps,
  isDark: boolean,
  width: number,
  customElevation?: number
): ViewStyle => {
  const { variant = 'elevated', size = 'medium', hasShadow, hasBorder, isFullWidth, elevation, borderRadius, backgroundColor, borderColor } = props;
  const variantStyle = CARD_VARIANTS[variant];
  const sizeStyle = CARD_SIZES[size];

  // Responsive adjustments
  const responsivePadding = width < 375 ? sizeStyle.padding * 0.8 : sizeStyle.padding;
  const responsiveBorderRadius = width < 375 ? sizeStyle.borderRadius * 0.8 : sizeStyle.borderRadius;

  const baseBackgroundColor = backgroundColor || (isDark ? '#2C2C2E' : '#FFFFFF');
  const baseBorderColor = borderColor || (isDark ? '#3A3A3C' : '#E5E5EA');

  return {
    padding: responsivePadding,
    borderRadius: borderRadius || responsiveBorderRadius,
    backgroundColor: variant === 'glass' ? variantStyle.backgroundColor : (backgroundColor || baseBackgroundColor),
    borderWidth: hasBorder ? 1 : variantStyle.borderWidth,
    borderColor: borderColor || baseBorderColor,
    width: isFullWidth ? '100%' : 'auto',
    shadowColor: isDark ? '#000000' : '#000000',
    shadowOffset: variantStyle.shadowOffset,
    shadowOpacity: hasShadow ? variantStyle.shadowOpacity : 0,
    shadowRadius: variantStyle.shadowRadius,
    elevation: customElevation || (hasShadow ? variantStyle.elevation : 0),
  };
};

const getTitleStyle = (props: OptimizedCardProps, isDark: boolean, width: number): TextStyle => {
  const { size = 'medium' } = props;
  const sizeStyle = CARD_SIZES[size];
  
  // Responsive font size
  const responsiveFontSize = width < 375 ? sizeStyle.titleFontSize * 0.9 : sizeStyle.titleFontSize;
  
  return {
    fontSize: responsiveFontSize,
    fontWeight: '600' as const,
    color: isDark ? '#FFFFFF' : '#000000',
    marginBottom: 4,
    includeFontPadding: false,
  };
};

const getSubtitleStyle = (props: OptimizedCardProps, isDark: boolean, width: number): TextStyle => {
  const { size = 'medium' } = props;
  const sizeStyle = CARD_SIZES[size];
  
  // Responsive font size
  const responsiveFontSize = width < 375 ? sizeStyle.subtitleFontSize * 0.9 : sizeStyle.subtitleFontSize;
  
  return {
    fontSize: responsiveFontSize,
    fontWeight: '400' as const,
    color: isDark ? '#8E8E93' : '#6C6C70',
    marginBottom: 12,
    includeFontPadding: false,
  };
};

// ============================================================================
// ANIMATION HELPERS
// ============================================================================

const createPulseAnimation = (value: Animated.Value) => {
  return Animated.sequence([
    Animated.timing(value, {
      toValue: 1.05,
      duration: 150,
      useNativeDriver: true,
    }),
    Animated.timing(value, {
      toValue: 1,
      duration: 150,
      useNativeDriver: true,
    }),
  ]);
};

const createShakeAnimation = (value: Animated.Value) => {
  return Animated.sequence([
    Animated.timing(value, {
      toValue: -5,
      duration: 50,
      useNativeDriver: true,
    }),
    Animated.timing(value, {
      toValue: 5,
      duration: 50,
      useNativeDriver: true,
    }),
    Animated.timing(value, {
      toValue: -5,
      duration: 50,
      useNativeDriver: true,
    }),
    Animated.timing(value, {
      toValue: 0,
      duration: 50,
      useNativeDriver: true,
    }),
  ]);
};

const createBounceAnimation = (value: Animated.Value) => {
  return Animated.sequence([
    Animated.timing(value, {
      toValue: 1.1,
      duration: 200,
      useNativeDriver: true,
    }),
    Animated.timing(value, {
      toValue: 0.9,
      duration: 200,
      useNativeDriver: true,
    }),
    Animated.timing(value, {
      toValue: 1,
      duration: 200,
      useNativeDriver: true,
    }),
  ]);
};

// ============================================================================
// MAIN EXPORTED COMPONENT
// ============================================================================

export const OptimizedCard = memo(forwardRef<CardRef, OptimizedCardProps>(({
  title,
  subtitle,
  content,
  children,
  onPress,
  onLongPress,
  variant = 'elevated',
  size = 'medium',
  isPressable = false,
  isDisabled = false,
  hasShadow = true,
  hasBorder = false,
  isFullWidth = false,
  containerStyle,
  contentStyle,
  titleStyle,
  subtitleStyle,
  testID,
  accessibilityLabel,
  accessibilityHint,
  elevation,
  borderRadius,
  backgroundColor,
  borderColor,
}, ref) => {
  const colorScheme = useColorScheme();
  const { width } = useWindowDimensions();
  const isDark = colorScheme === 'dark';

  // Animation values
  const scaleValue = React.useRef(new Animated.Value(1)).current;
  const translateXValue = React.useRef(new Animated.Value(0)).current;
  const currentElevation = React.useRef(elevation || 0);

  // Memoized styles for performance
  const cardStyle = useMemo(() => 
    getCardStyle({ variant, size, hasShadow, hasBorder, isFullWidth, elevation, borderRadius, backgroundColor, borderColor }, isDark, width, currentElevation.current), 
    [variant, size, hasShadow, hasBorder, isFullWidth, elevation, borderRadius, backgroundColor, borderColor, isDark, width]
  );

  const titleStyleMemo = useMemo(() => 
    getTitleStyle({ size }, isDark, width), 
    [size, isDark, width]
  );

  const subtitleStyleMemo = useMemo(() => 
    getSubtitleStyle({ size }, isDark, width), 
    [size, isDark, width]
  );

  // Animation functions
  const animate = useCallback((animation: 'pulse' | 'shake' | 'bounce') => {
    switch (animation) {
      case 'pulse':
        createPulseAnimation(scaleValue).start();
        break;
      case 'shake':
        createShakeAnimation(translateXValue).start();
        break;
      case 'bounce':
        createBounceAnimation(scaleValue).start();
        break;
    }
  }, [scaleValue, translateXValue]);

  const setElevation = useCallback((newElevation: number) => {
    currentElevation.current = newElevation;
    // Force re-render by updating state or using a ref
  }, []);

  // Expose methods via ref
  React.useImperativeHandle(ref, () => ({
    animate,
    setElevation,
  }), [animate, setElevation]);

  // Memoized accessibility props
  const accessibilityProps = useMemo(() => ({
    accessible: true,
    accessibilityLabel: accessibilityLabel || `${title || 'Card'} ${subtitle || ''}`.trim(),
    accessibilityHint: accessibilityHint || (isPressable ? 'Double tap to activate' : 'Card information'),
    accessibilityRole: isPressable ? 'button' as const : 'none' as const,
    accessibilityState: { 
      disabled: isDisabled,
      busy: false 
    },
  }), [accessibilityLabel, accessibilityHint, title, subtitle, isPressable, isDisabled]);

  // Memoized press handlers
  const handlePress = useCallback(() => {
    if (onPress && !isDisabled) {
      animate('pulse');
      onPress();
    }
  }, [onPress, isDisabled, animate]);

  const handleLongPress = useCallback(() => {
    if (onLongPress && !isDisabled) {
      animate('shake');
      onLongPress();
    }
  }, [onLongPress, isDisabled, animate]);

  // Memoized card content
  const CardContent = useMemo(() => (
    <>
      {title && (
        <Text style={[titleStyleMemo, titleStyle]} numberOfLines={2}>
          {title}
        </Text>
      )}
      {subtitle && (
        <Text style={[subtitleStyleMemo, subtitleStyle]} numberOfLines={3}>
          {subtitle}
        </Text>
      )}
      {content && (
        <View style={[styles.content, contentStyle]}>
          {content}
        </View>
      )}
      {children}
    </>
  ), [title, subtitle, content, children, titleStyleMemo, titleStyle, subtitleStyleMemo, subtitleStyle, contentStyle]);

  // Render card with or without press functionality
  if (isPressable) {
    return (
      <GestureHandlerRootView>
        <TouchableOpacity
          style={[
            styles.card,
            cardStyle,
            containerStyle,
          ]}
          onPress={handlePress}
          onLongPress={handleLongPress}
          disabled={isDisabled}
          activeOpacity={0.8}
          testID={testID}
          {...accessibilityProps}
        >
          <Animated.View
            style={[
              styles.animatedContainer,
              {
                transform: [
                  { scale: scaleValue },
                  { translateX: translateXValue },
                ],
              },
            ]}
          >
            {CardContent}
          </Animated.View>
        </TouchableOpacity>
      </GestureHandlerRootView>
    );
  }

  return (
    <View
      style={[
        styles.card,
        cardStyle,
        containerStyle,
      ]}
      testID={testID}
      {...accessibilityProps}
    >
      <Animated.View
        style={[
          styles.animatedContainer,
          {
            transform: [
              { scale: scaleValue },
              { translateX: translateXValue },
            ],
          },
        ]}
      >
        {CardContent}
      </Animated.View>
    </View>
  );
}));

OptimizedCard.displayName = 'OptimizedCard';

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  card: {
    margin: 8,
  },
  animatedContainer: {
    flex: 1,
  },
  content: {
    marginTop: 8,
  },
}); 
      toValue: 0,
      duration: 50,
      useNativeDriver: true,
    }),
  ]);
};

const createBounceAnimation = (value: Animated.Value) => {
  return Animated.sequence([
    Animated.timing(value, {
      toValue: 1.1,
      duration: 200,
      useNativeDriver: true,
    }),
    Animated.timing(value, {
      toValue: 0.9,
      duration: 200,
      useNativeDriver: true,
    }),
    Animated.timing(value, {
      toValue: 1,
      duration: 200,
      useNativeDriver: true,
    }),
  ]);
};

// ============================================================================
// MAIN EXPORTED COMPONENT
// ============================================================================

export const OptimizedCard = memo(forwardRef<CardRef, OptimizedCardProps>(({
  title,
  subtitle,
  content,
  children,
  onPress,
  onLongPress,
  variant = 'elevated',
  size = 'medium',
  isPressable = false,
  isDisabled = false,
  hasShadow = true,
  hasBorder = false,
  isFullWidth = false,
  containerStyle,
  contentStyle,
  titleStyle,
  subtitleStyle,
  testID,
  accessibilityLabel,
  accessibilityHint,
  elevation,
  borderRadius,
  backgroundColor,
  borderColor,
}, ref) => {
  const colorScheme = useColorScheme();
  const { width } = useWindowDimensions();
  const isDark = colorScheme === 'dark';

  // Animation values
  const scaleValue = React.useRef(new Animated.Value(1)).current;
  const translateXValue = React.useRef(new Animated.Value(0)).current;
  const currentElevation = React.useRef(elevation || 0);

  // Memoized styles for performance
  const cardStyle = useMemo(() => 
    getCardStyle({ variant, size, hasShadow, hasBorder, isFullWidth, elevation, borderRadius, backgroundColor, borderColor }, isDark, width, currentElevation.current), 
    [variant, size, hasShadow, hasBorder, isFullWidth, elevation, borderRadius, backgroundColor, borderColor, isDark, width]
  );

  const titleStyleMemo = useMemo(() => 
    getTitleStyle({ size }, isDark, width), 
    [size, isDark, width]
  );

  const subtitleStyleMemo = useMemo(() => 
    getSubtitleStyle({ size }, isDark, width), 
    [size, isDark, width]
  );

  // Animation functions
  const animate = useCallback((animation: 'pulse' | 'shake' | 'bounce') => {
    switch (animation) {
      case 'pulse':
        createPulseAnimation(scaleValue).start();
        break;
      case 'shake':
        createShakeAnimation(translateXValue).start();
        break;
      case 'bounce':
        createBounceAnimation(scaleValue).start();
        break;
    }
  }, [scaleValue, translateXValue]);

  const setElevation = useCallback((newElevation: number) => {
    currentElevation.current = newElevation;
    // Force re-render by updating state or using a ref
  }, []);

  // Expose methods via ref
  React.useImperativeHandle(ref, () => ({
    animate,
    setElevation,
  }), [animate, setElevation]);

  // Memoized accessibility props
  const accessibilityProps = useMemo(() => ({
    accessible: true,
    accessibilityLabel: accessibilityLabel || `${title || 'Card'} ${subtitle || ''}`.trim(),
    accessibilityHint: accessibilityHint || (isPressable ? 'Double tap to activate' : 'Card information'),
    accessibilityRole: isPressable ? 'button' as const : 'none' as const,
    accessibilityState: { 
      disabled: isDisabled,
      busy: false 
    },
  }), [accessibilityLabel, accessibilityHint, title, subtitle, isPressable, isDisabled]);

  // Memoized press handlers
  const handlePress = useCallback(() => {
    if (onPress && !isDisabled) {
      animate('pulse');
      onPress();
    }
  }, [onPress, isDisabled, animate]);

  const handleLongPress = useCallback(() => {
    if (onLongPress && !isDisabled) {
      animate('shake');
      onLongPress();
    }
  }, [onLongPress, isDisabled, animate]);

  // Memoized card content
  const CardContent = useMemo(() => (
    <>
      {title && (
        <Text style={[titleStyleMemo, titleStyle]} numberOfLines={2}>
          {title}
        </Text>
      )}
      {subtitle && (
        <Text style={[subtitleStyleMemo, subtitleStyle]} numberOfLines={3}>
          {subtitle}
        </Text>
      )}
      {content && (
        <View style={[styles.content, contentStyle]}>
          {content}
        </View>
      )}
      {children}
    </>
  ), [title, subtitle, content, children, titleStyleMemo, titleStyle, subtitleStyleMemo, subtitleStyle, contentStyle]);

  // Render card with or without press functionality
  if (isPressable) {
    return (
      <GestureHandlerRootView>
        <TouchableOpacity
          style={[
            styles.card,
            cardStyle,
            containerStyle,
          ]}
          onPress={handlePress}
          onLongPress={handleLongPress}
          disabled={isDisabled}
          activeOpacity={0.8}
          testID={testID}
          {...accessibilityProps}
        >
          <Animated.View
            style={[
              styles.animatedContainer,
              {
                transform: [
                  { scale: scaleValue },
                  { translateX: translateXValue },
                ],
              },
            ]}
          >
            {CardContent}
          </Animated.View>
        </TouchableOpacity>
      </GestureHandlerRootView>
    );
  }

  return (
    <View
      style={[
        styles.card,
        cardStyle,
        containerStyle,
      ]}
      testID={testID}
      {...accessibilityProps}
    >
      <Animated.View
        style={[
          styles.animatedContainer,
          {
            transform: [
              { scale: scaleValue },
              { translateX: translateXValue },
            ],
          },
        ]}
      >
        {CardContent}
      </Animated.View>
    </View>
  );
}));

OptimizedCard.displayName = 'OptimizedCard';

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  card: {
    margin: 8,
  },
  animatedContainer: {
    flex: 1,
  },
  content: {
    marginTop: 8,
  },
}); 