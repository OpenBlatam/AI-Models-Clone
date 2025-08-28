import React, { useState, useCallback, useMemo } from 'react';
import { View, StyleSheet, Dimensions } from 'react-native';
import { Image } from 'expo-image';
import SkeletonPlaceholder from 'react-native-skeleton-placeholder';

// ============================================================================
// TYPES
// ============================================================================
interface OptimizedImageProps {
  source: string | { uri: string };
  width?: number;
  height?: number;
  aspectRatio?: number;
  placeholder?: string;
  fallback?: string;
  priority?: 'low' | 'normal' | 'high';
  cachePolicy?: 'memory' | 'disk' | 'memory-disk';
  contentFit?: 'cover' | 'contain' | 'fill' | 'none' | 'scale-down';
  transition?: number;
  blurhash?: string;
  onLoadStart?: () => void;
  onLoadEnd?: () => void;
  onError?: (error: any) => void;
  onPress?: () => void;
  style?: any;
  testID?: string;
}

interface ImageState {
  isLoading: boolean;
  hasError: boolean;
  isLoaded: boolean;
}

// ============================================================================
// STATIC CONTENT
// ============================================================================
const DEFAULT_TRANSITION = 300;
const DEFAULT_PRIORITY = 'normal' as const;
const DEFAULT_CACHE_POLICY = 'memory-disk' as const;
const DEFAULT_CONTENT_FIT = 'cover' as const;

const IMAGE_SIZES = {
  thumbnail: { width: 100, height: 100 },
  small: { width: 200, height: 200 },
  medium: { width: 400, height: 400 },
  large: { width: 800, height: 800 },
  xlarge: { width: 1200, height: 1200 },
} as const;

// ============================================================================
// HELPERS
// ============================================================================
const getImageSource = (source: string | { uri: string }): { uri: string } => {
  if (typeof source === 'string') {
    return { uri: source };
  }
  return source;
};

const getWebPSource = (source: string | { uri: string }): { uri: string } => {
  const uri = typeof source === 'string' ? source : source.uri;
  
  // Check if WebP is supported and convert if possible
  if (uri.includes('.jpg') || uri.includes('.jpeg') || uri.includes('.png')) {
    const webpUri = uri.replace(/\.(jpg|jpeg|png)$/i, '.webp');
    return { uri: webpUri };
  }
  
  return getImageSource(source);
};

const getImageDimensions = (props: OptimizedImageProps): { width: number; height: number } => {
  const { width, height, aspectRatio } = props;
  const screenWidth = Dimensions.get('window').width;
  
  if (width && height) {
    return { width, height };
  }
  
  if (width && aspectRatio) {
    return { width, height: width / aspectRatio };
  }
  
  if (height && aspectRatio) {
    return { width: height * aspectRatio, height };
  }
  
  // Default to medium size
  return IMAGE_SIZES.medium;
};

const getSkeletonStyle = (props: OptimizedImageProps) => {
  const { width, height } = getImageDimensions(props);
  return {
    width,
    height,
    borderRadius: 8,
  };
};

// ============================================================================
// SUBCOMPONENTS
// ============================================================================
const ImageSkeleton: React.FC<{ props: OptimizedImageProps }> = ({ props }) => {
  const skeletonStyle = useMemo(() => getSkeletonStyle(props), [props]);
  
  return (
    <SkeletonPlaceholder>
      <View style={[styles.skeleton, skeletonStyle]} />
    </SkeletonPlaceholder>
  );
};

const ImageError: React.FC<{ props: OptimizedImageProps }> = ({ props }) => {
  const { fallback, onError } = props;
  
  const handleError = useCallback((error: any) => {
    console.warn('Image failed to load:', error);
    onError?.(error);
  }, [onError]);
  
  if (fallback) {
    return (
      <Image
        source={getImageSource(fallback)}
        style={[styles.image, props.style]}
        contentFit={props.contentFit || DEFAULT_CONTENT_FIT}
        transition={props.transition || DEFAULT_TRANSITION}
        onError={handleError}
        testID={props.testID}
      />
    );
  }
  
  return (
    <View style={[styles.errorContainer, props.style]}>
      <View style={styles.errorPlaceholder} />
    </View>
  );
};

// ============================================================================
// MAIN EXPORTED COMPONENT
// ============================================================================
export const OptimizedImage: React.FC<OptimizedImageProps> = (props) => {
  const [imageState, setImageState] = useState<ImageState>({
    isLoading: true,
    hasError: false,
    isLoaded: false,
  });
  
  const imageSource = useMemo(() => getWebPSource(props.source), [props.source]);
  const imageDimensions = useMemo(() => getImageDimensions(props), [props]);
  
  const handleLoadStart = useCallback(() => {
    setImageState(prev => ({ ...prev, isLoading: true, hasError: false }));
    props.onLoadStart?.();
  }, [props.onLoadStart]);
  
  const handleLoadEnd = useCallback(() => {
    setImageState(prev => ({ ...prev, isLoading: false, isLoaded: true }));
    props.onLoadEnd?.();
  }, [props.onLoadEnd]);
  
  const handleError = useCallback((error: any) => {
    setImageState(prev => ({ ...prev, isLoading: false, hasError: true }));
    props.onError?.(error);
  }, [props.onError]);
  
  const imageStyle = useMemo(() => [
    styles.image,
    imageDimensions,
    props.style,
  ], [imageDimensions, props.style]);
  
  if (imageState.hasError) {
    return <ImageError props={props} />;
  }
  
  return (
    <View style={styles.container}>
      <Image
        source={imageSource}
        style={imageStyle}
        contentFit={props.contentFit || DEFAULT_CONTENT_FIT}
        priority={props.priority || DEFAULT_PRIORITY}
        cachePolicy={props.cachePolicy || DEFAULT_CACHE_POLICY}
        transition={props.transition || DEFAULT_TRANSITION}
        blurhash={props.blurhash}
        placeholder={props.placeholder}
        onLoadStart={handleLoadStart}
        onLoadEnd={handleLoadEnd}
        onError={handleError}
        testID={props.testID}
      />
      {imageState.isLoading && <ImageSkeleton props={props} />}
    </View>
  );
};

// ============================================================================
// STYLES
// ============================================================================
const styles = StyleSheet.create({
  container: {
    position: 'relative',
  },
  image: {
    borderRadius: 8,
  },
  skeleton: {
    position: 'absolute',
    top: 0,
    left: 0,
  },
  errorContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
  },
  errorPlaceholder: {
    width: 40,
    height: 40,
    backgroundColor: '#e0e0e0',
    borderRadius: 20,
  },
});

// ============================================================================
// SPECIALIZED EXPORTS
// ============================================================================
export const ThumbnailImage: React.FC<Omit<OptimizedImageProps, 'width' | 'height'>> = (props) => (
  <OptimizedImage {...props} {...IMAGE_SIZES.thumbnail} />
);

export const SmallImage: React.FC<Omit<OptimizedImageProps, 'width' | 'height'>> = (props) => (
  <OptimizedImage {...props} {...IMAGE_SIZES.small} />
);

export const MediumImage: React.FC<Omit<OptimizedImageProps, 'width' | 'height'>> = (props) => (
  <OptimizedImage {...props} {...IMAGE_SIZES.medium} />
);

export const LargeImage: React.FC<Omit<OptimizedImageProps, 'width' | 'height'>> = (props) => (
  <OptimizedImage {...props} {...IMAGE_SIZES.large} />
);

export const XLargeImage: React.FC<Omit<OptimizedImageProps, 'width' | 'height'>> = (props) => (
  <OptimizedImage {...props} {...IMAGE_SIZES.xlarge} />
); 