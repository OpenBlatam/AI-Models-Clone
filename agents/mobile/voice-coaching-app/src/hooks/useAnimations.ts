import { useRef, useEffect, useCallback } from 'react';
import { Animated, Easing } from 'react-native';

/**
 * Custom hook for fade animations
 * @param initialValue - Initial opacity value (0-1)
 * @param duration - Animation duration in milliseconds
 */
export function useFadeAnimation(initialValue = 0, duration = 300) {
    const animatedValue = useRef(new Animated.Value(initialValue)).current;

    const fadeIn = useCallback(() => {
        Animated.timing(animatedValue, {
            toValue: 1,
            duration,
            useNativeDriver: true,
        }).start();
    }, [animatedValue, duration]);

    const fadeOut = useCallback(() => {
        Animated.timing(animatedValue, {
            toValue: 0,
            duration,
            useNativeDriver: true,
        }).start();
    }, [animatedValue, duration]);

    return { animatedValue, fadeIn, fadeOut };
}

/**
 * Custom hook for scale animations
 * @param initialScale - Initial scale value
 */
export function useScaleAnimation(initialScale = 1) {
    const scaleValue = useRef(new Animated.Value(initialScale)).current;

    const pulse = useCallback(() => {
        Animated.sequence([
            Animated.timing(scaleValue, {
                toValue: 1.1,
                duration: 150,
                useNativeDriver: true,
            }),
            Animated.timing(scaleValue, {
                toValue: 1,
                duration: 150,
                useNativeDriver: true,
            }),
        ]).start();
    }, [scaleValue]);

    const bounce = useCallback(() => {
        Animated.spring(scaleValue, {
            toValue: 1,
            friction: 3,
            tension: 40,
            useNativeDriver: true,
        }).start();
    }, [scaleValue]);

    return { scaleValue, pulse, bounce };
}

/**
 * Custom hook for slide animations
 * @param direction - 'up' | 'down' | 'left' | 'right'
 * @param distance - Distance to slide in pixels
 */
export function useSlideAnimation(
    direction: 'up' | 'down' | 'left' | 'right' = 'up',
    distance = 100
) {
    const translateValue = useRef(new Animated.Value(distance)).current;

    const getTransform = () => {
        switch (direction) {
            case 'up':
            case 'down':
                return { translateY: translateValue };
            case 'left':
            case 'right':
                return { translateX: translateValue };
        }
    };

    const slideIn = useCallback(() => {
        Animated.timing(translateValue, {
            toValue: 0,
            duration: 300,
            easing: Easing.out(Easing.cubic),
            useNativeDriver: true,
        }).start();
    }, [translateValue]);

    const slideOut = useCallback(() => {
        Animated.timing(translateValue, {
            toValue: distance,
            duration: 300,
            easing: Easing.in(Easing.cubic),
            useNativeDriver: true,
        }).start();
    }, [translateValue, distance]);

    return { translateValue, transform: getTransform(), slideIn, slideOut };
}

/**
 * Custom hook for pulsing animation loop
 * @param isActive - Whether the animation should be running
 */
export function usePulsingAnimation(isActive: boolean) {
    const scaleAnim = useRef(new Animated.Value(1)).current;
    const opacityAnim = useRef(new Animated.Value(0.5)).current;

    useEffect(() => {
        if (isActive) {
            const animation = Animated.loop(
                Animated.parallel([
                    Animated.sequence([
                        Animated.timing(scaleAnim, {
                            toValue: 1.3,
                            duration: 1000,
                            useNativeDriver: true,
                        }),
                        Animated.timing(scaleAnim, {
                            toValue: 1,
                            duration: 1000,
                            useNativeDriver: true,
                        }),
                    ]),
                    Animated.sequence([
                        Animated.timing(opacityAnim, {
                            toValue: 0.2,
                            duration: 1000,
                            useNativeDriver: true,
                        }),
                        Animated.timing(opacityAnim, {
                            toValue: 0.5,
                            duration: 1000,
                            useNativeDriver: true,
                        }),
                    ]),
                ])
            );
            animation.start();
            return () => animation.stop();
        } else {
            scaleAnim.setValue(1);
            opacityAnim.setValue(0.5);
        }
    }, [isActive, scaleAnim, opacityAnim]);

    return { scaleAnim, opacityAnim };
}
