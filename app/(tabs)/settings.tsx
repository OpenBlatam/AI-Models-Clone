import React, { useCallback, useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Switch,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

interface SettingItem {
  id: string;
  title: string;
  subtitle?: string;
  type: 'toggle' | 'navigation' | 'action';
  icon: string;
  value?: boolean;
  onPress?: () => void;
}

const SettingsSection: React.FC<{ 
  title: string; 
  children: React.ReactNode;
}> = React.memo(({ title, children }) => (
  <View style={styles.section}>
    <Text style={styles.sectionTitle}>{title}</Text>
    {children}
  </View>
));

const SettingItem: React.FC<{ 
  item: SettingItem; 
  onToggle?: (value: boolean) => void;
}> = React.memo(({ item, onToggle }) => (
  <TouchableOpacity 
    style={styles.settingItem} 
    onPress={item.onPress}
    disabled={item.type === 'toggle'}
  >
    <View style={styles.settingIcon}>
      <Ionicons name={item.icon as any} size={24} color="#007AFF" />
    </View>
    <View style={styles.settingContent}>
      <Text style={styles.settingTitle}>{item.title}</Text>
      {item.subtitle && (
        <Text style={styles.settingSubtitle}>{item.subtitle}</Text>
      )}
    </View>
    {item.type === 'toggle' ? (
      <Switch
        value={item.value}
        onValueChange={onToggle}
        trackColor={{ false: '#E5E5EA', true: '#007AFF' }}
        thumbColor="#FFFFFF"
      />
    ) : (
      <Ionicons name="chevron-forward" size={16} color="#C7C7CC" />
    )}
  </TouchableOpacity>
));

export default function SettingsScreen() {
  const router = useRouter();
  const [settings, setSettings] = useState({
    notifications: true,
    darkMode: false,
    autoSave: true,
    locationServices: false,
  });

  const handleToggleSetting = useCallback((key: keyof typeof settings, value: boolean) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  }, []);

  const handleAccountSettings = useCallback(() => {
    router.push('/profile/edit');
  }, [router]);

  const handlePrivacySettings = useCallback(() => {
    router.push('/settings/privacy');
  }, [router]);

  const handleSecuritySettings = useCallback(() => {
    router.push('/settings/security');
  }, [router]);

  const handleHelpSupport = useCallback(() => {
    Alert.alert('Help & Support', 'Help and support functionality would be implemented here');
  }, []);

  const handleAboutApp = useCallback(() => {
    Alert.alert('About App', 'App version 1.0.0\nReact Native with Expo Router');
  }, []);

  const handleClearCache = useCallback(() => {
    Alert.alert(
      'Clear Cache',
      'Are you sure you want to clear the app cache?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Clear', 
          style: 'destructive',
          onPress: () => {
            // Clear cache logic would go here
            Alert.alert('Success', 'Cache cleared successfully');
          }
        },
      ]
    );
  }, []);

  const handleLogout = useCallback(() => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Logout', 
          style: 'destructive',
          onPress: () => {
            // Logout logic would go here
            router.replace('/(auth)/login');
          }
        },
      ]
    );
  }, [router]);

  const notificationSettings: SettingItem[] = [
    {
      id: 'notifications',
      title: 'Push Notifications',
      subtitle: 'Receive notifications for new posts and updates',
      type: 'toggle',
      icon: 'notifications-outline',
      value: settings.notifications,
    },
    {
      id: 'darkMode',
      title: 'Dark Mode',
      subtitle: 'Use dark theme throughout the app',
      type: 'toggle',
      icon: 'moon-outline',
      value: settings.darkMode,
    },
  ];

  const accountSettings: SettingItem[] = [
    {
      id: 'account',
      title: 'Account Settings',
      subtitle: 'Manage your account information',
      type: 'navigation',
      icon: 'person-outline',
      onPress: handleAccountSettings,
    },
    {
      id: 'privacy',
      title: 'Privacy',
      subtitle: 'Control your privacy settings',
      type: 'navigation',
      icon: 'shield-outline',
      onPress: handlePrivacySettings,
    },
    {
      id: 'security',
      title: 'Security',
      subtitle: 'Manage your security settings',
      type: 'navigation',
      icon: 'lock-closed-outline',
      onPress: handleSecuritySettings,
    },
  ];

  const appSettings: SettingItem[] = [
    {
      id: 'autoSave',
      title: 'Auto Save',
      subtitle: 'Automatically save drafts',
      type: 'toggle',
      icon: 'save-outline',
      value: settings.autoSave,
    },
    {
      id: 'locationServices',
      title: 'Location Services',
      subtitle: 'Allow app to access your location',
      type: 'toggle',
      icon: 'location-outline',
      value: settings.locationServices,
    },
  ];

  const supportSettings: SettingItem[] = [
    {
      id: 'help',
      title: 'Help & Support',
      subtitle: 'Get help and contact support',
      type: 'action',
      icon: 'help-circle-outline',
      onPress: handleHelpSupport,
    },
    {
      id: 'about',
      title: 'About App',
      subtitle: 'App version and information',
      type: 'action',
      icon: 'information-circle-outline',
      onPress: handleAboutApp,
    },
    {
      id: 'clearCache',
      title: 'Clear Cache',
      subtitle: 'Free up storage space',
      type: 'action',
      icon: 'trash-outline',
      onPress: handleClearCache,
    },
  ];

  const accountActions: SettingItem[] = [
    {
      id: 'logout',
      title: 'Logout',
      subtitle: 'Sign out of your account',
      type: 'action',
      icon: 'log-out-outline',
      onPress: handleLogout,
    },
  ];

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <SettingsSection title="Notifications & Appearance">
        {notificationSettings.map(item => (
          <SettingItem
            key={item.id}
            item={item}
            onToggle={(value) => handleToggleSetting(item.id as keyof typeof settings, value)}
          />
        ))}
      </SettingsSection>

      <SettingsSection title="Account">
        {accountSettings.map(item => (
          <SettingItem key={item.id} item={item} />
        ))}
      </SettingsSection>

      <SettingsSection title="App Settings">
        {appSettings.map(item => (
          <SettingItem
            key={item.id}
            item={item}
            onToggle={(value) => handleToggleSetting(item.id as keyof typeof settings, value)}
          />
        ))}
      </SettingsSection>

      <SettingsSection title="Support">
        {supportSettings.map(item => (
          <SettingItem key={item.id} item={item} />
        ))}
      </SettingsSection>

      <SettingsSection title="Account Actions">
        {accountActions.map(item => (
          <SettingItem key={item.id} item={item} />
        ))}
      </SettingsSection>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  section: {
    marginTop: 20,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#8E8E93',
    marginBottom: 8,
    marginLeft: 16,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  },
  settingIcon: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: '#F2F2F7',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  settingContent: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    color: '#000000',
    marginBottom: 2,
  },
  settingSubtitle: {
    fontSize: 14,
    color: '#8E8E93',
  },
}); 