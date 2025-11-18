import React, { useCallback, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  Image,
  TouchableOpacity,
} from 'react-native';
import {
  PanGestureHandler,
  PinchGestureHandler,
  RotationGestureHandler,
  State,
} from 'react-native-gesture-handler';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
  runOnJS,
} from 'react-native-reanimated';
import { usePanGestureAnimation, usePinchGestureAnimation, useRotationGestureAnimation } from '../../lib/animations/advanced-animations';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

interface GestureCardProps {
  id: string;
  title: string;
  description: string;
  imageUrl?: string;
  onDismiss?: (id: string) => void;
  onPress?: (id: string) => void;
  onLongPress?: (id: string) => void;
  testID?: string;
}

export function GestureCard({
  id,
  title,
  description,
  imageUrl,
  onDismiss,
  onPress,
  onLongPress,
  testID,
}: GestureCardProps) {
  const { theme } = useAppStore();
  const { t } = useI18n();
  const [isPressed, setIsPressed] = useState(false);
  const [isLongPressed, setIsLongPressed] = useState(false);

  // Gesture animations
  const { panGestureHandler, animatedStyle: panStyle } = usePanGestureAnimation(
    useCallback((translation) => {
      if (Math.abs(translation.x) > screenWidth * 0.3) {
        onDismiss?.(id);
      }
    }, [id, onDismiss])
  );

  const { pinchGestureHandler, animatedStyle: pinchStyle } = usePinchGestureAnimation();
  const { rotationGestureHandler, animatedStyle: rotationStyle } = useRotationGestureAnimation();

  // Press animations
  const pressScale = useSharedValue(1);
  const pressOpacity = useSharedValue(1);

  const handlePressIn = useCallback(() => {
    setIsPressed(true);
    pressScale.value = withSpring(0.95, { damping: 15, stiffness: 300 });
    pressOpacity.value = withTiming(0.8, { duration: 100 });
  }, [pressScale, pressOpacity]);

  const handlePressOut = useCallback(() => {
    setIsPressed(false);
    pressScale.value = withSpring(1, { damping: 15, stiffness: 300 });
    pressOpacity.value = withTiming(1, { duration: 100 });
  }, [pressScale, pressOpacity]);

  const handlePress = useCallback(() => {
    onPress?.(id);
  }, [id, onPress]);

  const handleLongPress = useCallback(() => {
    setIsLongPressed(true);
    onLongPress?.(id);
    
    // Reset long press state after animation
    setTimeout(() => {
      setIsLongPressed(false);
    }, 300);
  }, [id, onLongPress]);

  const pressAnimatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: pressScale.value }],
    opacity: pressOpacity.value,
  }));

  const combinedAnimatedStyle = useAnimatedStyle(() => ({
    ...panStyle.value,
    ...pinchStyle.value,
    ...rotationStyle.value,
    ...pressAnimatedStyle.value,
  }));

  const cardStyle = [
    styles.card,
    {
      backgroundColor: theme.colors.surface,
      borderColor: theme.colors.border,
      shadowColor: theme.colors.shadow,
    },
    isPressed && styles.pressed,
    isLongPressed && styles.longPressed,
  ];

  return (
    <PanGestureHandler
      onGestureEvent={panGestureHandler}
      onHandlerStateChange={(event) => {
        if (event.nativeEvent.state === State.END) {
          runOnJS(handlePressOut)();
        }
      }}
    >
      <Animated.View style={[combinedAnimatedStyle]}>
        <PinchGestureHandler onGestureEvent={pinchGestureHandler}>
          <Animated.View>
            <RotationGestureHandler onGestureEvent={rotationGestureHandler}>
              <Animated.View>
                <TouchableOpacity
                  testID={testID}
                  onPressIn={handlePressIn}
                  onPressOut={handlePressOut}
                  onPress={handlePress}
                  onLongPress={handleLongPress}
                  delayLongPress={500}
                  activeOpacity={1}
                  style={cardStyle}
                >
                  {imageUrl && (
                    <Image
                      source={{ uri: imageUrl }}
                      style={styles.image}
                      resizeMode="cover"
                    />
                  )}
                  
                  <View style={styles.content}>
                    <Text
                      style={[styles.title, { color: theme.colors.text }]}
                      numberOfLines={2}
                    >
                      {title}
                    </Text>
                    
                    <Text
                      style={[styles.description, { color: theme.colors.textSecondary }]}
                      numberOfLines={3}
                    >
                      {description}
                    </Text>
                  </View>

                  {/* Gesture indicators */}
                  <View style={styles.gestureIndicators}>
                    <View style={[styles.indicator, { backgroundColor: theme.colors.primary }]}>
                      <Text style={[styles.indicatorText, { color: 'white' }]}>
                        {t('gestures.swipe')}
                      </Text>
                    </View>
                    
                    <View style={[styles.indicator, { backgroundColor: theme.colors.secondary }]}>
                      <Text style={[styles.indicatorText, { color: 'white' }]}>
                        {t('gestures.pinch')}
                      </Text>
                    </View>
                    
                    <View style={[styles.indicator, { backgroundColor: theme.colors.accent }]}>
                      <Text style={[styles.indicatorText, { color: 'white' }]}>
                        {t('gestures.rotate')}
                      </Text>
                    </View>
                  </View>
                </TouchableOpacity>
              </Animated.View>
            </RotationGestureHandler>
          </Animated.View>
        </PinchGestureHandler>
      </Animated.View>
    </PanGestureHandler>
  );
}

const styles = StyleSheet.create({
  card: {
    width: screenWidth * 0.9,
    minHeight: 200,
    borderRadius: 16,
    borderWidth: 1,
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
    marginVertical: 8,
    marginHorizontal: screenWidth * 0.05,
    overflow: 'hidden',
  },
  pressed: {
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 8,
  },
  longPressed: {
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 12,
  },
  image: {
    width: '100%',
    height: 120,
  },
  content: {
    padding: 16,
    flex: 1,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    lineHeight: 20,
  },
  gestureIndicators: {
    position: 'absolute',
    top: 8,
    right: 8,
    flexDirection: 'row',
    gap: 4,
  },
  indicator: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  indicatorText: {
    fontSize: 10,
    fontWeight: 'bold',
  },
});
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  Image,
  TouchableOpacity,
} from 'react-native';
import {
  PanGestureHandler,
  PinchGestureHandler,
  RotationGestureHandler,
  State,
} from 'react-native-gesture-handler';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
  runOnJS,
} from 'react-native-reanimated';
import { usePanGestureAnimation, usePinchGestureAnimation, useRotationGestureAnimation } from '../../lib/animations/advanced-animations';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

interface GestureCardProps {
  id: string;
  title: string;
  description: string;
  imageUrl?: string;
  onDismiss?: (id: string) => void;
  onPress?: (id: string) => void;
  onLongPress?: (id: string) => void;
  testID?: string;
}

export function GestureCard({
  id,
  title,
  description,
  imageUrl,
  onDismiss,
  onPress,
  onLongPress,
  testID,
}: GestureCardProps) {
  const { theme } = useAppStore();
  const { t } = useI18n();
  const [isPressed, setIsPressed] = useState(false);
  const [isLongPressed, setIsLongPressed] = useState(false);

  // Gesture animations
  const { panGestureHandler, animatedStyle: panStyle } = usePanGestureAnimation(
    useCallback((translation) => {
      if (Math.abs(translation.x) > screenWidth * 0.3) {
        onDismiss?.(id);
      }
    }, [id, onDismiss])
  );

  const { pinchGestureHandler, animatedStyle: pinchStyle } = usePinchGestureAnimation();
  const { rotationGestureHandler, animatedStyle: rotationStyle } = useRotationGestureAnimation();

  // Press animations
  const pressScale = useSharedValue(1);
  const pressOpacity = useSharedValue(1);

  const handlePressIn = useCallback(() => {
    setIsPressed(true);
    pressScale.value = withSpring(0.95, { damping: 15, stiffness: 300 });
    pressOpacity.value = withTiming(0.8, { duration: 100 });
  }, [pressScale, pressOpacity]);

  const handlePressOut = useCallback(() => {
    setIsPressed(false);
    pressScale.value = withSpring(1, { damping: 15, stiffness: 300 });
    pressOpacity.value = withTiming(1, { duration: 100 });
  }, [pressScale, pressOpacity]);

  const handlePress = useCallback(() => {
    onPress?.(id);
  }, [id, onPress]);

  const handleLongPress = useCallback(() => {
    setIsLongPressed(true);
    onLongPress?.(id);
    
    // Reset long press state after animation
    setTimeout(() => {
      setIsLongPressed(false);
    }, 300);
  }, [id, onLongPress]);

  const pressAnimatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: pressScale.value }],
    opacity: pressOpacity.value,
  }));

  const combinedAnimatedStyle = useAnimatedStyle(() => ({
    ...panStyle.value,
    ...pinchStyle.value,
    ...rotationStyle.value,
    ...pressAnimatedStyle.value,
  }));

  const cardStyle = [
    styles.card,
    {
      backgroundColor: theme.colors.surface,
      borderColor: theme.colors.border,
      shadowColor: theme.colors.shadow,
    },
    isPressed && styles.pressed,
    isLongPressed && styles.longPressed,
  ];

  return (
    <PanGestureHandler
      onGestureEvent={panGestureHandler}
      onHandlerStateChange={(event) => {
        if (event.nativeEvent.state === State.END) {
          runOnJS(handlePressOut)();
        }
      }}
    >
      <Animated.View style={[combinedAnimatedStyle]}>
        <PinchGestureHandler onGestureEvent={pinchGestureHandler}>
          <Animated.View>
            <RotationGestureHandler onGestureEvent={rotationGestureHandler}>
              <Animated.View>
                <TouchableOpacity
                  testID={testID}
                  onPressIn={handlePressIn}
                  onPressOut={handlePressOut}
                  onPress={handlePress}
                  onLongPress={handleLongPress}
                  delayLongPress={500}
                  activeOpacity={1}
                  style={cardStyle}
                >
                  {imageUrl && (
                    <Image
                      source={{ uri: imageUrl }}
                      style={styles.image}
                      resizeMode="cover"
                    />
                  )}
                  
                  <View style={styles.content}>
                    <Text
                      style={[styles.title, { color: theme.colors.text }]}
                      numberOfLines={2}
                    >
                      {title}
                    </Text>
                    
                    <Text
                      style={[styles.description, { color: theme.colors.textSecondary }]}
                      numberOfLines={3}
                    >
                      {description}
                    </Text>
                  </View>

                  {/* Gesture indicators */}
                  <View style={styles.gestureIndicators}>
                    <View style={[styles.indicator, { backgroundColor: theme.colors.primary }]}>
                      <Text style={[styles.indicatorText, { color: 'white' }]}>
                        {t('gestures.swipe')}
                      </Text>
                    </View>
                    
                    <View style={[styles.indicator, { backgroundColor: theme.colors.secondary }]}>
                      <Text style={[styles.indicatorText, { color: 'white' }]}>
                        {t('gestures.pinch')}
                      </Text>
                    </View>
                    
                    <View style={[styles.indicator, { backgroundColor: theme.colors.accent }]}>
                      <Text style={[styles.indicatorText, { color: 'white' }]}>
                        {t('gestures.rotate')}
                      </Text>
                    </View>
                  </View>
                </TouchableOpacity>
              </Animated.View>
            </RotationGestureHandler>
          </Animated.View>
        </PinchGestureHandler>
      </Animated.View>
    </PanGestureHandler>
  );
}

const styles = StyleSheet.create({
  card: {
    width: screenWidth * 0.9,
    minHeight: 200,
    borderRadius: 16,
    borderWidth: 1,
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
    marginVertical: 8,
    marginHorizontal: screenWidth * 0.05,
    overflow: 'hidden',
  },
  pressed: {
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 8,
  },
  longPressed: {
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 12,
  },
  image: {
    width: '100%',
    height: 120,
  },
  content: {
    padding: 16,
    flex: 1,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    lineHeight: 20,
  },
  gestureIndicators: {
    position: 'absolute',
    top: 8,
    right: 8,
    flexDirection: 'row',
    gap: 4,
  },
  indicator: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  indicatorText: {
    fontSize: 10,
    fontWeight: 'bold',
  },
});


