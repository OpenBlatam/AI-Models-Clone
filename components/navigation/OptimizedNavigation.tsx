import React, { useCallback, useMemo } from 'react';
import { View, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface NavigationProps {
  title: string;
  onBack?: () => void;
  onMenu?: () => void;
  rightAction?: {
    icon: string;
    onPress: () => void;
  };
}

export const OptimizedNavigation = React.memo<NavigationProps>(({
  title,
  onBack,
  onMenu,
  rightAction
}) => {
  const handleBackPress = useCallback(() => {
    onBack?.();
  }, [onBack]);

  const handleMenuPress = useCallback(() => {
    onMenu?.();
  }, [onMenu]);

  const handleRightAction = useCallback(() => {
    rightAction?.onPress();
  }, [rightAction]);

  const headerStyle = useMemo(() => [
    styles.header,
    { justifyContent: onBack ? 'space-between' : 'center' }
  ], [onBack]);

  return (
    <View style={headerStyle}>
      {onBack && (
        <TouchableOpacity onPress={handleBackPress} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#007AFF" />
        </TouchableOpacity>
      )}
      
      <Text style={styles.title}>{title}</Text>
      
      <View style={styles.rightActions}>
        {rightAction && (
          <TouchableOpacity onPress={handleRightAction} style={styles.actionButton}>
            <Ionicons name={rightAction.icon as any} size={24} color="#007AFF" />
          </TouchableOpacity>
        )}
        {onMenu && (
          <TouchableOpacity onPress={handleMenuPress} style={styles.actionButton}>
            <Ionicons name="menu" size={24} color="#007AFF" />
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
});

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  backButton: {
    padding: 8,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#000000',
  },
  rightActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionButton: {
    padding: 8,
    marginLeft: 8,
  },
}); 