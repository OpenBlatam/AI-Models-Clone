import React, { useCallback, useMemo } from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import SkeletonPlaceholder from 'react-native-skeleton-placeholder';

interface OptimizedSkeletonProps {
  width?: number | string;
  height?: number | string;
  borderRadius?: number;
  variant?: 'text' | 'avatar' | 'button' | 'card' | 'list';
  lines?: number;
  lineHeight?: number;
  lineSpacing?: number;
  style?: ViewStyle;
  accessibilityLabel?: string;
}

const variantConfigs = {
  text: {
    width: '100%',
    height: 16,
    borderRadius: 4,
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
  },
  button: {
    width: 120,
    height: 44,
    borderRadius: 8,
  },
  card: {
    width: '100%',
    height: 200,
    borderRadius: 12,
  },
  list: {
    width: '100%',
    height: 60,
    borderRadius: 8,
  },
} as const;

export const OptimizedSkeleton: React.FC<OptimizedSkeletonProps> = ({
  width,
  height,
  borderRadius,
  variant = 'text',
  lines = 1,
  lineHeight = 16,
  lineSpacing = 8,
  style,
  accessibilityLabel,
}) => {
  const getSkeletonStyle = useCallback((): ViewStyle => {
    const config = variantConfigs[variant];
    return {
      width: width ?? config.width,
      height: height ?? config.height,
      borderRadius: borderRadius ?? config.borderRadius,
    };
  }, [width, height, borderRadius, variant]);

  const renderSingleSkeleton = useCallback(() => (
    <View
      style={[getSkeletonStyle(), style]}
      accessible={true}
      accessibilityLabel={accessibilityLabel || `Loading ${variant}`}
    >
      <SkeletonPlaceholder>
        <View style={getSkeletonStyle()} />
      </SkeletonPlaceholder>
    </View>
  ), [getSkeletonStyle, style, accessibilityLabel, variant]);

  const renderMultiLineSkeleton = useCallback(() => (
    <View
      style={style}
      accessible={true}
      accessibilityLabel={accessibilityLabel || `Loading ${lines} lines`}
    >
      <SkeletonPlaceholder>
        {Array.from({ length: lines }, (_, index) => (
          <View
            key={index}
            style={{
              width: '100%',
              height: lineHeight,
              borderRadius: 4,
              marginBottom: index < lines - 1 ? lineSpacing : 0,
            }}
          />
        ))}
      </SkeletonPlaceholder>
    </View>
  ), [lines, lineHeight, lineSpacing, style, accessibilityLabel]);

  const skeletonContent = useMemo(() => {
    if (lines > 1) {
      return renderMultiLineSkeleton();
    }
    return renderSingleSkeleton();
  }, [lines, renderMultiLineSkeleton, renderSingleSkeleton]);

  return skeletonContent;
};

// Specialized skeleton components
export const TextSkeleton: React.FC<Omit<OptimizedSkeletonProps, 'variant'> & { lines?: number }> = (props) => (
  <OptimizedSkeleton variant="text" {...props} />
);

export const AvatarSkeleton: React.FC<Omit<OptimizedSkeletonProps, 'variant' | 'lines'> & { size?: number }> = ({ size, ...props }) => (
  <OptimizedSkeleton
    variant="avatar"
    width={size}
    height={size}
    borderRadius={size ? size / 2 : undefined}
    {...props}
  />
);

export const ButtonSkeleton: React.FC<Omit<OptimizedSkeletonProps, 'variant' | 'lines'> & { width?: number }> = (props) => (
  <OptimizedSkeleton variant="button" {...props} />
);

export const CardSkeleton: React.FC<Omit<OptimizedSkeletonProps, 'variant' | 'lines'> & { height?: number }> = (props) => (
  <OptimizedSkeleton variant="card" {...props} />
);

export const ListSkeleton: React.FC<Omit<OptimizedSkeletonProps, 'variant' | 'lines'> & { items?: number }> = ({ items = 3, ...props }) => (
  <View style={{ gap: 12 }}>
    {Array.from({ length: items }, (_, index) => (
      <OptimizedSkeleton key={index} variant="list" {...props} />
    ))}
  </View>
); 