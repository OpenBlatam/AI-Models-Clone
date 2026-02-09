/**
 * @fileoverview Comprehensive notification system demo
 * @author Blaze AI Team
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNotifications } from '../../hooks/notifications/use-notifications';
import { DeepLinkHandler } from '../../lib/deep-linking/deep-link-handler';
import { AccessibleButton } from '../accessibility/accessible-button';
import { NotificationPermissionRequest } from '../notifications/notification-permission-request';
import { NotificationSettingsComponent } from '../notifications/notification-settings';
import { NotificationPayload, DeepLinkData } from '../../lib/notifications/notification-types';

interface NotificationDemoProps {
  readonly onNavigate?: (route: string, params?: Record<string, string>) => void;
}

/**
 * Comprehensive demo of the notification system
 */
export function NotificationDemo({
  onNavigate
}: NotificationDemoProps): React.JSX.Element {
  const {
    isInitialized,
    permissionStatus,
    notificationToken,
    settings,
    lastNotification,
    requestPermissions,
    scheduleNotification,
    cancelAllNotifications,
    setBadgeCount,
    clearBadge
  } = useNotifications();

  const [showPermissionRequest, setShowPermissionRequest] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [scheduledNotifications, setScheduledNotifications] = useState<string[]>([]);

  const deepLinkHandler = new DeepLinkHandler();

  /**
   * Handles deep link navigation
   */
  const handleDeepLink = (deepLinkData: DeepLinkData): void => {
    deepLinkHandler.handleDeepLink(deepLinkData).then(success => {
      if (success && onNavigate) {
        onNavigate(deepLinkData.route, deepLinkData.params);
      }
    });
  };

  /**
   * Schedules a test notification
   */
  const scheduleTestNotification = async (type: 'immediate' | 'delayed' | 'repeating'): Promise<void> => {
    try {
      const payload: NotificationPayload = {
        title: 'Test Notification',
        body: `This is a ${type} test notification`,
        data: {
          type: 'test',
          route: 'home',
          params: JSON.stringify({ source: 'demo' })
        },
        category: 'message'
      };

      let trigger;
      switch (type) {
        case 'immediate':
          trigger = null; // Immediate
          break;
        case 'delayed':
          trigger = { seconds: 5 }; // 5 seconds delay
          break;
        case 'repeating':
          trigger = { seconds: 10, repeats: true }; // Every 10 seconds
          break;
      }

      const notificationId = await scheduleNotification(payload, trigger);
      setScheduledNotifications(prev => [...prev, notificationId]);
      
      Alert.alert(
        'Notification Scheduled',
        `A ${type} notification has been scheduled.`,
        [{ text: 'OK' }]
      );
    } catch (error) {
      Alert.alert(
        'Error',
        'Failed to schedule notification. Please check permissions.',
        [{ text: 'OK' }]
      );
    }
  };

  /**
   * Tests badge count
   */
  const testBadgeCount = async (): Promise<void> => {
    try {
      await setBadgeCount(5);
      Alert.alert(
        'Badge Set',
        'App badge has been set to 5.',
        [{ text: 'OK' }]
      );
    } catch (error) {
      Alert.alert(
        'Error',
        'Failed to set badge count.',
        [{ text: 'OK' }]
      );
    }
  };

  /**
   * Clears badge
   */
  const clearBadgeCount = async (): Promise<void> => {
    try {
      await clearBadge();
      Alert.alert(
        'Badge Cleared',
        'App badge has been cleared.',
        [{ text: 'OK' }]
      );
    } catch (error) {
      Alert.alert(
        'Error',
        'Failed to clear badge.',
        [{ text: 'OK' }]
      );
    }
  };

  /**
   * Cancels all notifications
   */
  const cancelAllScheduledNotifications = async (): Promise<void> => {
    try {
      await cancelAllNotifications();
      setScheduledNotifications([]);
      Alert.alert(
        'Notifications Cancelled',
        'All scheduled notifications have been cancelled.',
        [{ text: 'OK' }]
      );
    } catch (error) {
      Alert.alert(
        'Error',
        'Failed to cancel notifications.',
        [{ text: 'OK' }]
      );
    }
  };

  /**
   * Tests deep linking
   */
  const testDeepLink = async (route: string): Promise<void> => {
    const deepLinkData: DeepLinkData = {
      route,
      params: { id: '123', source: 'demo' },
      timestamp: Date.now()
    };

    const success = await deepLinkHandler.handleDeepLink(deepLinkData);
    if (success) {
      Alert.alert(
        'Deep Link Test',
        `Successfully handled deep link to ${route}`,
        [{ text: 'OK' }]
      );
    } else {
      Alert.alert(
        'Deep Link Test',
        `Failed to handle deep link to ${route}`,
        [{ text: 'OK' }]
      );
    }
  };

  // Show permission request if not granted
  useEffect(() => {
    if (isInitialized && permissionStatus && !permissionStatus.granted) {
      setShowPermissionRequest(true);
    }
  }, [isInitialized, permissionStatus]);

  if (showPermissionRequest) {
    return (
      <NotificationPermissionRequest
        onPermissionGranted={() => setShowPermissionRequest(false)}
        onPermissionDenied={() => setShowPermissionRequest(false)}
        onSkip={() => setShowPermissionRequest(false)}
      />
    );
  }

  if (showSettings) {
    return (
      <NotificationSettingsComponent
        onBack={() => setShowSettings(false)}
      />
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.title}>Notification System Demo</Text>
          <Text style={styles.subtitle}>
            Comprehensive push notification and deep linking system
          </Text>
        </View>

        {/* Status Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Status</Text>
          
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Initialized:</Text>
            <Text style={[styles.statusValue, { color: isInitialized ? '#10B981' : '#EF4444' }]}>
              {isInitialized ? 'Yes' : 'No'}
            </Text>
          </View>
          
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Permissions:</Text>
            <Text style={[styles.statusValue, { 
              color: permissionStatus?.granted ? '#10B981' : '#EF4444' 
            }]}>
              {permissionStatus?.status || 'Unknown'}
            </Text>
          </View>
          
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Token:</Text>
            <Text style={styles.statusValue}>
              {notificationToken ? 'Available' : 'Not Available'}
            </Text>
          </View>
          
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Scheduled:</Text>
            <Text style={styles.statusValue}>
              {scheduledNotifications.length} notifications
            </Text>
          </View>
        </View>

        {/* Notification Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Test Notifications</Text>
          
          <AccessibleButton
            title="Immediate Notification"
            onPress={() => scheduleTestNotification('immediate')}
            style={styles.actionButton}
            accessibilityLabel="Schedule an immediate test notification"
          />
          
          <AccessibleButton
            title="Delayed Notification (5s)"
            onPress={() => scheduleTestNotification('delayed')}
            style={styles.actionButton}
            accessibilityLabel="Schedule a delayed test notification"
          />
          
          <AccessibleButton
            title="Repeating Notification (10s)"
            onPress={() => scheduleTestNotification('repeating')}
            style={styles.actionButton}
            accessibilityLabel="Schedule a repeating test notification"
          />
          
          <AccessibleButton
            title="Cancel All Notifications"
            onPress={cancelAllScheduledNotifications}
            variant="secondary"
            style={styles.actionButton}
            accessibilityLabel="Cancel all scheduled notifications"
          />
        </View>

        {/* Badge Management */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Badge Management</Text>
          
          <AccessibleButton
            title="Set Badge to 5"
            onPress={testBadgeCount}
            style={styles.actionButton}
            accessibilityLabel="Set app badge count to 5"
          />
          
          <AccessibleButton
            title="Clear Badge"
            onPress={clearBadgeCount}
            variant="secondary"
            style={styles.actionButton}
            accessibilityLabel="Clear app badge count"
          />
        </View>

        {/* Deep Link Testing */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Deep Link Testing</Text>
          
          <AccessibleButton
            title="Test Home Deep Link"
            onPress={() => testDeepLink('home')}
            style={styles.actionButton}
            accessibilityLabel="Test deep link to home screen"
          />
          
          <AccessibleButton
            title="Test Profile Deep Link"
            onPress={() => testDeepLink('profile')}
            style={styles.actionButton}
            accessibilityLabel="Test deep link to profile screen"
          />
          
          <AccessibleButton
            title="Test Chat Deep Link"
            onPress={() => testDeepLink('chat')}
            style={styles.actionButton}
            accessibilityLabel="Test deep link to chat screen"
          />
          
          <AccessibleButton
            title="Test Product Deep Link"
            onPress={() => testDeepLink('product')}
            style={styles.actionButton}
            accessibilityLabel="Test deep link to product screen"
          />
        </View>

        {/* Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Settings</Text>
          
          <AccessibleButton
            title="Notification Settings"
            onPress={() => setShowSettings(true)}
            variant="secondary"
            style={styles.actionButton}
            accessibilityLabel="Open notification settings"
          />
          
          <AccessibleButton
            title="Request Permissions"
            onPress={requestPermissions}
            variant="secondary"
            style={styles.actionButton}
            accessibilityLabel="Request notification permissions"
          />
        </View>

        {/* Last Notification */}
        {lastNotification && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Last Notification</Text>
            <View style={styles.notificationCard}>
              <Text style={styles.notificationTitle}>
                {lastNotification.payload.title}
              </Text>
              <Text style={styles.notificationBody}>
                {lastNotification.payload.body}
              </Text>
              <Text style={styles.notificationType}>
                Type: {lastNotification.type}
              </Text>
              {lastNotification.deepLinkData && (
                <Text style={styles.notificationRoute}>
                  Route: {lastNotification.deepLinkData.route}
                </Text>
              )}
            </View>
          </View>
        )}

        {/* Token Display */}
        {notificationToken && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Push Token</Text>
            <View style={styles.tokenContainer}>
              <Text style={styles.tokenText} numberOfLines={3}>
                {notificationToken.token}
              </Text>
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF'
  },
  scrollView: {
    flex: 1
  },
  header: {
    paddingHorizontal: 20,
    paddingVertical: 24,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB'
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    lineHeight: 24
  },
  section: {
    paddingHorizontal: 20,
    paddingVertical: 16
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 16
  },
  statusItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6'
  },
  statusLabel: {
    fontSize: 16,
    color: '#374151',
    fontWeight: '500'
  },
  statusValue: {
    fontSize: 16,
    color: '#1F2937',
    fontWeight: '600'
  },
  actionButton: {
    marginBottom: 12,
    paddingVertical: 14,
    borderRadius: 10
  },
  notificationCard: {
    backgroundColor: '#F9FAFB',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB'
  },
  notificationTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4
  },
  notificationBody: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 8
  },
  notificationType: {
    fontSize: 12,
    color: '#9CA3AF',
    marginBottom: 4
  },
  notificationRoute: {
    fontSize: 12,
    color: '#9CA3AF'
  },
  tokenContainer: {
    backgroundColor: '#F3F4F6',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#D1D5DB'
  },
  tokenText: {
    fontSize: 12,
    color: '#374151',
    fontFamily: 'monospace'
  }
});
 * @fileoverview Comprehensive notification system demo
 * @author Blaze AI Team
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNotifications } from '../../hooks/notifications/use-notifications';
import { DeepLinkHandler } from '../../lib/deep-linking/deep-link-handler';
import { AccessibleButton } from '../accessibility/accessible-button';
import { NotificationPermissionRequest } from '../notifications/notification-permission-request';
import { NotificationSettingsComponent } from '../notifications/notification-settings';
import { NotificationPayload, DeepLinkData } from '../../lib/notifications/notification-types';

interface NotificationDemoProps {
  readonly onNavigate?: (route: string, params?: Record<string, string>) => void;
}

/**
 * Comprehensive demo of the notification system
 */
export function NotificationDemo({
  onNavigate
}: NotificationDemoProps): React.JSX.Element {
  const {
    isInitialized,
    permissionStatus,
    notificationToken,
    settings,
    lastNotification,
    requestPermissions,
    scheduleNotification,
    cancelAllNotifications,
    setBadgeCount,
    clearBadge
  } = useNotifications();

  const [showPermissionRequest, setShowPermissionRequest] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [scheduledNotifications, setScheduledNotifications] = useState<string[]>([]);

  const deepLinkHandler = new DeepLinkHandler();

  /**
   * Handles deep link navigation
   */
  const handleDeepLink = (deepLinkData: DeepLinkData): void => {
    deepLinkHandler.handleDeepLink(deepLinkData).then(success => {
      if (success && onNavigate) {
        onNavigate(deepLinkData.route, deepLinkData.params);
      }
    });
  };

  /**
   * Schedules a test notification
   */
  const scheduleTestNotification = async (type: 'immediate' | 'delayed' | 'repeating'): Promise<void> => {
    try {
      const payload: NotificationPayload = {
        title: 'Test Notification',
        body: `This is a ${type} test notification`,
        data: {
          type: 'test',
          route: 'home',
          params: JSON.stringify({ source: 'demo' })
        },
        category: 'message'
      };

      let trigger;
      switch (type) {
        case 'immediate':
          trigger = null; // Immediate
          break;
        case 'delayed':
          trigger = { seconds: 5 }; // 5 seconds delay
          break;
        case 'repeating':
          trigger = { seconds: 10, repeats: true }; // Every 10 seconds
          break;
      }

      const notificationId = await scheduleNotification(payload, trigger);
      setScheduledNotifications(prev => [...prev, notificationId]);
      
      Alert.alert(
        'Notification Scheduled',
        `A ${type} notification has been scheduled.`,
        [{ text: 'OK' }]
      );
    } catch (error) {
      Alert.alert(
        'Error',
        'Failed to schedule notification. Please check permissions.',
        [{ text: 'OK' }]
      );
    }
  };

  /**
   * Tests badge count
   */
  const testBadgeCount = async (): Promise<void> => {
    try {
      await setBadgeCount(5);
      Alert.alert(
        'Badge Set',
        'App badge has been set to 5.',
        [{ text: 'OK' }]
      );
    } catch (error) {
      Alert.alert(
        'Error',
        'Failed to set badge count.',
        [{ text: 'OK' }]
      );
    }
  };

  /**
   * Clears badge
   */
  const clearBadgeCount = async (): Promise<void> => {
    try {
      await clearBadge();
      Alert.alert(
        'Badge Cleared',
        'App badge has been cleared.',
        [{ text: 'OK' }]
      );
    } catch (error) {
      Alert.alert(
        'Error',
        'Failed to clear badge.',
        [{ text: 'OK' }]
      );
    }
  };

  /**
   * Cancels all notifications
   */
  const cancelAllScheduledNotifications = async (): Promise<void> => {
    try {
      await cancelAllNotifications();
      setScheduledNotifications([]);
      Alert.alert(
        'Notifications Cancelled',
        'All scheduled notifications have been cancelled.',
        [{ text: 'OK' }]
      );
    } catch (error) {
      Alert.alert(
        'Error',
        'Failed to cancel notifications.',
        [{ text: 'OK' }]
      );
    }
  };

  /**
   * Tests deep linking
   */
  const testDeepLink = async (route: string): Promise<void> => {
    const deepLinkData: DeepLinkData = {
      route,
      params: { id: '123', source: 'demo' },
      timestamp: Date.now()
    };

    const success = await deepLinkHandler.handleDeepLink(deepLinkData);
    if (success) {
      Alert.alert(
        'Deep Link Test',
        `Successfully handled deep link to ${route}`,
        [{ text: 'OK' }]
      );
    } else {
      Alert.alert(
        'Deep Link Test',
        `Failed to handle deep link to ${route}`,
        [{ text: 'OK' }]
      );
    }
  };

  // Show permission request if not granted
  useEffect(() => {
    if (isInitialized && permissionStatus && !permissionStatus.granted) {
      setShowPermissionRequest(true);
    }
  }, [isInitialized, permissionStatus]);

  if (showPermissionRequest) {
    return (
      <NotificationPermissionRequest
        onPermissionGranted={() => setShowPermissionRequest(false)}
        onPermissionDenied={() => setShowPermissionRequest(false)}
        onSkip={() => setShowPermissionRequest(false)}
      />
    );
  }

  if (showSettings) {
    return (
      <NotificationSettingsComponent
        onBack={() => setShowSettings(false)}
      />
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.title}>Notification System Demo</Text>
          <Text style={styles.subtitle}>
            Comprehensive push notification and deep linking system
          </Text>
        </View>

        {/* Status Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Status</Text>
          
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Initialized:</Text>
            <Text style={[styles.statusValue, { color: isInitialized ? '#10B981' : '#EF4444' }]}>
              {isInitialized ? 'Yes' : 'No'}
            </Text>
          </View>
          
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Permissions:</Text>
            <Text style={[styles.statusValue, { 
              color: permissionStatus?.granted ? '#10B981' : '#EF4444' 
            }]}>
              {permissionStatus?.status || 'Unknown'}
            </Text>
          </View>
          
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Token:</Text>
            <Text style={styles.statusValue}>
              {notificationToken ? 'Available' : 'Not Available'}
            </Text>
          </View>
          
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Scheduled:</Text>
            <Text style={styles.statusValue}>
              {scheduledNotifications.length} notifications
            </Text>
          </View>
        </View>

        {/* Notification Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Test Notifications</Text>
          
          <AccessibleButton
            title="Immediate Notification"
            onPress={() => scheduleTestNotification('immediate')}
            style={styles.actionButton}
            accessibilityLabel="Schedule an immediate test notification"
          />
          
          <AccessibleButton
            title="Delayed Notification (5s)"
            onPress={() => scheduleTestNotification('delayed')}
            style={styles.actionButton}
            accessibilityLabel="Schedule a delayed test notification"
          />
          
          <AccessibleButton
            title="Repeating Notification (10s)"
            onPress={() => scheduleTestNotification('repeating')}
            style={styles.actionButton}
            accessibilityLabel="Schedule a repeating test notification"
          />
          
          <AccessibleButton
            title="Cancel All Notifications"
            onPress={cancelAllScheduledNotifications}
            variant="secondary"
            style={styles.actionButton}
            accessibilityLabel="Cancel all scheduled notifications"
          />
        </View>

        {/* Badge Management */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Badge Management</Text>
          
          <AccessibleButton
            title="Set Badge to 5"
            onPress={testBadgeCount}
            style={styles.actionButton}
            accessibilityLabel="Set app badge count to 5"
          />
          
          <AccessibleButton
            title="Clear Badge"
            onPress={clearBadgeCount}
            variant="secondary"
            style={styles.actionButton}
            accessibilityLabel="Clear app badge count"
          />
        </View>

        {/* Deep Link Testing */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Deep Link Testing</Text>
          
          <AccessibleButton
            title="Test Home Deep Link"
            onPress={() => testDeepLink('home')}
            style={styles.actionButton}
            accessibilityLabel="Test deep link to home screen"
          />
          
          <AccessibleButton
            title="Test Profile Deep Link"
            onPress={() => testDeepLink('profile')}
            style={styles.actionButton}
            accessibilityLabel="Test deep link to profile screen"
          />
          
          <AccessibleButton
            title="Test Chat Deep Link"
            onPress={() => testDeepLink('chat')}
            style={styles.actionButton}
            accessibilityLabel="Test deep link to chat screen"
          />
          
          <AccessibleButton
            title="Test Product Deep Link"
            onPress={() => testDeepLink('product')}
            style={styles.actionButton}
            accessibilityLabel="Test deep link to product screen"
          />
        </View>

        {/* Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Settings</Text>
          
          <AccessibleButton
            title="Notification Settings"
            onPress={() => setShowSettings(true)}
            variant="secondary"
            style={styles.actionButton}
            accessibilityLabel="Open notification settings"
          />
          
          <AccessibleButton
            title="Request Permissions"
            onPress={requestPermissions}
            variant="secondary"
            style={styles.actionButton}
            accessibilityLabel="Request notification permissions"
          />
        </View>

        {/* Last Notification */}
        {lastNotification && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Last Notification</Text>
            <View style={styles.notificationCard}>
              <Text style={styles.notificationTitle}>
                {lastNotification.payload.title}
              </Text>
              <Text style={styles.notificationBody}>
                {lastNotification.payload.body}
              </Text>
              <Text style={styles.notificationType}>
                Type: {lastNotification.type}
              </Text>
              {lastNotification.deepLinkData && (
                <Text style={styles.notificationRoute}>
                  Route: {lastNotification.deepLinkData.route}
                </Text>
              )}
            </View>
          </View>
        )}

        {/* Token Display */}
        {notificationToken && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Push Token</Text>
            <View style={styles.tokenContainer}>
              <Text style={styles.tokenText} numberOfLines={3}>
                {notificationToken.token}
              </Text>
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF'
  },
  scrollView: {
    flex: 1
  },
  header: {
    paddingHorizontal: 20,
    paddingVertical: 24,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB'
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    lineHeight: 24
  },
  section: {
    paddingHorizontal: 20,
    paddingVertical: 16
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 16
  },
  statusItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6'
  },
  statusLabel: {
    fontSize: 16,
    color: '#374151',
    fontWeight: '500'
  },
  statusValue: {
    fontSize: 16,
    color: '#1F2937',
    fontWeight: '600'
  },
  actionButton: {
    marginBottom: 12,
    paddingVertical: 14,
    borderRadius: 10
  },
  notificationCard: {
    backgroundColor: '#F9FAFB',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB'
  },
  notificationTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4
  },
  notificationBody: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 8
  },
  notificationType: {
    fontSize: 12,
    color: '#9CA3AF',
    marginBottom: 4
  },
  notificationRoute: {
    fontSize: 12,
    color: '#9CA3AF'
  },
  tokenContainer: {
    backgroundColor: '#F3F4F6',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#D1D5DB'
  },
  tokenText: {
    fontSize: 12,
    color: '#374151',
    fontFamily: 'monospace'
  }
});


