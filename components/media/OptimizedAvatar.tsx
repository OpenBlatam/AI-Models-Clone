import React, { useCallback, useMemo } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ViewStyle } from 'react-native';
import { OptimizedImage } from './OptimizedImage';

interface OptimizedAvatarProps {
  uri?: string;
  initials?: string;
  size?: 'small' | 'medium' | 'large' | 'xlarge';
  variant?: 'circle' | 'rounded' | 'square';
  onPress?: () => void;
  isOnline?: boolean;
  style?: ViewStyle;
  accessibilityLabel?: string;
}

const sizeMap = {
  small: 32,
  medium: 48,
  large: 64,
  xlarge: 96,
} as const;

const borderRadiusMap = {
  circle: 50,
  rounded: 8,
  square: 0,
} as const;

export const OptimizedAvatar: React.FC<OptimizedAvatarProps> = ({
  uri,
  initials,
  size = 'medium',
  variant = 'circle',
  onPress,
  isOnline,
  style,
  accessibilityLabel,
}) => {
  const avatarSize = sizeMap[size];
  const borderRadius = (avatarSize * borderRadiusMap[variant]) / 100;

  const handlePress = useCallback(() => {
    onPress?.();
  }, [onPress]);

  const renderContent = useMemo(() => {
    if (uri) {
      return (
        <OptimizedImage
          uri={uri}
          width={avatarSize}
          height={avatarSize}
          borderRadius={borderRadius}
          priority="high"
        />
      );
    }

    if (initials) {
      return (
        <View style={[styles.initialsContainer, { width: avatarSize, height: avatarSize, borderRadius }]}>
          <Text style={[styles.initials, { fontSize: avatarSize * 0.4 }]}>
            {initials.toUpperCase()}
          </Text>
        </View>
      );
    }

    return (
      <View style={[styles.placeholder, { width: avatarSize, height: avatarSize, borderRadius }]}>
        <Text style={[styles.placeholderText, { fontSize: avatarSize * 0.3 }]}>
          👤
        </Text>
      </View>
    );
  }, [uri, initials, avatarSize, borderRadius]);

  const Container = onPress ? TouchableOpacity : View;

  return (
    <Container
      style={[styles.container, style]}
      onPress={handlePress}
      accessible={true}
      accessibilityLabel={accessibilityLabel || `Avatar ${initials || 'user'}`}
      accessibilityRole={onPress ? 'button' : undefined}
    >
      {renderContent}
      {isOnline && (
        <View style={[styles.onlineIndicator, { width: avatarSize * 0.25, height: avatarSize * 0.25 }]} />
      )}
    </Container>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'relative',
  },
  initialsContainer: {
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  initials: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  placeholder: {
    backgroundColor: '#F2F2F7',
    justifyContent: 'center',
    alignItems: 'center',
  },
  placeholderText: {
    color: '#8E8E93',
  },
  onlineIndicator: {
    position: 'absolute',
    bottom: 2,
    right: 2,
    backgroundColor: '#34C759',
    borderRadius: 50,
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
}); 