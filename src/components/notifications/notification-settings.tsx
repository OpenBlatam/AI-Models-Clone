/**
 * @fileoverview Component for managing notification settings
 * @author Blaze AI Team
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Switch,
  ScrollView,
  Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNotifications } from '../../hooks/notifications/use-notifications';
import { AccessibleButton } from '../accessibility/accessible-button';
import { NotificationSettings } from '../../lib/notifications/notification-types';

interface NotificationSettingsProps {
  readonly onBack?: () => void;
}

/**
 * Component for managing notification preferences
 */
export function NotificationSettingsComponent({
  onBack
}: NotificationSettingsProps): React.JSX.Element {
  const { settings, updateSettings, clearBadge, setBadgeCount } = useNotifications();
  const [localSettings, setLocalSettings] = useState<NotificationSettings>(settings);

  /**
   * Updates a specific setting
   */
  const updateSetting = <K extends keyof NotificationSettings>(
    key: K,
    value: NotificationSettings[K]
  ): void => {
    const newSettings = { ...localSettings, [key]: value };
    setLocalSettings(newSettings);
    updateSettings(newSettings);
  };

  /**
   * Toggles notification channel
   */
  const toggleChannel = (channelId: string): void => {
    const currentChannels = localSettings.channels;
    const newChannels = currentChannels.includes(channelId)
      ? currentChannels.filter(id => id !== channelId)
      : [...currentChannels, channelId];
    
    updateSetting('channels', newChannels);
  };

  /**
   * Toggles quiet hours
   */
  const toggleQuietHours = (): void => {
    updateSetting('quietHours', {
      ...localSettings.quietHours,
      enabled: !localSettings.quietHours.enabled
    });
  };

  /**
   * Updates quiet hours time
   */
  const updateQuietHoursTime = (field: 'start' | 'end', time: string): void => {
    updateSetting('quietHours', {
      ...localSettings.quietHours,
      [field]: time
    });
  };

  /**
   * Tests notification
   */
  const testNotification = async (): Promise<void> => {
    try {
      await setBadgeCount(1);
      Alert.alert(
        'Test Notification',
        'A test notification has been sent. Check your notification panel.',
        [{ text: 'OK' }]
      );
    } catch (error) {
      Alert.alert(
        'Error',
        'Failed to send test notification. Please check your permissions.',
        [{ text: 'OK' }]
      );
    }
  };

  /**
   * Clears all notifications
   */
  const clearAllNotifications = async (): Promise<void> => {
    try {
      await clearBadge();
      Alert.alert(
        'Notifications Cleared',
        'All notification badges have been cleared.',
        [{ text: 'OK' }]
      );
    } catch (error) {
      Alert.alert(
        'Error',
        'Failed to clear notifications.',
        [{ text: 'OK' }]
      );
    }
  };

  const channels = [
    { id: 'general', name: 'General', description: 'App updates and general information' },
    { id: 'urgent', name: 'Urgent', description: 'Important alerts and urgent messages' },
    { id: 'marketing', name: 'Marketing', description: 'Promotional content and offers' }
  ];

  const categories = [
    { id: 'message', name: 'Messages', description: 'Chat and message notifications' },
    { id: 'reminder', name: 'Reminders', description: 'Task and appointment reminders' }
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.title}>Notification Settings</Text>
          {onBack && (
            <AccessibleButton
              title="Back"
              onPress={onBack}
              variant="secondary"
              style={styles.backButton}
            />
          )}
        </View>

        {/* General Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>General</Text>
          
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Enable Notifications</Text>
              <Text style={styles.settingDescription}>
                Allow the app to send you notifications
              </Text>
            </View>
            <Switch
              value={localSettings.enabled}
              onValueChange={(value) => updateSetting('enabled', value)}
              accessibilityLabel="Enable notifications"
              accessibilityHint="Toggle to enable or disable all notifications"
            />
          </View>
        </View>

        {/* Notification Channels */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Notification Types</Text>
          {channels.map(channel => (
            <View key={channel.id} style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingLabel}>{channel.name}</Text>
                <Text style={styles.settingDescription}>{channel.description}</Text>
              </View>
              <Switch
                value={localSettings.channels.includes(channel.id)}
                onValueChange={() => toggleChannel(channel.id)}
                disabled={!localSettings.enabled}
                accessibilityLabel={`Enable ${channel.name} notifications`}
                accessibilityHint={`Toggle to enable or disable ${channel.name} notifications`}
              />
            </View>
          ))}
        </View>

        {/* Quiet Hours */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quiet Hours</Text>
          
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Enable Quiet Hours</Text>
              <Text style={styles.settingDescription}>
                Pause notifications during specified hours
              </Text>
            </View>
            <Switch
              value={localSettings.quietHours.enabled}
              onValueChange={toggleQuietHours}
              disabled={!localSettings.enabled}
              accessibilityLabel="Enable quiet hours"
              accessibilityHint="Toggle to enable or disable quiet hours"
            />
          </View>

          {localSettings.quietHours.enabled && (
            <View style={styles.quietHoursContainer}>
              <View style={styles.timeRow}>
                <Text style={styles.timeLabel}>Start Time</Text>
                <Text style={styles.timeValue}>{localSettings.quietHours.start}</Text>
              </View>
              <View style={styles.timeRow}>
                <Text style={styles.timeLabel}>End Time</Text>
                <Text style={styles.timeValue}>{localSettings.quietHours.end}</Text>
              </View>
            </View>
          )}
        </View>

        {/* Notification Categories */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Categories</Text>
          {categories.map(category => (
            <View key={category.id} style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingLabel}>{category.name}</Text>
                <Text style={styles.settingDescription}>{category.description}</Text>
              </View>
              <Switch
                value={localSettings.categories.includes(category.id)}
                onValueChange={() => {
                  const newCategories = localSettings.categories.includes(category.id)
                    ? localSettings.categories.filter(id => id !== category.id)
                    : [...localSettings.categories, category.id];
                  updateSetting('categories', newCategories);
                }}
                disabled={!localSettings.enabled}
                accessibilityLabel={`Enable ${category.name} notifications`}
                accessibilityHint={`Toggle to enable or disable ${category.name} notifications`}
              />
            </View>
          ))}
        </View>

        {/* Test Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Test</Text>
          
          <AccessibleButton
            title="Send Test Notification"
            onPress={testNotification}
            variant="secondary"
            style={styles.testButton}
            accessibilityLabel="Send a test notification"
            accessibilityHint="Double tap to send a test notification"
          />
          
          <AccessibleButton
            title="Clear All Notifications"
            onPress={clearAllNotifications}
            variant="secondary"
            style={styles.testButton}
            accessibilityLabel="Clear all notification badges"
            accessibilityHint="Double tap to clear all notification badges"
          />
        </View>
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937'
  },
  backButton: {
    paddingHorizontal: 16,
    paddingVertical: 8
  },
  section: {
    paddingHorizontal: 20,
    paddingVertical: 16
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 16
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6'
  },
  settingInfo: {
    flex: 1,
    marginRight: 16
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1F2937',
    marginBottom: 4
  },
  settingDescription: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20
  },
  quietHoursContainer: {
    marginTop: 12,
    paddingLeft: 16,
    borderLeftWidth: 2,
    borderLeftColor: '#E5E7EB'
  },
  timeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8
  },
  timeLabel: {
    fontSize: 14,
    color: '#6B7280'
  },
  timeValue: {
    fontSize: 14,
    fontWeight: '500',
    color: '#1F2937'
  },
  testButton: {
    marginBottom: 12,
    paddingVertical: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#D1D5DB'
  }
});
 * @fileoverview Component for managing notification settings
 * @author Blaze AI Team
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Switch,
  ScrollView,
  Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNotifications } from '../../hooks/notifications/use-notifications';
import { AccessibleButton } from '../accessibility/accessible-button';
import { NotificationSettings } from '../../lib/notifications/notification-types';

interface NotificationSettingsProps {
  readonly onBack?: () => void;
}

/**
 * Component for managing notification preferences
 */
export function NotificationSettingsComponent({
  onBack
}: NotificationSettingsProps): React.JSX.Element {
  const { settings, updateSettings, clearBadge, setBadgeCount } = useNotifications();
  const [localSettings, setLocalSettings] = useState<NotificationSettings>(settings);

  /**
   * Updates a specific setting
   */
  const updateSetting = <K extends keyof NotificationSettings>(
    key: K,
    value: NotificationSettings[K]
  ): void => {
    const newSettings = { ...localSettings, [key]: value };
    setLocalSettings(newSettings);
    updateSettings(newSettings);
  };

  /**
   * Toggles notification channel
   */
  const toggleChannel = (channelId: string): void => {
    const currentChannels = localSettings.channels;
    const newChannels = currentChannels.includes(channelId)
      ? currentChannels.filter(id => id !== channelId)
      : [...currentChannels, channelId];
    
    updateSetting('channels', newChannels);
  };

  /**
   * Toggles quiet hours
   */
  const toggleQuietHours = (): void => {
    updateSetting('quietHours', {
      ...localSettings.quietHours,
      enabled: !localSettings.quietHours.enabled
    });
  };

  /**
   * Updates quiet hours time
   */
  const updateQuietHoursTime = (field: 'start' | 'end', time: string): void => {
    updateSetting('quietHours', {
      ...localSettings.quietHours,
      [field]: time
    });
  };

  /**
   * Tests notification
   */
  const testNotification = async (): Promise<void> => {
    try {
      await setBadgeCount(1);
      Alert.alert(
        'Test Notification',
        'A test notification has been sent. Check your notification panel.',
        [{ text: 'OK' }]
      );
    } catch (error) {
      Alert.alert(
        'Error',
        'Failed to send test notification. Please check your permissions.',
        [{ text: 'OK' }]
      );
    }
  };

  /**
   * Clears all notifications
   */
  const clearAllNotifications = async (): Promise<void> => {
    try {
      await clearBadge();
      Alert.alert(
        'Notifications Cleared',
        'All notification badges have been cleared.',
        [{ text: 'OK' }]
      );
    } catch (error) {
      Alert.alert(
        'Error',
        'Failed to clear notifications.',
        [{ text: 'OK' }]
      );
    }
  };

  const channels = [
    { id: 'general', name: 'General', description: 'App updates and general information' },
    { id: 'urgent', name: 'Urgent', description: 'Important alerts and urgent messages' },
    { id: 'marketing', name: 'Marketing', description: 'Promotional content and offers' }
  ];

  const categories = [
    { id: 'message', name: 'Messages', description: 'Chat and message notifications' },
    { id: 'reminder', name: 'Reminders', description: 'Task and appointment reminders' }
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.title}>Notification Settings</Text>
          {onBack && (
            <AccessibleButton
              title="Back"
              onPress={onBack}
              variant="secondary"
              style={styles.backButton}
            />
          )}
        </View>

        {/* General Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>General</Text>
          
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Enable Notifications</Text>
              <Text style={styles.settingDescription}>
                Allow the app to send you notifications
              </Text>
            </View>
            <Switch
              value={localSettings.enabled}
              onValueChange={(value) => updateSetting('enabled', value)}
              accessibilityLabel="Enable notifications"
              accessibilityHint="Toggle to enable or disable all notifications"
            />
          </View>
        </View>

        {/* Notification Channels */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Notification Types</Text>
          {channels.map(channel => (
            <View key={channel.id} style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingLabel}>{channel.name}</Text>
                <Text style={styles.settingDescription}>{channel.description}</Text>
              </View>
              <Switch
                value={localSettings.channels.includes(channel.id)}
                onValueChange={() => toggleChannel(channel.id)}
                disabled={!localSettings.enabled}
                accessibilityLabel={`Enable ${channel.name} notifications`}
                accessibilityHint={`Toggle to enable or disable ${channel.name} notifications`}
              />
            </View>
          ))}
        </View>

        {/* Quiet Hours */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quiet Hours</Text>
          
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Enable Quiet Hours</Text>
              <Text style={styles.settingDescription}>
                Pause notifications during specified hours
              </Text>
            </View>
            <Switch
              value={localSettings.quietHours.enabled}
              onValueChange={toggleQuietHours}
              disabled={!localSettings.enabled}
              accessibilityLabel="Enable quiet hours"
              accessibilityHint="Toggle to enable or disable quiet hours"
            />
          </View>

          {localSettings.quietHours.enabled && (
            <View style={styles.quietHoursContainer}>
              <View style={styles.timeRow}>
                <Text style={styles.timeLabel}>Start Time</Text>
                <Text style={styles.timeValue}>{localSettings.quietHours.start}</Text>
              </View>
              <View style={styles.timeRow}>
                <Text style={styles.timeLabel}>End Time</Text>
                <Text style={styles.timeValue}>{localSettings.quietHours.end}</Text>
              </View>
            </View>
          )}
        </View>

        {/* Notification Categories */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Categories</Text>
          {categories.map(category => (
            <View key={category.id} style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingLabel}>{category.name}</Text>
                <Text style={styles.settingDescription}>{category.description}</Text>
              </View>
              <Switch
                value={localSettings.categories.includes(category.id)}
                onValueChange={() => {
                  const newCategories = localSettings.categories.includes(category.id)
                    ? localSettings.categories.filter(id => id !== category.id)
                    : [...localSettings.categories, category.id];
                  updateSetting('categories', newCategories);
                }}
                disabled={!localSettings.enabled}
                accessibilityLabel={`Enable ${category.name} notifications`}
                accessibilityHint={`Toggle to enable or disable ${category.name} notifications`}
              />
            </View>
          ))}
        </View>

        {/* Test Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Test</Text>
          
          <AccessibleButton
            title="Send Test Notification"
            onPress={testNotification}
            variant="secondary"
            style={styles.testButton}
            accessibilityLabel="Send a test notification"
            accessibilityHint="Double tap to send a test notification"
          />
          
          <AccessibleButton
            title="Clear All Notifications"
            onPress={clearAllNotifications}
            variant="secondary"
            style={styles.testButton}
            accessibilityLabel="Clear all notification badges"
            accessibilityHint="Double tap to clear all notification badges"
          />
        </View>
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937'
  },
  backButton: {
    paddingHorizontal: 16,
    paddingVertical: 8
  },
  section: {
    paddingHorizontal: 20,
    paddingVertical: 16
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 16
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6'
  },
  settingInfo: {
    flex: 1,
    marginRight: 16
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1F2937',
    marginBottom: 4
  },
  settingDescription: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20
  },
  quietHoursContainer: {
    marginTop: 12,
    paddingLeft: 16,
    borderLeftWidth: 2,
    borderLeftColor: '#E5E7EB'
  },
  timeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8
  },
  timeLabel: {
    fontSize: 14,
    color: '#6B7280'
  },
  timeValue: {
    fontSize: 14,
    fontWeight: '500',
    color: '#1F2937'
  },
  testButton: {
    marginBottom: 12,
    paddingVertical: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#D1D5DB'
  }
});


