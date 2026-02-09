import React, { useCallback, useMemo } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Modal,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { BlurView } from 'react-native-blur';
import { Ionicons } from '@expo/vector-icons';

interface OptimizedModalProps {
  isVisible: boolean;
  onClose: () => void;
  title?: string;
  subtitle?: string;
  children?: React.ReactNode;
  variant?: 'default' | 'sheet' | 'fullscreen' | 'centered';
  size?: 'small' | 'medium' | 'large';
  showCloseButton?: boolean;
  closeOnBackdropPress?: boolean;
  style?: ViewStyle;
  contentStyle?: ViewStyle;
  titleStyle?: TextStyle;
  subtitleStyle?: TextStyle;
  accessibilityLabel?: string;
  accessibilityHint?: string;
}

export const OptimizedModal: React.FC<OptimizedModalProps> = ({
  isVisible,
  onClose,
  title,
  subtitle,
  children,
  variant = 'default',
  size = 'medium',
  showCloseButton = true,
  closeOnBackdropPress = true,
  style,
  contentStyle,
  titleStyle,
  subtitleStyle,
  accessibilityLabel,
  accessibilityHint,
}) => {
  const handleBackdropPress = useCallback(() => {
    if (closeOnBackdropPress) {
      onClose();
    }
  }, [closeOnBackdropPress, onClose]);

  const handleClosePress = useCallback(() => {
    onClose();
  }, [onClose]);

  const getModalStyle = useCallback((): ViewStyle => {
    const baseStyle: ViewStyle = {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      ...style,
    };

    const variantStyles: Record<string, ViewStyle> = {
      default: { padding: 20 },
      sheet: { justifyContent: 'flex-end' },
      fullscreen: { padding: 0 },
      centered: { padding: 40 },
    };

    return {
      ...baseStyle,
      ...variantStyles[variant],
    };
  }, [variant, style]);

  const getContentStyle = useCallback((): ViewStyle => {
    const baseStyle: ViewStyle = {
      backgroundColor: '#FFFFFF',
      borderRadius: 12,
      overflow: 'hidden',
      ...contentStyle,
    };

    const sizeStyles: Record<string, ViewStyle> = {
      small: { minWidth: 280, maxWidth: 320 },
      medium: { minWidth: 320, maxWidth: 400 },
      large: { minWidth: 400, maxWidth: 500 },
    };

    const variantStyles: Record<string, ViewStyle> = {
      default: { padding: 20 },
      sheet: { 
        borderTopLeftRadius: 20,
        borderTopRightRadius: 20,
        padding: 20,
        paddingTop: 30,
      },
      fullscreen: { 
        flex: 1,
        borderRadius: 0,
      },
      centered: { padding: 24 },
    };

    return {
      ...baseStyle,
      ...sizeStyles[size],
      ...variantStyles[variant],
    };
  }, [variant, size, contentStyle]);

  const getTitleStyle = useCallback((): TextStyle => {
    const baseStyle: TextStyle = {
      fontSize: 18,
      fontWeight: '600',
      color: '#000000',
      marginBottom: 4,
      ...titleStyle,
    };

    const sizeStyles: Record<string, TextStyle> = {
      small: { fontSize: 16 },
      medium: { fontSize: 18 },
      large: { fontSize: 20 },
    };

    return {
      ...baseStyle,
      ...sizeStyles[size],
    };
  }, [size, titleStyle]);

  const getSubtitleStyle = useCallback((): TextStyle => {
    const baseStyle: TextStyle = {
      fontSize: 14,
      color: '#8E8E93',
      marginBottom: 16,
      ...subtitleStyle,
    };

    const sizeStyles: Record<string, TextStyle> = {
      small: { fontSize: 12 },
      medium: { fontSize: 14 },
      large: { fontSize: 16 },
    };

    return {
      ...baseStyle,
      ...sizeStyles[size],
    };
  }, [size, subtitleStyle]);

  const renderHeader = useMemo(() => {
    if (!title && !subtitle && !showCloseButton) {
      return null;
    }

    return (
      <View style={styles.header}>
        <View style={styles.headerContent}>
          {title && <Text style={getTitleStyle()}>{title}</Text>}
          {subtitle && <Text style={getSubtitleStyle()}>{subtitle}</Text>}
        </View>
        {showCloseButton && (
          <TouchableOpacity
            onPress={handleClosePress}
            style={styles.closeButton}
            accessible={true}
            accessibilityLabel="Close modal"
            accessibilityRole="button"
          >
            <Ionicons name="close" size={24} color="#8E8E93" />
          </TouchableOpacity>
        )}
      </View>
    );
  }, [title, subtitle, showCloseButton, getTitleStyle, getSubtitleStyle, handleClosePress]);

  const renderContent = useMemo(() => {
    if (!children) return null;
    return <View style={styles.content}>{children}</View>;
  }, [children]);

  return (
    <Modal
      visible={isVisible}
      transparent={true}
      animationType="fade"
      onRequestClose={onClose}
      accessible={true}
      accessibilityLabel={accessibilityLabel || title}
      accessibilityHint={accessibilityHint}
    >
      <TouchableOpacity
        style={getModalStyle()}
        activeOpacity={1}
        onPress={handleBackdropPress}
        accessible={false}
      >
        <TouchableOpacity
          style={getContentStyle()}
          activeOpacity={1}
          onPress={() => {}}
          accessible={false}
        >
          {renderHeader}
          {renderContent}
        </TouchableOpacity>
      </TouchableOpacity>
    </Modal>
  );
};

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  headerContent: {
    flex: 1,
  },
  closeButton: {
    padding: 4,
    marginLeft: 8,
  },
  content: {
    flex: 1,
  },
}); 