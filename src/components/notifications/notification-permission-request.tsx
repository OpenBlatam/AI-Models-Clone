/**
 * @fileoverview Component for requesting notification permissions
 * @author Blaze AI Team
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Linking
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNotifications } from '../../hooks/notifications/use-notifications';
import { AccessibleButton } from '../accessibility/accessible-button';

interface NotificationPermissionRequestProps {
  readonly onPermissionGranted?: () => void;
  readonly onPermissionDenied?: () => void;
  readonly showSkipOption?: boolean;
  readonly onSkip?: () => void;
}

/**
 * Component for requesting notification permissions with user-friendly UI
 */
export function NotificationPermissionRequest({
  onPermissionGranted,
  onPermissionDenied,
  showSkipOption = true,
  onSkip
}: NotificationPermissionRequestProps): React.JSX.Element {
  const { requestPermissions, permissionStatus } = useNotifications();
  const [isRequesting, setIsRequesting] = useState(false);

  /**
   * Handles permission request
   */
  const handleRequestPermissions = async (): Promise<void> => {
    setIsRequesting(true);
    
    try {
      const result = await requestPermissions();
      
      if (result.granted) {
        onPermissionGranted?.();
      } else {
        if (result.canAskAgain) {
          Alert.alert(
            'Permission Required',
            'Notifications help keep you updated with important information. You can enable them later in Settings.',
            [
              { text: 'Cancel', style: 'cancel', onPress: onPermissionDenied },
              { text: 'Open Settings', onPress: openAppSettings }
            ]
          );
        } else {
          Alert.alert(
            'Permission Denied',
            'Notifications are disabled. You can enable them in your device Settings.',
            [
              { text: 'Cancel', style: 'cancel', onPress: onPermissionDenied },
              { text: 'Open Settings', onPress: openAppSettings }
            ]
          );
        }
      }
    } catch (error) {
      console.error('Failed to request permissions:', error);
      Alert.alert(
        'Error',
        'Failed to request notification permissions. Please try again.',
        [{ text: 'OK', onPress: onPermissionDenied }]
      );
    } finally {
      setIsRequesting(false);
    }
  };

  /**
   * Opens app settings
   */
  const openAppSettings = (): void => {
    Linking.openSettings().catch(error => {
      console.error('Failed to open settings:', error);
    });
  };

  /**
   * Handles skip action
   */
  const handleSkip = (): void => {
    onSkip?.();
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.iconContainer}>
          <Text style={styles.icon}>🔔</Text>
        </View>
        
        <Text style={styles.title}>
          Stay Updated
        </Text>
        
        <Text style={styles.description}>
          Get notified about important updates, messages, and reminders. 
          You can customize these settings anytime.
        </Text>
        
        <View style={styles.benefitsContainer}>
          <View style={styles.benefitItem}>
            <Text style={styles.benefitIcon}>📱</Text>
            <Text style={styles.benefitText}>
              Instant notifications for new messages
            </Text>
          </View>
          
          <View style={styles.benefitItem}>
            <Text style={styles.benefitIcon}>⏰</Text>
            <Text style={styles.benefitText}>
              Reminders for important tasks
            </Text>
          </View>
          
          <View style={styles.benefitItem}>
            <Text style={styles.benefitIcon}>🔒</Text>
            <Text style={styles.benefitText}>
              Secure and private notifications
            </Text>
          </View>
        </View>
        
        <View style={styles.buttonContainer}>
          <AccessibleButton
            title="Enable Notifications"
            onPress={handleRequestPermissions}
            disabled={isRequesting}
            loading={isRequesting}
            style={styles.primaryButton}
            accessibilityLabel="Enable push notifications for this app"
            accessibilityHint="Double tap to allow notifications"
          />
          
          {showSkipOption && (
            <AccessibleButton
              title="Skip for Now"
              onPress={handleSkip}
              variant="secondary"
              style={styles.secondaryButton}
              accessibilityLabel="Skip enabling notifications"
              accessibilityHint="Double tap to continue without notifications"
            />
          )}
        </View>
        
        {permissionStatus && !permissionStatus.granted && (
          <Text style={styles.statusText}>
            Current status: {permissionStatus.status}
          </Text>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF'
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
    paddingVertical: 32,
    justifyContent: 'center',
    alignItems: 'center'
  },
  iconContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24
  },
  icon: {
    fontSize: 32
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    textAlign: 'center',
    marginBottom: 16
  },
  description: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32
  },
  benefitsContainer: {
    width: '100%',
    marginBottom: 40
  },
  benefitItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    paddingHorizontal: 16
  },
  benefitIcon: {
    fontSize: 20,
    marginRight: 12,
    width: 24,
    textAlign: 'center'
  },
  benefitText: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
    lineHeight: 20
  },
  buttonContainer: {
    width: '100%',
    gap: 12
  },
  primaryButton: {
    backgroundColor: '#3B82F6',
    paddingVertical: 16,
    borderRadius: 12
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    paddingVertical: 16,
    borderRadius: 12
  },
  statusText: {
    fontSize: 12,
    color: '#9CA3AF',
    textAlign: 'center',
    marginTop: 16
  }
});
 * @fileoverview Component for requesting notification permissions
 * @author Blaze AI Team
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Linking
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNotifications } from '../../hooks/notifications/use-notifications';
import { AccessibleButton } from '../accessibility/accessible-button';

interface NotificationPermissionRequestProps {
  readonly onPermissionGranted?: () => void;
  readonly onPermissionDenied?: () => void;
  readonly showSkipOption?: boolean;
  readonly onSkip?: () => void;
}

/**
 * Component for requesting notification permissions with user-friendly UI
 */
export function NotificationPermissionRequest({
  onPermissionGranted,
  onPermissionDenied,
  showSkipOption = true,
  onSkip
}: NotificationPermissionRequestProps): React.JSX.Element {
  const { requestPermissions, permissionStatus } = useNotifications();
  const [isRequesting, setIsRequesting] = useState(false);

  /**
   * Handles permission request
   */
  const handleRequestPermissions = async (): Promise<void> => {
    setIsRequesting(true);
    
    try {
      const result = await requestPermissions();
      
      if (result.granted) {
        onPermissionGranted?.();
      } else {
        if (result.canAskAgain) {
          Alert.alert(
            'Permission Required',
            'Notifications help keep you updated with important information. You can enable them later in Settings.',
            [
              { text: 'Cancel', style: 'cancel', onPress: onPermissionDenied },
              { text: 'Open Settings', onPress: openAppSettings }
            ]
          );
        } else {
          Alert.alert(
            'Permission Denied',
            'Notifications are disabled. You can enable them in your device Settings.',
            [
              { text: 'Cancel', style: 'cancel', onPress: onPermissionDenied },
              { text: 'Open Settings', onPress: openAppSettings }
            ]
          );
        }
      }
    } catch (error) {
      console.error('Failed to request permissions:', error);
      Alert.alert(
        'Error',
        'Failed to request notification permissions. Please try again.',
        [{ text: 'OK', onPress: onPermissionDenied }]
      );
    } finally {
      setIsRequesting(false);
    }
  };

  /**
   * Opens app settings
   */
  const openAppSettings = (): void => {
    Linking.openSettings().catch(error => {
      console.error('Failed to open settings:', error);
    });
  };

  /**
   * Handles skip action
   */
  const handleSkip = (): void => {
    onSkip?.();
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.iconContainer}>
          <Text style={styles.icon}>🔔</Text>
        </View>
        
        <Text style={styles.title}>
          Stay Updated
        </Text>
        
        <Text style={styles.description}>
          Get notified about important updates, messages, and reminders. 
          You can customize these settings anytime.
        </Text>
        
        <View style={styles.benefitsContainer}>
          <View style={styles.benefitItem}>
            <Text style={styles.benefitIcon}>📱</Text>
            <Text style={styles.benefitText}>
              Instant notifications for new messages
            </Text>
          </View>
          
          <View style={styles.benefitItem}>
            <Text style={styles.benefitIcon}>⏰</Text>
            <Text style={styles.benefitText}>
              Reminders for important tasks
            </Text>
          </View>
          
          <View style={styles.benefitItem}>
            <Text style={styles.benefitIcon}>🔒</Text>
            <Text style={styles.benefitText}>
              Secure and private notifications
            </Text>
          </View>
        </View>
        
        <View style={styles.buttonContainer}>
          <AccessibleButton
            title="Enable Notifications"
            onPress={handleRequestPermissions}
            disabled={isRequesting}
            loading={isRequesting}
            style={styles.primaryButton}
            accessibilityLabel="Enable push notifications for this app"
            accessibilityHint="Double tap to allow notifications"
          />
          
          {showSkipOption && (
            <AccessibleButton
              title="Skip for Now"
              onPress={handleSkip}
              variant="secondary"
              style={styles.secondaryButton}
              accessibilityLabel="Skip enabling notifications"
              accessibilityHint="Double tap to continue without notifications"
            />
          )}
        </View>
        
        {permissionStatus && !permissionStatus.granted && (
          <Text style={styles.statusText}>
            Current status: {permissionStatus.status}
          </Text>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF'
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
    paddingVertical: 32,
    justifyContent: 'center',
    alignItems: 'center'
  },
  iconContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24
  },
  icon: {
    fontSize: 32
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    textAlign: 'center',
    marginBottom: 16
  },
  description: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32
  },
  benefitsContainer: {
    width: '100%',
    marginBottom: 40
  },
  benefitItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    paddingHorizontal: 16
  },
  benefitIcon: {
    fontSize: 20,
    marginRight: 12,
    width: 24,
    textAlign: 'center'
  },
  benefitText: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
    lineHeight: 20
  },
  buttonContainer: {
    width: '100%',
    gap: 12
  },
  primaryButton: {
    backgroundColor: '#3B82F6',
    paddingVertical: 16,
    borderRadius: 12
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    paddingVertical: 16,
    borderRadius: 12
  },
  statusText: {
    fontSize: 12,
    color: '#9CA3AF',
    textAlign: 'center',
    marginTop: 16
  }
});


