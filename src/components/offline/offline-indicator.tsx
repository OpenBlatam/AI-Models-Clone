import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { useOfflineSync } from '../../hooks/offline/use-offline-sync';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';

const { width: screenWidth } = Dimensions.get('window');

interface OfflineIndicatorProps {
  showDetails?: boolean;
  onPress?: () => void;
  testID?: string;
}

export function OfflineIndicator({ 
  showDetails = false, 
  onPress,
  testID 
}: OfflineIndicatorProps) {
  const { theme } = useAppStore();
  const { t } = useI18n();
  const { 
    isOnline, 
    isSyncing, 
    pendingActions, 
    failedActions, 
    syncProgress,
    hasConflicts,
    sync,
    forceSync 
  } = useOfflineSync();

  const [slideAnim] = useState(new Animated.Value(-100));
  const [pulseAnim] = useState(new Animated.Value(1));

  useEffect(() => {
    if (!isOnline) {
      // Slide in when offline
      Animated.spring(slideAnim, {
        toValue: 0,
        useNativeDriver: true,
        tension: 100,
        friction: 8,
      }).start();
    } else {
      // Slide out when online
      Animated.spring(slideAnim, {
        toValue: -100,
        useNativeDriver: true,
        tension: 100,
        friction: 8,
      }).start();
    }
  }, [isOnline, slideAnim]);

  useEffect(() => {
    if (isSyncing) {
      // Pulse animation during sync
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.1,
            duration: 500,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 500,
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      pulseAnim.setValue(1);
    }
  }, [isSyncing, pulseAnim]);

  const handlePress = () => {
    if (onPress) {
      onPress();
    } else if (!isOnline) {
      // Default action: try to sync
      forceSync();
    }
  };

  const getStatusText = () => {
    if (!isOnline) {
      return t('offline.disconnected');
    }
    if (isSyncing) {
      return t('offline.syncing');
    }
    if (hasConflicts) {
      return t('offline.conflicts');
    }
    if (pendingActions > 0) {
      return t('offline.pending', { count: pendingActions });
    }
    return t('offline.connected');
  };

  const getStatusColor = () => {
    if (!isOnline) {
      return theme.colors.error;
    }
    if (isSyncing) {
      return theme.colors.warning;
    }
    if (hasConflicts) {
      return theme.colors.error;
    }
    if (pendingActions > 0) {
      return theme.colors.warning;
    }
    return theme.colors.success;
  };

  const getStatusIcon = () => {
    if (!isOnline) {
      return '📡';
    }
    if (isSyncing) {
      return '🔄';
    }
    if (hasConflicts) {
      return '⚠️';
    }
    if (pendingActions > 0) {
      return '⏳';
    }
    return '✅';
  };

  if (isOnline && pendingActions === 0 && !hasConflicts) {
    return null;
  }

  return (
    <Animated.View
      testID={testID}
      style={[
        styles.container,
        {
          backgroundColor: getStatusColor(),
          transform: [
            { translateY: slideAnim },
            { scale: pulseAnim },
          ],
        },
      ]}
    >
      <TouchableOpacity
        style={styles.content}
        onPress={handlePress}
        activeOpacity={0.8}
      >
        <View style={styles.statusRow}>
          <Text style={styles.icon}>{getStatusIcon()}</Text>
          <Text style={styles.statusText}>{getStatusText()}</Text>
          {isSyncing && (
            <Text style={styles.progressText}>
              {Math.round(syncProgress)}%
            </Text>
          )}
        </View>

        {showDetails && (
          <View style={styles.detailsRow}>
            {pendingActions > 0 && (
              <Text style={styles.detailText}>
                {t('offline.pendingActions', { count: pendingActions })}
              </Text>
            )}
            {failedActions > 0 && (
              <Text style={styles.detailText}>
                {t('offline.failedActions', { count: failedActions })}
              </Text>
            )}
            {hasConflicts && (
              <Text style={styles.detailText}>
                {t('offline.conflictsDetected')}
              </Text>
            )}
          </View>
        )}

        {isSyncing && (
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                { width: `${syncProgress}%` },
              ]}
            />
          </View>
        )}
      </TouchableOpacity>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1000,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  content: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    paddingTop: 50, // Account for status bar
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  icon: {
    fontSize: 16,
    marginRight: 8,
  },
  statusText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
    flex: 1,
    textAlign: 'center',
  },
  progressText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '500',
  },
  detailsRow: {
    marginTop: 4,
    alignItems: 'center',
  },
  detailText: {
    color: 'white',
    fontSize: 12,
    opacity: 0.9,
  },
  progressBar: {
    height: 2,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    borderRadius: 1,
    marginTop: 8,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: 'white',
    borderRadius: 1,
  },
});
import {
  View,
  Text,
  StyleSheet,
  Animated,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { useOfflineSync } from '../../hooks/offline/use-offline-sync';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';

const { width: screenWidth } = Dimensions.get('window');

interface OfflineIndicatorProps {
  showDetails?: boolean;
  onPress?: () => void;
  testID?: string;
}

export function OfflineIndicator({ 
  showDetails = false, 
  onPress,
  testID 
}: OfflineIndicatorProps) {
  const { theme } = useAppStore();
  const { t } = useI18n();
  const { 
    isOnline, 
    isSyncing, 
    pendingActions, 
    failedActions, 
    syncProgress,
    hasConflicts,
    sync,
    forceSync 
  } = useOfflineSync();

  const [slideAnim] = useState(new Animated.Value(-100));
  const [pulseAnim] = useState(new Animated.Value(1));

  useEffect(() => {
    if (!isOnline) {
      // Slide in when offline
      Animated.spring(slideAnim, {
        toValue: 0,
        useNativeDriver: true,
        tension: 100,
        friction: 8,
      }).start();
    } else {
      // Slide out when online
      Animated.spring(slideAnim, {
        toValue: -100,
        useNativeDriver: true,
        tension: 100,
        friction: 8,
      }).start();
    }
  }, [isOnline, slideAnim]);

  useEffect(() => {
    if (isSyncing) {
      // Pulse animation during sync
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.1,
            duration: 500,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 500,
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      pulseAnim.setValue(1);
    }
  }, [isSyncing, pulseAnim]);

  const handlePress = () => {
    if (onPress) {
      onPress();
    } else if (!isOnline) {
      // Default action: try to sync
      forceSync();
    }
  };

  const getStatusText = () => {
    if (!isOnline) {
      return t('offline.disconnected');
    }
    if (isSyncing) {
      return t('offline.syncing');
    }
    if (hasConflicts) {
      return t('offline.conflicts');
    }
    if (pendingActions > 0) {
      return t('offline.pending', { count: pendingActions });
    }
    return t('offline.connected');
  };

  const getStatusColor = () => {
    if (!isOnline) {
      return theme.colors.error;
    }
    if (isSyncing) {
      return theme.colors.warning;
    }
    if (hasConflicts) {
      return theme.colors.error;
    }
    if (pendingActions > 0) {
      return theme.colors.warning;
    }
    return theme.colors.success;
  };

  const getStatusIcon = () => {
    if (!isOnline) {
      return '📡';
    }
    if (isSyncing) {
      return '🔄';
    }
    if (hasConflicts) {
      return '⚠️';
    }
    if (pendingActions > 0) {
      return '⏳';
    }
    return '✅';
  };

  if (isOnline && pendingActions === 0 && !hasConflicts) {
    return null;
  }

  return (
    <Animated.View
      testID={testID}
      style={[
        styles.container,
        {
          backgroundColor: getStatusColor(),
          transform: [
            { translateY: slideAnim },
            { scale: pulseAnim },
          ],
        },
      ]}
    >
      <TouchableOpacity
        style={styles.content}
        onPress={handlePress}
        activeOpacity={0.8}
      >
        <View style={styles.statusRow}>
          <Text style={styles.icon}>{getStatusIcon()}</Text>
          <Text style={styles.statusText}>{getStatusText()}</Text>
          {isSyncing && (
            <Text style={styles.progressText}>
              {Math.round(syncProgress)}%
            </Text>
          )}
        </View>

        {showDetails && (
          <View style={styles.detailsRow}>
            {pendingActions > 0 && (
              <Text style={styles.detailText}>
                {t('offline.pendingActions', { count: pendingActions })}
              </Text>
            )}
            {failedActions > 0 && (
              <Text style={styles.detailText}>
                {t('offline.failedActions', { count: failedActions })}
              </Text>
            )}
            {hasConflicts && (
              <Text style={styles.detailText}>
                {t('offline.conflictsDetected')}
              </Text>
            )}
          </View>
        )}

        {isSyncing && (
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                { width: `${syncProgress}%` },
              ]}
            />
          </View>
        )}
      </TouchableOpacity>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1000,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  content: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    paddingTop: 50, // Account for status bar
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  icon: {
    fontSize: 16,
    marginRight: 8,
  },
  statusText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
    flex: 1,
    textAlign: 'center',
  },
  progressText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '500',
  },
  detailsRow: {
    marginTop: 4,
    alignItems: 'center',
  },
  detailText: {
    color: 'white',
    fontSize: 12,
    opacity: 0.9,
  },
  progressBar: {
    height: 2,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    borderRadius: 1,
    marginTop: 8,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: 'white',
    borderRadius: 1,
  },
});


