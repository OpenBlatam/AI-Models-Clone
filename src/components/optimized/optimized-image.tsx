import React, { useState, useCallback, useMemo, memo } from 'react';
import {
  View,
  StyleSheet,
  ViewStyle,
  ImageStyle,
  ActivityIndicator,
  Animated,
  Dimensions,
} from 'react-native';
import { Image } from 'expo-image';
import { useColorScheme } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

// ============================================================================
// TYPES
// ============================================================================

interface OptimizedImageProps {
  source: string | { uri: string };
  width?: number;
  height?: number;
  style?: ViewStyle | ImageStyle;
  placeholder?: string;
  fallback?: string;
  resizeMode?: 'cover' | 'contain' | 'stretch' | 'center' | 'repeat';
  priority?: 'low' | 'normal' | 'high';
  cachePolicy?: 'memory' | 'disk' | 'memory-disk' | 'none';
  blurRadius?: number;
  borderRadius?: number;
  aspectRatio?: number;
  isLazy?: boolean;
  onLoad?: () => void;
  onError?: (error: any) => void;
  onLoadStart?: () => void;
  onLoadEnd?: () => void;
  // Accessibility
  accessibilityLabel?: string;
  accessibilityHint?: string;
  // Performance
  enableWebP?: boolean;
  quality?: number;
  // Animation
  fadeInDuration?: number;
  scaleInDuration?: number;
  // Error handling
  showErrorIcon?: boolean;
  errorIconSize?: number;
  errorIconColor?: string;
}

interface ImageState {
  isLoading: boolean;
  hasError: boolean;
  isLoaded: boolean;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const { width: screenWidth } = Dimensions.get('window');
const DEFAULT_FADE_DURATION = 300;
const DEFAULT_SCALE_DURATION = 200;

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const OptimizedImage = memo<OptimizedImageProps>(({
  source,
  width,
  height,
  style,
  placeholder,
  fallback,
  resizeMode = 'cover',
  priority = 'normal',
  cachePolicy = 'memory-disk',
  blurRadius = 0,
  borderRadius = 0,
  aspectRatio,
  isLazy = true,
  onLoad,
  onError,
  onLoadStart,
  onLoadEnd,
  accessibilityLabel,
  accessibilityHint,
  enableWebP = true,
  quality = 0.8,
  fadeInDuration = DEFAULT_FADE_DURATION,
  scaleInDuration = DEFAULT_SCALE_DURATION,
  showErrorIcon = true,
  errorIconSize = 24,
  errorIconColor,
}) => {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  
  const [imageState, setImageState] = useState<ImageState>({
    isLoading: true,
    hasError: false,
    isLoaded: false,
  });
  
  const [fadeAnim] = useState(new Animated.Value(0));
  const [scaleAnim] = useState(new Animated.Value(0.95));

  // ============================================================================
  // MEMOIZED VALUES
  // ============================================================================

  const imageSource = useMemo(() => {
    if (typeof source === 'string') {
      return { uri: source };
    }
    return source;
  }, [source]);

  const optimizedSource = useMemo(() => {
    if (!enableWebP || typeof source !== 'string') {
      return imageSource;
    }

    // Add WebP support if the source is a URL
    const url = new URL(source);
    const params = new URLSearchParams(url.search);
    
    // Add WebP format if supported
    if (params.get('format') !== 'webp') {
      params.set('format', 'webp');
    }
    
    // Add quality parameter
    if (params.get('quality') !== quality.toString()) {
      params.set('quality', quality.toString());
    }
    
    // Add responsive width if not specified
    if (width && !params.get('w')) {
      params.set('w', width.toString());
    }
    
    url.search = params.toString();
    return { uri: url.toString() };
  }, [source, imageSource, enableWebP, quality, width]);

  const containerStyle = useMemo(() => {
    const baseStyle: ViewStyle = {
      width: width || '100%',
      height: height || 'auto',
      borderRadius,
      overflow: 'hidden',
    };

    if (aspectRatio) {
      baseStyle.aspectRatio = aspectRatio;
    }

    return [baseStyle, style];
  }, [width, height, borderRadius, aspectRatio, style]);

  const imageStyle = useMemo(() => {
    return {
      width: '100%',
      height: '100%',
      borderRadius,
    };
  }, [borderRadius]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleLoadStart = useCallback(() => {
    setImageState(prev => ({ ...prev, isLoading: true, hasError: false }));
    onLoadStart?.();
  }, [onLoadStart]);

  const handleLoad = useCallback(() => {
    setImageState(prev => ({ ...prev, isLoading: false, isLoaded: true }));
    
    // Start animations
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: fadeInDuration,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: scaleInDuration,
        useNativeDriver: true,
      }),
    ]).start();
    
    onLoad?.();
    onLoadEnd?.();
  }, [fadeAnim, scaleAnim, fadeInDuration, scaleInDuration, onLoad, onLoadEnd]);

  const handleError = useCallback((error: any) => {
    setImageState(prev => ({ ...prev, isLoading: false, hasError: true }));
    onError?.(error);
    onLoadEnd?.();
  }, [onError, onLoadEnd]);

  // ============================================================================
  // RENDER HELPERS
  // ============================================================================

  const renderPlaceholder = () => {
    if (!placeholder) return null;
    
    return (
      <View style={[styles.placeholder, containerStyle]}>
        <Image
          source={{ uri: placeholder }}
          style={imageStyle}
          contentFit={resizeMode}
          cachePolicy={cachePolicy}
        />
      </View>
    );
  };

  const renderErrorState = () => {
    if (!showErrorIcon) return null;
    
    return (
      <View style={[styles.errorContainer, containerStyle]}>
        <Ionicons
          name="image-outline"
          size={errorIconSize}
          color={errorIconColor || (isDark ? '#8E8E93' : '#6C6C70')}
        />
      </View>
    );
  };

  const renderLoadingIndicator = () => {
    if (!imageState.isLoading) return null;
    
    return (
      <View style={[styles.loadingContainer, containerStyle]}>
        <ActivityIndicator
          size="small"
          color={isDark ? '#007AFF' : '#007AFF'}
        />
      </View>
    );
  };

  // ============================================================================
  // RENDER
  // ============================================================================

  if (imageState.hasError) {
    return renderErrorState();
  }

  return (
    <View style={containerStyle}>
      {/* Placeholder */}
      {imageState.isLoading && renderPlaceholder()}
      
      {/* Loading Indicator */}
      {renderLoadingIndicator()}
      
      {/* Main Image */}
      <Animated.View
        style={[
          styles.imageContainer,
          {
            opacity: fadeAnim,
            transform: [{ scale: scaleAnim }],
          },
        ]}
      >
        <Image
          source={optimizedSource}
          style={imageStyle}
          contentFit={resizeMode}
          priority={priority}
          cachePolicy={cachePolicy}
          blurRadius={blurRadius}
          onLoadStart={handleLoadStart}
          onLoad={handleLoad}
          onError={handleError}
          accessible={true}
          accessibilityLabel={accessibilityLabel}
          accessibilityHint={accessibilityHint}
          accessibilityRole="image"
        />
      </Animated.View>
    </View>
  );
});

OptimizedImage.displayName = 'OptimizedImage';

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  imageContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  placeholder: {
    backgroundColor: '#F0F0F0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.05)',
  },
  errorContainer: {
    backgroundColor: '#F8F9FA',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderStyle: 'dashed',
  },
});

// ============================================================================
// SPECIALIZED COMPONENTS
// ============================================================================

export const AvatarImage = memo<Omit<OptimizedImageProps, 'aspectRatio' | 'resizeMode'>>((props) => (
  <OptimizedImage
    {...props}
    aspectRatio={1}
    resizeMode="cover"
    borderRadius={props.borderRadius || 50}
    priority="high"
  />
));

export const CardImage = memo<Omit<OptimizedImageProps, 'resizeMode'>>((props) => (
  <OptimizedImage
    {...props}
    resizeMode="cover"
    borderRadius={props.borderRadius || 12}
    priority="normal"
  />
));

export const ThumbnailImage = memo<Omit<OptimizedImageProps, 'resizeMode' | 'priority'>>((props) => (
  <OptimizedImage
    {...props}
    resizeMode="cover"
    priority="low"
    isLazy={true}
    width={props.width || 100}
    height={props.height || 100}
  />
));

// ============================================================================
// HOOK FOR IMAGE OPTIMIZATION
// ============================================================================

export function useImageOptimization() {
  const preloadImages = useCallback(async (urls: string[]) => {
    try {
      await Promise.all(
        urls.map(url => 
          Image.prefetch(url, { cachePolicy: 'memory-disk' })
        )
      );
    } catch (error) {
      console.error('Error preloading images:', error);
    }
  }, []);

  const clearImageCache = useCallback(async () => {
    try {
      await Image.clearMemoryCache();
      await Image.clearDiskCache();
    } catch (error) {
      console.error('Error clearing image cache:', error);
    }
  }, []);

  const getImageInfo = useCallback(async (url: string) => {
    try {
      const info = await Image.getSizeAsync(url);
      return info;
    } catch (error) {
      console.error('Error getting image info:', error);
      return null;
    }
  }, []);

  return {
    preloadImages,
    clearImageCache,
    getImageInfo,
  };
}
import {
  View,
  StyleSheet,
  ViewStyle,
  ImageStyle,
  ActivityIndicator,
  Animated,
  Dimensions,
} from 'react-native';
import { Image } from 'expo-image';
import { useColorScheme } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

// ============================================================================
// TYPES
// ============================================================================

interface OptimizedImageProps {
  source: string | { uri: string };
  width?: number;
  height?: number;
  style?: ViewStyle | ImageStyle;
  placeholder?: string;
  fallback?: string;
  resizeMode?: 'cover' | 'contain' | 'stretch' | 'center' | 'repeat';
  priority?: 'low' | 'normal' | 'high';
  cachePolicy?: 'memory' | 'disk' | 'memory-disk' | 'none';
  blurRadius?: number;
  borderRadius?: number;
  aspectRatio?: number;
  isLazy?: boolean;
  onLoad?: () => void;
  onError?: (error: any) => void;
  onLoadStart?: () => void;
  onLoadEnd?: () => void;
  // Accessibility
  accessibilityLabel?: string;
  accessibilityHint?: string;
  // Performance
  enableWebP?: boolean;
  quality?: number;
  // Animation
  fadeInDuration?: number;
  scaleInDuration?: number;
  // Error handling
  showErrorIcon?: boolean;
  errorIconSize?: number;
  errorIconColor?: string;
}

interface ImageState {
  isLoading: boolean;
  hasError: boolean;
  isLoaded: boolean;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const { width: screenWidth } = Dimensions.get('window');
const DEFAULT_FADE_DURATION = 300;
const DEFAULT_SCALE_DURATION = 200;

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const OptimizedImage = memo<OptimizedImageProps>(({
  source,
  width,
  height,
  style,
  placeholder,
  fallback,
  resizeMode = 'cover',
  priority = 'normal',
  cachePolicy = 'memory-disk',
  blurRadius = 0,
  borderRadius = 0,
  aspectRatio,
  isLazy = true,
  onLoad,
  onError,
  onLoadStart,
  onLoadEnd,
  accessibilityLabel,
  accessibilityHint,
  enableWebP = true,
  quality = 0.8,
  fadeInDuration = DEFAULT_FADE_DURATION,
  scaleInDuration = DEFAULT_SCALE_DURATION,
  showErrorIcon = true,
  errorIconSize = 24,
  errorIconColor,
}) => {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  
  const [imageState, setImageState] = useState<ImageState>({
    isLoading: true,
    hasError: false,
    isLoaded: false,
  });
  
  const [fadeAnim] = useState(new Animated.Value(0));
  const [scaleAnim] = useState(new Animated.Value(0.95));

  // ============================================================================
  // MEMOIZED VALUES
  // ============================================================================

  const imageSource = useMemo(() => {
    if (typeof source === 'string') {
      return { uri: source };
    }
    return source;
  }, [source]);

  const optimizedSource = useMemo(() => {
    if (!enableWebP || typeof source !== 'string') {
      return imageSource;
    }

    // Add WebP support if the source is a URL
    const url = new URL(source);
    const params = new URLSearchParams(url.search);
    
    // Add WebP format if supported
    if (params.get('format') !== 'webp') {
      params.set('format', 'webp');
    }
    
    // Add quality parameter
    if (params.get('quality') !== quality.toString()) {
      params.set('quality', quality.toString());
    }
    
    // Add responsive width if not specified
    if (width && !params.get('w')) {
      params.set('w', width.toString());
    }
    
    url.search = params.toString();
    return { uri: url.toString() };
  }, [source, imageSource, enableWebP, quality, width]);

  const containerStyle = useMemo(() => {
    const baseStyle: ViewStyle = {
      width: width || '100%',
      height: height || 'auto',
      borderRadius,
      overflow: 'hidden',
    };

    if (aspectRatio) {
      baseStyle.aspectRatio = aspectRatio;
    }

    return [baseStyle, style];
  }, [width, height, borderRadius, aspectRatio, style]);

  const imageStyle = useMemo(() => {
    return {
      width: '100%',
      height: '100%',
      borderRadius,
    };
  }, [borderRadius]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleLoadStart = useCallback(() => {
    setImageState(prev => ({ ...prev, isLoading: true, hasError: false }));
    onLoadStart?.();
  }, [onLoadStart]);

  const handleLoad = useCallback(() => {
    setImageState(prev => ({ ...prev, isLoading: false, isLoaded: true }));
    
    // Start animations
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: fadeInDuration,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: scaleInDuration,
        useNativeDriver: true,
      }),
    ]).start();
    
    onLoad?.();
    onLoadEnd?.();
  }, [fadeAnim, scaleAnim, fadeInDuration, scaleInDuration, onLoad, onLoadEnd]);

  const handleError = useCallback((error: any) => {
    setImageState(prev => ({ ...prev, isLoading: false, hasError: true }));
    onError?.(error);
    onLoadEnd?.();
  }, [onError, onLoadEnd]);

  // ============================================================================
  // RENDER HELPERS
  // ============================================================================

  const renderPlaceholder = () => {
    if (!placeholder) return null;
    
    return (
      <View style={[styles.placeholder, containerStyle]}>
        <Image
          source={{ uri: placeholder }}
          style={imageStyle}
          contentFit={resizeMode}
          cachePolicy={cachePolicy}
        />
      </View>
    );
  };

  const renderErrorState = () => {
    if (!showErrorIcon) return null;
    
    return (
      <View style={[styles.errorContainer, containerStyle]}>
        <Ionicons
          name="image-outline"
          size={errorIconSize}
          color={errorIconColor || (isDark ? '#8E8E93' : '#6C6C70')}
        />
      </View>
    );
  };

  const renderLoadingIndicator = () => {
    if (!imageState.isLoading) return null;
    
    return (
      <View style={[styles.loadingContainer, containerStyle]}>
        <ActivityIndicator
          size="small"
          color={isDark ? '#007AFF' : '#007AFF'}
        />
      </View>
    );
  };

  // ============================================================================
  // RENDER
  // ============================================================================

  if (imageState.hasError) {
    return renderErrorState();
  }

  return (
    <View style={containerStyle}>
      {/* Placeholder */}
      {imageState.isLoading && renderPlaceholder()}
      
      {/* Loading Indicator */}
      {renderLoadingIndicator()}
      
      {/* Main Image */}
      <Animated.View
        style={[
          styles.imageContainer,
          {
            opacity: fadeAnim,
            transform: [{ scale: scaleAnim }],
          },
        ]}
      >
        <Image
          source={optimizedSource}
          style={imageStyle}
          contentFit={resizeMode}
          priority={priority}
          cachePolicy={cachePolicy}
          blurRadius={blurRadius}
          onLoadStart={handleLoadStart}
          onLoad={handleLoad}
          onError={handleError}
          accessible={true}
          accessibilityLabel={accessibilityLabel}
          accessibilityHint={accessibilityHint}
          accessibilityRole="image"
        />
      </Animated.View>
    </View>
  );
});

OptimizedImage.displayName = 'OptimizedImage';

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  imageContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  placeholder: {
    backgroundColor: '#F0F0F0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.05)',
  },
  errorContainer: {
    backgroundColor: '#F8F9FA',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderStyle: 'dashed',
  },
});

// ============================================================================
// SPECIALIZED COMPONENTS
// ============================================================================

export const AvatarImage = memo<Omit<OptimizedImageProps, 'aspectRatio' | 'resizeMode'>>((props) => (
  <OptimizedImage
    {...props}
    aspectRatio={1}
    resizeMode="cover"
    borderRadius={props.borderRadius || 50}
    priority="high"
  />
));

export const CardImage = memo<Omit<OptimizedImageProps, 'resizeMode'>>((props) => (
  <OptimizedImage
    {...props}
    resizeMode="cover"
    borderRadius={props.borderRadius || 12}
    priority="normal"
  />
));

export const ThumbnailImage = memo<Omit<OptimizedImageProps, 'resizeMode' | 'priority'>>((props) => (
  <OptimizedImage
    {...props}
    resizeMode="cover"
    priority="low"
    isLazy={true}
    width={props.width || 100}
    height={props.height || 100}
  />
));

// ============================================================================
// HOOK FOR IMAGE OPTIMIZATION
// ============================================================================

export function useImageOptimization() {
  const preloadImages = useCallback(async (urls: string[]) => {
    try {
      await Promise.all(
        urls.map(url => 
          Image.prefetch(url, { cachePolicy: 'memory-disk' })
        )
      );
    } catch (error) {
      console.error('Error preloading images:', error);
    }
  }, []);

  const clearImageCache = useCallback(async () => {
    try {
      await Image.clearMemoryCache();
      await Image.clearDiskCache();
    } catch (error) {
      console.error('Error clearing image cache:', error);
    }
  }, []);

  const getImageInfo = useCallback(async (url: string) => {
    try {
      const info = await Image.getSizeAsync(url);
      return info;
    } catch (error) {
      console.error('Error getting image info:', error);
      return null;
    }
  }, []);

  return {
    preloadImages,
    clearImageCache,
    getImageInfo,
  };
}


