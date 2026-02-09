import React, { useCallback, useMemo } from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface IconConfig {
  name: keyof typeof Ionicons.glyphMap;
  size: number;
  color: string;
}

interface OptimizedIconProps {
  name: keyof typeof Ionicons.glyphMap;
  size?: number;
  color?: string;
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  style?: ViewStyle;
  accessibilityLabel?: string;
}

const iconVariants = {
  default: { color: '#8E8E93' },
  primary: { color: '#007AFF' },
  secondary: { color: '#5AC8FA' },
  success: { color: '#34C759' },
  warning: { color: '#FF9500' },
  error: { color: '#FF3B30' },
} as const;

const iconSizes = {
  small: 16,
  medium: 24,
  large: 32,
  xlarge: 48,
} as const;

export const OptimizedIcon: React.FC<OptimizedIconProps> = ({
  name,
  size = 'medium',
  color,
  variant = 'default',
  style,
  accessibilityLabel,
}) => {
  const getIconConfig = useCallback((): IconConfig => {
    const iconSize = typeof size === 'string' ? iconSizes[size] : size;
    const iconColor = color || iconVariants[variant].color;
    
    return {
      name,
      size: iconSize,
      color: iconColor,
    };
  }, [name, size, color, variant]);

  const iconStyle = useMemo(() => [styles.icon, style], [style]);

  const config = getIconConfig();

  return (
    <View
      style={iconStyle}
      accessible={true}
      accessibilityLabel={accessibilityLabel || `Icon ${name}`}
      accessibilityRole="image"
    >
      <Ionicons
        name={config.name}
        size={config.size}
        color={config.color}
      />
    </View>
  );
};

// Modular icon components using iteration
const createIconComponent = (name: keyof typeof Ionicons.glyphMap, defaultVariant?: keyof typeof iconVariants) => {
  return React.forwardRef<View, Omit<OptimizedIconProps, 'name'>>((props, ref) => (
    <OptimizedIcon
      ref={ref}
      name={name}
      variant={defaultVariant}
      {...props}
    />
  ));
};

// Generate common icons using iteration
export const IconComponents = {
  // Navigation icons
  Home: createIconComponent('home'),
  Search: createIconComponent('search'),
  Profile: createIconComponent('person'),
  Settings: createIconComponent('settings'),
  
  // Action icons
  Add: createIconComponent('add', 'primary'),
  Edit: createIconComponent('create'),
  Delete: createIconComponent('trash', 'error'),
  Share: createIconComponent('share'),
  
  // Status icons
  Check: createIconComponent('checkmark', 'success'),
  Close: createIconComponent('close', 'error'),
  Warning: createIconComponent('warning', 'warning'),
  Info: createIconComponent('information-circle', 'primary'),
  
  // Media icons
  Camera: createIconComponent('camera'),
  Image: createIconComponent('image'),
  Video: createIconComponent('videocam'),
  Mic: createIconComponent('mic'),
  
  // Communication icons
  Mail: createIconComponent('mail'),
  Call: createIconComponent('call'),
  Message: createIconComponent('chatbubble'),
  Heart: createIconComponent('heart'),
  
  // Direction icons
  ArrowUp: createIconComponent('chevron-up'),
  ArrowDown: createIconComponent('chevron-down'),
  ArrowLeft: createIconComponent('chevron-back'),
  ArrowRight: createIconComponent('chevron-forward'),
} as const;

// Modular icon set generator
export const createIconSet = <T extends Record<string, keyof typeof Ionicons.glyphMap>>(
  iconMap: T,
  defaultVariant?: keyof typeof iconVariants
) => {
  const iconSet = {} as Record<keyof T, React.ForwardRefExoticComponent<any>>;
  
  Object.entries(iconMap).forEach(([key, iconName]) => {
    iconSet[key as keyof T] = createIconComponent(iconName, defaultVariant);
  });
  
  return iconSet;
};

// Example usage of modular icon sets
export const NavigationIcons = createIconSet({
  Home: 'home',
  Search: 'search',
  Profile: 'person',
  Settings: 'settings',
}, 'default');

export const ActionIcons = createIconSet({
  Add: 'add',
  Edit: 'create',
  Delete: 'trash',
  Share: 'share',
}, 'primary');

export const StatusIcons = createIconSet({
  Success: 'checkmark',
  Error: 'close',
  Warning: 'warning',
  Info: 'information-circle',
}, 'default');

const styles = StyleSheet.create({
  icon: {
    alignItems: 'center',
    justifyContent: 'center',
  },
}); 