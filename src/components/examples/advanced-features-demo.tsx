import React, { useState, useCallback, useMemo, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Alert,
  useWindowDimensions,
  Platform,
  Linking,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useColorScheme } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { AnimatedCard } from '../advanced/animated-card';
import { OptimizedImage, AvatarImage, CardImage } from '../optimized/optimized-image';
import { AccessibleButton } from '../accessibility/accessible-button';
import { useAppStore, useAuth, useTheme } from '../../store/app-store';
import { useOptimizedPerformance } from '../../hooks/performance/use-optimized-performance';
import { useTranslation } from '../../lib/i18n/i18n-config';
import { 
  initializeDeepLinking, 
  registerDeepLinkHandler, 
  generateDeepLink,
  navigateToScreen,
  shareScreen,
} from '../../lib/navigation/deep-linking';
import { 
  initializeSentry, 
  trackScreen, 
  trackUserAction, 
  captureMessage,
  setUser,
} from '../../lib/monitoring/sentry-config';
import { 
  initializePermissions, 
  requestPermission, 
  isPermissionGranted,
  getPermissionGroups,
} from '../../lib/permissions/permissions-manager';
import { 
  initializeOTAUpdates, 
  checkForUpdates, 
  getUpdateInfo,
  isUpdateEnabled,
} from '../../lib/updates/ota-updates';
import { 
  LazyDashboardScreen, 
  LazyProfileScreen, 
  preloadMainComponents,
} from '../../lib/code-splitting/lazy-components';

// ============================================================================
// TYPES
// ============================================================================

interface FeatureDemo {
  id: string;
  title: string;
  description: string;
  icon: keyof typeof Ionicons.glyphMap;
  onPress: () => void;
  isEnabled: boolean;
}

interface SystemInfo {
  platform: string;
  version: string;
  screenSize: string;
  isDarkMode: boolean;
  locale: string;
  updateEnabled: boolean;
  permissions: string[];
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function AdvancedFeaturesDemo(): JSX.Element {
  const { width, height } = useWindowDimensions();
  const colorScheme = useColorScheme();
  const { t } = useTranslation();
  const { isDarkMode, effectiveTheme } = useTheme();
  const { user, isAuthenticated } = useAuth();
  
  const {
    metrics,
    optimization,
    trackRender,
    trackInteraction,
    endInteraction,
  } = useOptimizedPerformance({
    enableRenderTracking: true,
    enableFPSTracking: true,
    enableInteractionTracking: true,
  });

  const [systemInfo, setSystemInfo] = useState<SystemInfo>({
    platform: Platform.OS,
    version: Platform.Version.toString(),
    screenSize: `${width} × ${height}`,
    isDarkMode,
    locale: t('locale'),
    updateEnabled: false,
    permissions: [],
  });

  const [isLoading, setIsLoading] = useState(false);

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  useEffect(() => {
    const initializeFeatures = async () => {
      try {
        setIsLoading(true);

        // Initialize deep linking
        initializeDeepLinking();
        registerDeepLinkHandler('/demo', (params) => {
          Alert.alert('Deep Link Received', `Demo screen opened with params: ${JSON.stringify(params)}`);
        });

        // Initialize Sentry
        initializeSentry();
        if (user) {
          setUser({
            id: user.id,
            email: user.email,
            username: user.username,
            role: user.role,
          });
        }

        // Initialize permissions
        await initializePermissions();
        const permissionGroups = getPermissionGroups();
        setSystemInfo(prev => ({
          ...prev,
          permissions: permissionGroups.map(group => group.name),
        }));

        // Initialize OTA updates
        await initializeOTAUpdates({
          checkOnLaunch: true,
          autoDownload: true,
          requireUserConsent: true,
        });
        setSystemInfo(prev => ({
          ...prev,
          updateEnabled: isUpdateEnabled(),
        }));

        // Track screen
        trackScreen('AdvancedFeaturesDemo');

        setIsLoading(false);
      } catch (error) {
        console.error('Error initializing features:', error);
        setIsLoading(false);
      }
    };

    initializeFeatures();
  }, [user, t, isDarkMode, width, height]);

  // ============================================================================
  // FEATURE DEMOS
  // ============================================================================

  const featureDemos: FeatureDemo[] = useMemo(() => [
    {
      id: 'deep-linking',
      title: 'Deep Linking',
      description: 'Test deep linking and universal links',
      icon: 'link-outline',
      onPress: handleDeepLinkingDemo,
      isEnabled: true,
    },
    {
      id: 'image-optimization',
      title: 'Image Optimization',
      description: 'WebP support and lazy loading',
      icon: 'image-outline',
      onPress: handleImageOptimizationDemo,
      isEnabled: true,
    },
    {
      id: 'code-splitting',
      title: 'Code Splitting',
      description: 'Lazy loading with React Suspense',
      icon: 'code-slash-outline',
      onPress: handleCodeSplittingDemo,
      isEnabled: true,
    },
    {
      id: 'permissions',
      title: 'Permissions',
      description: 'Device permissions management',
      icon: 'shield-checkmark-outline',
      onPress: handlePermissionsDemo,
      isEnabled: true,
    },
    {
      id: 'ota-updates',
      title: 'OTA Updates',
      description: 'Over-the-air updates',
      icon: 'cloud-download-outline',
      onPress: handleOTAUpdatesDemo,
      isEnabled: systemInfo.updateEnabled,
    },
    {
      id: 'sentry-monitoring',
      title: 'Error Monitoring',
      description: 'Sentry integration for error tracking',
      icon: 'bug-outline',
      onPress: handleSentryDemo,
      isEnabled: true,
    },
    {
      id: 'performance',
      title: 'Performance',
      description: 'Real-time performance monitoring',
      icon: 'speedometer-outline',
      onPress: handlePerformanceDemo,
      isEnabled: true,
    },
    {
      id: 'animations',
      title: 'Animations',
      description: 'Advanced animations with Reanimated',
      icon: 'flash-outline',
      onPress: handleAnimationsDemo,
      isEnabled: true,
    },
  ], [systemInfo.updateEnabled]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleDeepLinkingDemo = useCallback(async () => {
    const interaction = trackInteraction('deep_linking_demo');
    
    try {
      const deepLink = generateDeepLink('demo', { feature: 'deep_linking' });
      await shareScreen('demo', { feature: 'deep_linking' });
      
      Alert.alert(
        'Deep Link Generated',
        `Deep link: ${deepLink}\n\nThis link can be shared and will open the app directly to this screen.`,
        [
          { text: 'OK' },
          { 
            text: 'Copy Link', 
            onPress: () => {
              // In a real app, you'd copy to clipboard
              console.log('Deep link copied:', deepLink);
            }
          }
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to generate deep link');
    } finally {
      endInteraction(interaction);
    }
  }, [trackInteraction, endInteraction]);

  const handleImageOptimizationDemo = useCallback(() => {
    const interaction = trackInteraction('image_optimization_demo');
    
    Alert.alert(
      'Image Optimization',
      'The images below demonstrate:\n\n• WebP format support\n• Lazy loading\n• Responsive sizing\n• Error handling\n• Caching strategies',
      [{ text: 'OK' }]
    );
    
    endInteraction(interaction);
  }, [trackInteraction, endInteraction]);

  const handleCodeSplittingDemo = useCallback(async () => {
    const interaction = trackInteraction('code_splitting_demo');
    
    try {
      Alert.alert(
        'Code Splitting',
        'Preloading main components...',
        [{ text: 'OK' }]
      );
      
      await preloadMainComponents();
      
      Alert.alert(
        'Success',
        'Main components have been preloaded successfully!'
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to preload components');
    } finally {
      endInteraction(interaction);
    }
  }, [trackInteraction, endInteraction]);

  const handlePermissionsDemo = useCallback(async () => {
    const interaction = trackInteraction('permissions_demo');
    
    try {
      const result = await requestPermission({
        permission: 'camera',
        rationale: 'Camera access is needed to demonstrate the permissions system.',
        onGranted: () => {
          Alert.alert('Success', 'Camera permission granted!');
        },
        onDenied: () => {
          Alert.alert('Permission Denied', 'Camera permission was denied.');
        },
        onBlocked: () => {
          Alert.alert('Permission Blocked', 'Camera permission is blocked. Please enable it in settings.');
        },
      });
      
      console.log('Permission result:', result);
    } catch (error) {
      Alert.alert('Error', 'Failed to request permission');
    } finally {
      endInteraction(interaction);
    }
  }, [trackInteraction, endInteraction]);

  const handleOTAUpdatesDemo = useCallback(async () => {
    const interaction = trackInteraction('ota_updates_demo');
    
    try {
      const updateInfo = await getUpdateInfo();
      
      if (updateInfo.isAvailable) {
        Alert.alert(
          'Update Available',
          `A new update is available!\n\nVersion: ${updateInfo.manifest?.version || 'Unknown'}\nDescription: ${updateInfo.manifest?.description || 'Bug fixes and improvements'}`,
          [
            { text: 'Later' },
            { 
              text: 'Check for Updates', 
              onPress: async () => {
                const result = await checkForUpdates();
                if (result.isAvailable) {
                  Alert.alert('Update Found', 'A new update is available for download.');
                } else {
                  Alert.alert('No Updates', 'You are running the latest version.');
                }
              }
            }
          ]
        );
      } else {
        Alert.alert('No Updates', 'You are running the latest version.');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to check for updates');
    } finally {
      endInteraction(interaction);
    }
  }, [trackInteraction, endInteraction]);

  const handleSentryDemo = useCallback(() => {
    const interaction = trackInteraction('sentry_demo');
    
    try {
      // Simulate an error for testing
      throw new Error('This is a test error for Sentry monitoring');
    } catch (error) {
      captureMessage('Sentry demo error captured', 'error', {
        feature: 'sentry_demo',
        timestamp: new Date().toISOString(),
      });
      
      Alert.alert(
        'Error Captured',
        'A test error has been captured and sent to Sentry for monitoring.',
        [{ text: 'OK' }]
      );
    } finally {
      endInteraction(interaction);
    }
  }, [trackInteraction, endInteraction]);

  const handlePerformanceDemo = useCallback(() => {
    const interaction = trackInteraction('performance_demo');
    
    Alert.alert(
      'Performance Metrics',
      `Current Performance:\n\n• Renders: ${metrics.renderCount}\n• Avg Render Time: ${metrics.averageRenderTime.toFixed(2)}ms\n• FPS: ${metrics.fps || 'N/A'}\n• Interactions: ${metrics.interactionCount}\n\nOptimization Level: ${optimization.optimizationLevel.toUpperCase()}`,
      [{ text: 'OK' }]
    );
    
    endInteraction(interaction);
  }, [trackInteraction, endInteraction, metrics, optimization]);

  const handleAnimationsDemo = useCallback(() => {
    const interaction = trackInteraction('animations_demo');
    
    Alert.alert(
      'Animations Demo',
      'The cards below demonstrate advanced animations:\n\n• Spring animations\n• Gesture handling\n• Hover effects\n• Press animations\n• Swipe gestures',
      [{ text: 'OK' }]
    );
    
    endInteraction(interaction);
  }, [trackInteraction, endInteraction]);

  // ============================================================================
  // RENDER TRACKING
  // ============================================================================
  
  useEffect(() => {
    trackRender();
  });

  // ============================================================================
  // RENDER
  // ============================================================================

  const styles = createStyles(isDarkMode, width, height);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView 
        style={styles.scrollView} 
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Advanced Features Demo</Text>
          <Text style={styles.subtitle}>
            Demonstrating all the advanced features and optimizations
          </Text>
        </View>

        {/* System Information */}
        <AnimatedCard
          title="System Information"
          subtitle="Current device and app status"
          icon="information-circle-outline"
          variant="elevated"
          size="medium"
          style={styles.infoCard}
        >
          <View style={styles.systemInfo}>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Platform:</Text>
              <Text style={styles.infoValue}>{systemInfo.platform} {systemInfo.version}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Screen:</Text>
              <Text style={styles.infoValue}>{systemInfo.screenSize}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Theme:</Text>
              <Text style={styles.infoValue}>{systemInfo.isDarkMode ? 'Dark' : 'Light'}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Locale:</Text>
              <Text style={styles.infoValue}>{systemInfo.locale}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>OTA Updates:</Text>
              <Text style={styles.infoValue}>{systemInfo.updateEnabled ? 'Enabled' : 'Disabled'}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Permissions:</Text>
              <Text style={styles.infoValue}>{systemInfo.permissions.length} groups</Text>
            </View>
          </View>
        </AnimatedCard>

        {/* Feature Demos */}
        <View style={styles.featuresSection}>
          <Text style={styles.sectionTitle}>Feature Demonstrations</Text>
          
          {featureDemos.map((feature) => (
            <AnimatedCard
              key={feature.id}
              title={feature.title}
              description={feature.description}
              icon={feature.icon}
              variant="outlined"
              size="medium"
              onPress={feature.onPress}
              enablePress={feature.isEnabled}
              enableLongPress={true}
              enableSwipe={true}
              style={[
                styles.featureCard,
                !feature.isEnabled && styles.disabledCard,
              ]}
            >
              <View style={styles.featureFooter}>
                <Text style={[
                  styles.featureStatus,
                  feature.isEnabled ? styles.enabledStatus : styles.disabledStatus,
                ]}>
                  {feature.isEnabled ? 'Enabled' : 'Disabled'}
                </Text>
                <Ionicons
                  name={feature.isEnabled ? 'checkmark-circle' : 'close-circle'}
                  size={16}
                  color={feature.isEnabled ? '#34C759' : '#FF3B30'}
                />
              </View>
            </AnimatedCard>
          ))}
        </View>

        {/* Image Optimization Demo */}
        <View style={styles.imagesSection}>
          <Text style={styles.sectionTitle}>Image Optimization</Text>
          
          <View style={styles.imageGrid}>
            <AvatarImage
              source="https://picsum.photos/200/200?random=1"
              width={80}
              height={80}
              placeholder="https://via.placeholder.com/80x80/007AFF/FFFFFF?text=Avatar"
              fallback="https://via.placeholder.com/80x80/FF3B30/FFFFFF?text=Error"
              enableWebP={true}
              quality={0.8}
              accessibilityLabel="Sample avatar image"
            />
            
            <CardImage
              source="https://picsum.photos/300/200?random=2"
              width={150}
              height={100}
              placeholder="https://via.placeholder.com/150x100/007AFF/FFFFFF?text=Loading"
              fallback="https://via.placeholder.com/150x100/FF3B30/FFFFFF?text=Error"
              enableWebP={true}
              quality={0.9}
              accessibilityLabel="Sample card image"
            />
            
            <OptimizedImage
              source="https://picsum.photos/200/150?random=3"
              width={120}
              height={90}
              placeholder="https://via.placeholder.com/120x90/007AFF/FFFFFF?text=Loading"
              fallback="https://via.placeholder.com/120x90/FF3B30/FFFFFF?text=Error"
              enableWebP={true}
              quality={0.7}
              fadeInDuration={500}
              scaleInDuration={300}
              accessibilityLabel="Sample optimized image"
            />
          </View>
        </View>

        {/* Performance Metrics */}
        <AnimatedCard
          title="Performance Metrics"
          subtitle="Real-time performance monitoring"
          icon="speedometer-outline"
          variant="filled"
          size="large"
          style={styles.performanceCard}
        >
          <View style={styles.metricsGrid}>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>Renders</Text>
              <Text style={styles.metricValue}>{metrics.renderCount}</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>Avg Render Time</Text>
              <Text style={styles.metricValue}>{metrics.averageRenderTime.toFixed(2)}ms</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>FPS</Text>
              <Text style={styles.metricValue}>{metrics.fps || 'N/A'}</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>Interactions</Text>
              <Text style={styles.metricValue}>{metrics.interactionCount}</Text>
            </View>
          </View>
          
          {optimization.shouldOptimize && (
            <View style={styles.optimizationWarning}>
              <Text style={styles.warningText}>
                Optimization Level: {optimization.optimizationLevel.toUpperCase()}
              </Text>
              {optimization.criticalIssues.length > 0 && (
                <Text style={styles.criticalText}>
                  Critical Issues: {optimization.criticalIssues.join(', ')}
                </Text>
              )}
            </View>
          )}
        </AnimatedCard>

        {/* Loading State */}
        {isLoading && (
          <View style={styles.loadingOverlay}>
            <Text style={styles.loadingText}>Initializing advanced features...</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

// ============================================================================
// STYLES
// ============================================================================

function createStyles(isDark: boolean, width: number, height: number) {
  return StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: isDark ? '#000000' : '#FFFFFF',
    },
    scrollView: {
      flex: 1,
    },
    scrollContent: {
      padding: 16,
      paddingBottom: 32,
    },
    header: {
      alignItems: 'center',
      marginBottom: 24,
      paddingVertical: 16,
    },
    title: {
      fontSize: 28,
      fontWeight: 'bold',
      color: isDark ? '#FFFFFF' : '#000000',
      marginBottom: 8,
      textAlign: 'center',
    },
    subtitle: {
      fontSize: 16,
      color: isDark ? '#8E8E93' : '#6C6C70',
      textAlign: 'center',
      lineHeight: 24,
    },
    infoCard: {
      marginBottom: 24,
    },
    systemInfo: {
      gap: 8,
    },
    infoRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    infoLabel: {
      fontSize: 14,
      color: isDark ? '#8E8E93' : '#6C6C70',
      fontWeight: '500',
    },
    infoValue: {
      fontSize: 14,
      color: isDark ? '#FFFFFF' : '#000000',
      fontWeight: '600',
    },
    featuresSection: {
      marginBottom: 24,
    },
    sectionTitle: {
      fontSize: 20,
      fontWeight: '600',
      color: isDark ? '#FFFFFF' : '#000000',
      marginBottom: 16,
    },
    featureCard: {
      marginBottom: 12,
    },
    disabledCard: {
      opacity: 0.6,
    },
    featureFooter: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginTop: 8,
    },
    featureStatus: {
      fontSize: 12,
      fontWeight: '600',
    },
    enabledStatus: {
      color: '#34C759',
    },
    disabledStatus: {
      color: '#FF3B30',
    },
    imagesSection: {
      marginBottom: 24,
    },
    imageGrid: {
      flexDirection: 'row',
      justifyContent: 'space-around',
      alignItems: 'center',
      paddingVertical: 16,
    },
    performanceCard: {
      marginBottom: 24,
    },
    metricsGrid: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      justifyContent: 'space-between',
      marginBottom: 16,
    },
    metricItem: {
      width: '48%',
      backgroundColor: isDark ? '#2C2C2E' : '#FFFFFF',
      borderRadius: 12,
      padding: 12,
      marginBottom: 8,
      alignItems: 'center',
    },
    metricLabel: {
      fontSize: 12,
      color: isDark ? '#8E8E93' : '#6C6C70',
      marginBottom: 4,
    },
    metricValue: {
      fontSize: 18,
      fontWeight: 'bold',
      color: isDark ? '#FFFFFF' : '#000000',
    },
    optimizationWarning: {
      backgroundColor: isDark ? '#FF3B30' : '#FFE5E5',
      borderRadius: 8,
      padding: 12,
      marginTop: 8,
    },
    warningText: {
      fontSize: 14,
      fontWeight: '600',
      color: isDark ? '#FFFFFF' : '#FF3B30',
      marginBottom: 4,
    },
    criticalText: {
      fontSize: 12,
      color: isDark ? '#FFFFFF' : '#FF3B30',
    },
    loadingOverlay: {
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: isDark ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.8)',
      justifyContent: 'center',
      alignItems: 'center',
    },
    loadingText: {
      fontSize: 16,
      color: isDark ? '#FFFFFF' : '#000000',
      textAlign: 'center',
    },
  });
}
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Alert,
  useWindowDimensions,
  Platform,
  Linking,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useColorScheme } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { AnimatedCard } from '../advanced/animated-card';
import { OptimizedImage, AvatarImage, CardImage } from '../optimized/optimized-image';
import { AccessibleButton } from '../accessibility/accessible-button';
import { useAppStore, useAuth, useTheme } from '../../store/app-store';
import { useOptimizedPerformance } from '../../hooks/performance/use-optimized-performance';
import { useTranslation } from '../../lib/i18n/i18n-config';
import { 
  initializeDeepLinking, 
  registerDeepLinkHandler, 
  generateDeepLink,
  navigateToScreen,
  shareScreen,
} from '../../lib/navigation/deep-linking';
import { 
  initializeSentry, 
  trackScreen, 
  trackUserAction, 
  captureMessage,
  setUser,
} from '../../lib/monitoring/sentry-config';
import { 
  initializePermissions, 
  requestPermission, 
  isPermissionGranted,
  getPermissionGroups,
} from '../../lib/permissions/permissions-manager';
import { 
  initializeOTAUpdates, 
  checkForUpdates, 
  getUpdateInfo,
  isUpdateEnabled,
} from '../../lib/updates/ota-updates';
import { 
  LazyDashboardScreen, 
  LazyProfileScreen, 
  preloadMainComponents,
} from '../../lib/code-splitting/lazy-components';

// ============================================================================
// TYPES
// ============================================================================

interface FeatureDemo {
  id: string;
  title: string;
  description: string;
  icon: keyof typeof Ionicons.glyphMap;
  onPress: () => void;
  isEnabled: boolean;
}

interface SystemInfo {
  platform: string;
  version: string;
  screenSize: string;
  isDarkMode: boolean;
  locale: string;
  updateEnabled: boolean;
  permissions: string[];
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function AdvancedFeaturesDemo(): JSX.Element {
  const { width, height } = useWindowDimensions();
  const colorScheme = useColorScheme();
  const { t } = useTranslation();
  const { isDarkMode, effectiveTheme } = useTheme();
  const { user, isAuthenticated } = useAuth();
  
  const {
    metrics,
    optimization,
    trackRender,
    trackInteraction,
    endInteraction,
  } = useOptimizedPerformance({
    enableRenderTracking: true,
    enableFPSTracking: true,
    enableInteractionTracking: true,
  });

  const [systemInfo, setSystemInfo] = useState<SystemInfo>({
    platform: Platform.OS,
    version: Platform.Version.toString(),
    screenSize: `${width} × ${height}`,
    isDarkMode,
    locale: t('locale'),
    updateEnabled: false,
    permissions: [],
  });

  const [isLoading, setIsLoading] = useState(false);

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  useEffect(() => {
    const initializeFeatures = async () => {
      try {
        setIsLoading(true);

        // Initialize deep linking
        initializeDeepLinking();
        registerDeepLinkHandler('/demo', (params) => {
          Alert.alert('Deep Link Received', `Demo screen opened with params: ${JSON.stringify(params)}`);
        });

        // Initialize Sentry
        initializeSentry();
        if (user) {
          setUser({
            id: user.id,
            email: user.email,
            username: user.username,
            role: user.role,
          });
        }

        // Initialize permissions
        await initializePermissions();
        const permissionGroups = getPermissionGroups();
        setSystemInfo(prev => ({
          ...prev,
          permissions: permissionGroups.map(group => group.name),
        }));

        // Initialize OTA updates
        await initializeOTAUpdates({
          checkOnLaunch: true,
          autoDownload: true,
          requireUserConsent: true,
        });
        setSystemInfo(prev => ({
          ...prev,
          updateEnabled: isUpdateEnabled(),
        }));

        // Track screen
        trackScreen('AdvancedFeaturesDemo');

        setIsLoading(false);
      } catch (error) {
        console.error('Error initializing features:', error);
        setIsLoading(false);
      }
    };

    initializeFeatures();
  }, [user, t, isDarkMode, width, height]);

  // ============================================================================
  // FEATURE DEMOS
  // ============================================================================

  const featureDemos: FeatureDemo[] = useMemo(() => [
    {
      id: 'deep-linking',
      title: 'Deep Linking',
      description: 'Test deep linking and universal links',
      icon: 'link-outline',
      onPress: handleDeepLinkingDemo,
      isEnabled: true,
    },
    {
      id: 'image-optimization',
      title: 'Image Optimization',
      description: 'WebP support and lazy loading',
      icon: 'image-outline',
      onPress: handleImageOptimizationDemo,
      isEnabled: true,
    },
    {
      id: 'code-splitting',
      title: 'Code Splitting',
      description: 'Lazy loading with React Suspense',
      icon: 'code-slash-outline',
      onPress: handleCodeSplittingDemo,
      isEnabled: true,
    },
    {
      id: 'permissions',
      title: 'Permissions',
      description: 'Device permissions management',
      icon: 'shield-checkmark-outline',
      onPress: handlePermissionsDemo,
      isEnabled: true,
    },
    {
      id: 'ota-updates',
      title: 'OTA Updates',
      description: 'Over-the-air updates',
      icon: 'cloud-download-outline',
      onPress: handleOTAUpdatesDemo,
      isEnabled: systemInfo.updateEnabled,
    },
    {
      id: 'sentry-monitoring',
      title: 'Error Monitoring',
      description: 'Sentry integration for error tracking',
      icon: 'bug-outline',
      onPress: handleSentryDemo,
      isEnabled: true,
    },
    {
      id: 'performance',
      title: 'Performance',
      description: 'Real-time performance monitoring',
      icon: 'speedometer-outline',
      onPress: handlePerformanceDemo,
      isEnabled: true,
    },
    {
      id: 'animations',
      title: 'Animations',
      description: 'Advanced animations with Reanimated',
      icon: 'flash-outline',
      onPress: handleAnimationsDemo,
      isEnabled: true,
    },
  ], [systemInfo.updateEnabled]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleDeepLinkingDemo = useCallback(async () => {
    const interaction = trackInteraction('deep_linking_demo');
    
    try {
      const deepLink = generateDeepLink('demo', { feature: 'deep_linking' });
      await shareScreen('demo', { feature: 'deep_linking' });
      
      Alert.alert(
        'Deep Link Generated',
        `Deep link: ${deepLink}\n\nThis link can be shared and will open the app directly to this screen.`,
        [
          { text: 'OK' },
          { 
            text: 'Copy Link', 
            onPress: () => {
              // In a real app, you'd copy to clipboard
              console.log('Deep link copied:', deepLink);
            }
          }
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to generate deep link');
    } finally {
      endInteraction(interaction);
    }
  }, [trackInteraction, endInteraction]);

  const handleImageOptimizationDemo = useCallback(() => {
    const interaction = trackInteraction('image_optimization_demo');
    
    Alert.alert(
      'Image Optimization',
      'The images below demonstrate:\n\n• WebP format support\n• Lazy loading\n• Responsive sizing\n• Error handling\n• Caching strategies',
      [{ text: 'OK' }]
    );
    
    endInteraction(interaction);
  }, [trackInteraction, endInteraction]);

  const handleCodeSplittingDemo = useCallback(async () => {
    const interaction = trackInteraction('code_splitting_demo');
    
    try {
      Alert.alert(
        'Code Splitting',
        'Preloading main components...',
        [{ text: 'OK' }]
      );
      
      await preloadMainComponents();
      
      Alert.alert(
        'Success',
        'Main components have been preloaded successfully!'
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to preload components');
    } finally {
      endInteraction(interaction);
    }
  }, [trackInteraction, endInteraction]);

  const handlePermissionsDemo = useCallback(async () => {
    const interaction = trackInteraction('permissions_demo');
    
    try {
      const result = await requestPermission({
        permission: 'camera',
        rationale: 'Camera access is needed to demonstrate the permissions system.',
        onGranted: () => {
          Alert.alert('Success', 'Camera permission granted!');
        },
        onDenied: () => {
          Alert.alert('Permission Denied', 'Camera permission was denied.');
        },
        onBlocked: () => {
          Alert.alert('Permission Blocked', 'Camera permission is blocked. Please enable it in settings.');
        },
      });
      
      console.log('Permission result:', result);
    } catch (error) {
      Alert.alert('Error', 'Failed to request permission');
    } finally {
      endInteraction(interaction);
    }
  }, [trackInteraction, endInteraction]);

  const handleOTAUpdatesDemo = useCallback(async () => {
    const interaction = trackInteraction('ota_updates_demo');
    
    try {
      const updateInfo = await getUpdateInfo();
      
      if (updateInfo.isAvailable) {
        Alert.alert(
          'Update Available',
          `A new update is available!\n\nVersion: ${updateInfo.manifest?.version || 'Unknown'}\nDescription: ${updateInfo.manifest?.description || 'Bug fixes and improvements'}`,
          [
            { text: 'Later' },
            { 
              text: 'Check for Updates', 
              onPress: async () => {
                const result = await checkForUpdates();
                if (result.isAvailable) {
                  Alert.alert('Update Found', 'A new update is available for download.');
                } else {
                  Alert.alert('No Updates', 'You are running the latest version.');
                }
              }
            }
          ]
        );
      } else {
        Alert.alert('No Updates', 'You are running the latest version.');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to check for updates');
    } finally {
      endInteraction(interaction);
    }
  }, [trackInteraction, endInteraction]);

  const handleSentryDemo = useCallback(() => {
    const interaction = trackInteraction('sentry_demo');
    
    try {
      // Simulate an error for testing
      throw new Error('This is a test error for Sentry monitoring');
    } catch (error) {
      captureMessage('Sentry demo error captured', 'error', {
        feature: 'sentry_demo',
        timestamp: new Date().toISOString(),
      });
      
      Alert.alert(
        'Error Captured',
        'A test error has been captured and sent to Sentry for monitoring.',
        [{ text: 'OK' }]
      );
    } finally {
      endInteraction(interaction);
    }
  }, [trackInteraction, endInteraction]);

  const handlePerformanceDemo = useCallback(() => {
    const interaction = trackInteraction('performance_demo');
    
    Alert.alert(
      'Performance Metrics',
      `Current Performance:\n\n• Renders: ${metrics.renderCount}\n• Avg Render Time: ${metrics.averageRenderTime.toFixed(2)}ms\n• FPS: ${metrics.fps || 'N/A'}\n• Interactions: ${metrics.interactionCount}\n\nOptimization Level: ${optimization.optimizationLevel.toUpperCase()}`,
      [{ text: 'OK' }]
    );
    
    endInteraction(interaction);
  }, [trackInteraction, endInteraction, metrics, optimization]);

  const handleAnimationsDemo = useCallback(() => {
    const interaction = trackInteraction('animations_demo');
    
    Alert.alert(
      'Animations Demo',
      'The cards below demonstrate advanced animations:\n\n• Spring animations\n• Gesture handling\n• Hover effects\n• Press animations\n• Swipe gestures',
      [{ text: 'OK' }]
    );
    
    endInteraction(interaction);
  }, [trackInteraction, endInteraction]);

  // ============================================================================
  // RENDER TRACKING
  // ============================================================================
  
  useEffect(() => {
    trackRender();
  });

  // ============================================================================
  // RENDER
  // ============================================================================

  const styles = createStyles(isDarkMode, width, height);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView 
        style={styles.scrollView} 
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Advanced Features Demo</Text>
          <Text style={styles.subtitle}>
            Demonstrating all the advanced features and optimizations
          </Text>
        </View>

        {/* System Information */}
        <AnimatedCard
          title="System Information"
          subtitle="Current device and app status"
          icon="information-circle-outline"
          variant="elevated"
          size="medium"
          style={styles.infoCard}
        >
          <View style={styles.systemInfo}>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Platform:</Text>
              <Text style={styles.infoValue}>{systemInfo.platform} {systemInfo.version}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Screen:</Text>
              <Text style={styles.infoValue}>{systemInfo.screenSize}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Theme:</Text>
              <Text style={styles.infoValue}>{systemInfo.isDarkMode ? 'Dark' : 'Light'}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Locale:</Text>
              <Text style={styles.infoValue}>{systemInfo.locale}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>OTA Updates:</Text>
              <Text style={styles.infoValue}>{systemInfo.updateEnabled ? 'Enabled' : 'Disabled'}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Permissions:</Text>
              <Text style={styles.infoValue}>{systemInfo.permissions.length} groups</Text>
            </View>
          </View>
        </AnimatedCard>

        {/* Feature Demos */}
        <View style={styles.featuresSection}>
          <Text style={styles.sectionTitle}>Feature Demonstrations</Text>
          
          {featureDemos.map((feature) => (
            <AnimatedCard
              key={feature.id}
              title={feature.title}
              description={feature.description}
              icon={feature.icon}
              variant="outlined"
              size="medium"
              onPress={feature.onPress}
              enablePress={feature.isEnabled}
              enableLongPress={true}
              enableSwipe={true}
              style={[
                styles.featureCard,
                !feature.isEnabled && styles.disabledCard,
              ]}
            >
              <View style={styles.featureFooter}>
                <Text style={[
                  styles.featureStatus,
                  feature.isEnabled ? styles.enabledStatus : styles.disabledStatus,
                ]}>
                  {feature.isEnabled ? 'Enabled' : 'Disabled'}
                </Text>
                <Ionicons
                  name={feature.isEnabled ? 'checkmark-circle' : 'close-circle'}
                  size={16}
                  color={feature.isEnabled ? '#34C759' : '#FF3B30'}
                />
              </View>
            </AnimatedCard>
          ))}
        </View>

        {/* Image Optimization Demo */}
        <View style={styles.imagesSection}>
          <Text style={styles.sectionTitle}>Image Optimization</Text>
          
          <View style={styles.imageGrid}>
            <AvatarImage
              source="https://picsum.photos/200/200?random=1"
              width={80}
              height={80}
              placeholder="https://via.placeholder.com/80x80/007AFF/FFFFFF?text=Avatar"
              fallback="https://via.placeholder.com/80x80/FF3B30/FFFFFF?text=Error"
              enableWebP={true}
              quality={0.8}
              accessibilityLabel="Sample avatar image"
            />
            
            <CardImage
              source="https://picsum.photos/300/200?random=2"
              width={150}
              height={100}
              placeholder="https://via.placeholder.com/150x100/007AFF/FFFFFF?text=Loading"
              fallback="https://via.placeholder.com/150x100/FF3B30/FFFFFF?text=Error"
              enableWebP={true}
              quality={0.9}
              accessibilityLabel="Sample card image"
            />
            
            <OptimizedImage
              source="https://picsum.photos/200/150?random=3"
              width={120}
              height={90}
              placeholder="https://via.placeholder.com/120x90/007AFF/FFFFFF?text=Loading"
              fallback="https://via.placeholder.com/120x90/FF3B30/FFFFFF?text=Error"
              enableWebP={true}
              quality={0.7}
              fadeInDuration={500}
              scaleInDuration={300}
              accessibilityLabel="Sample optimized image"
            />
          </View>
        </View>

        {/* Performance Metrics */}
        <AnimatedCard
          title="Performance Metrics"
          subtitle="Real-time performance monitoring"
          icon="speedometer-outline"
          variant="filled"
          size="large"
          style={styles.performanceCard}
        >
          <View style={styles.metricsGrid}>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>Renders</Text>
              <Text style={styles.metricValue}>{metrics.renderCount}</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>Avg Render Time</Text>
              <Text style={styles.metricValue}>{metrics.averageRenderTime.toFixed(2)}ms</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>FPS</Text>
              <Text style={styles.metricValue}>{metrics.fps || 'N/A'}</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>Interactions</Text>
              <Text style={styles.metricValue}>{metrics.interactionCount}</Text>
            </View>
          </View>
          
          {optimization.shouldOptimize && (
            <View style={styles.optimizationWarning}>
              <Text style={styles.warningText}>
                Optimization Level: {optimization.optimizationLevel.toUpperCase()}
              </Text>
              {optimization.criticalIssues.length > 0 && (
                <Text style={styles.criticalText}>
                  Critical Issues: {optimization.criticalIssues.join(', ')}
                </Text>
              )}
            </View>
          )}
        </AnimatedCard>

        {/* Loading State */}
        {isLoading && (
          <View style={styles.loadingOverlay}>
            <Text style={styles.loadingText}>Initializing advanced features...</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

// ============================================================================
// STYLES
// ============================================================================

function createStyles(isDark: boolean, width: number, height: number) {
  return StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: isDark ? '#000000' : '#FFFFFF',
    },
    scrollView: {
      flex: 1,
    },
    scrollContent: {
      padding: 16,
      paddingBottom: 32,
    },
    header: {
      alignItems: 'center',
      marginBottom: 24,
      paddingVertical: 16,
    },
    title: {
      fontSize: 28,
      fontWeight: 'bold',
      color: isDark ? '#FFFFFF' : '#000000',
      marginBottom: 8,
      textAlign: 'center',
    },
    subtitle: {
      fontSize: 16,
      color: isDark ? '#8E8E93' : '#6C6C70',
      textAlign: 'center',
      lineHeight: 24,
    },
    infoCard: {
      marginBottom: 24,
    },
    systemInfo: {
      gap: 8,
    },
    infoRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    infoLabel: {
      fontSize: 14,
      color: isDark ? '#8E8E93' : '#6C6C70',
      fontWeight: '500',
    },
    infoValue: {
      fontSize: 14,
      color: isDark ? '#FFFFFF' : '#000000',
      fontWeight: '600',
    },
    featuresSection: {
      marginBottom: 24,
    },
    sectionTitle: {
      fontSize: 20,
      fontWeight: '600',
      color: isDark ? '#FFFFFF' : '#000000',
      marginBottom: 16,
    },
    featureCard: {
      marginBottom: 12,
    },
    disabledCard: {
      opacity: 0.6,
    },
    featureFooter: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginTop: 8,
    },
    featureStatus: {
      fontSize: 12,
      fontWeight: '600',
    },
    enabledStatus: {
      color: '#34C759',
    },
    disabledStatus: {
      color: '#FF3B30',
    },
    imagesSection: {
      marginBottom: 24,
    },
    imageGrid: {
      flexDirection: 'row',
      justifyContent: 'space-around',
      alignItems: 'center',
      paddingVertical: 16,
    },
    performanceCard: {
      marginBottom: 24,
    },
    metricsGrid: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      justifyContent: 'space-between',
      marginBottom: 16,
    },
    metricItem: {
      width: '48%',
      backgroundColor: isDark ? '#2C2C2E' : '#FFFFFF',
      borderRadius: 12,
      padding: 12,
      marginBottom: 8,
      alignItems: 'center',
    },
    metricLabel: {
      fontSize: 12,
      color: isDark ? '#8E8E93' : '#6C6C70',
      marginBottom: 4,
    },
    metricValue: {
      fontSize: 18,
      fontWeight: 'bold',
      color: isDark ? '#FFFFFF' : '#000000',
    },
    optimizationWarning: {
      backgroundColor: isDark ? '#FF3B30' : '#FFE5E5',
      borderRadius: 8,
      padding: 12,
      marginTop: 8,
    },
    warningText: {
      fontSize: 14,
      fontWeight: '600',
      color: isDark ? '#FFFFFF' : '#FF3B30',
      marginBottom: 4,
    },
    criticalText: {
      fontSize: 12,
      color: isDark ? '#FFFFFF' : '#FF3B30',
    },
    loadingOverlay: {
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: isDark ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.8)',
      justifyContent: 'center',
      alignItems: 'center',
    },
    loadingText: {
      fontSize: 16,
      color: isDark ? '#FFFFFF' : '#000000',
      textAlign: 'center',
    },
  });
}


