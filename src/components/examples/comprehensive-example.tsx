import React, { useState, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Alert,
  useWindowDimensions,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import { ErrorBoundary } from '../error-boundary/error-boundary';
import { useAppStore, useAuth, useTheme, useNotifications } from '../../store/app-store';
import { useOptimizedPerformance } from '../../hooks/performance/use-optimized-performance';
import { useTranslation } from '../../lib/i18n/i18n-config';
import { validateFormData, LoginFormSchema, type LoginFormData } from '../../lib/validation/validation-schemas';
import { secureStorage } from '../../lib/security/secure-storage';

// ============================================================================
// TYPES
// ============================================================================

interface ExampleFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

interface PerformanceMetrics {
  renderCount: number;
  averageRenderTime: number;
  fps?: number;
  interactionCount: number;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function ComprehensiveExample(): JSX.Element {
  // ============================================================================
  // HOOKS
  // ============================================================================
  
  const { width, height } = useWindowDimensions();
  const { t } = useTranslation();
  const { isDarkMode, effectiveTheme, setMode } = useTheme();
  const { login, logout, isAuthenticated, user, isLoading, error } = useAuth();
  const { toggle: toggleNotification } = useNotifications();
  
  const {
    metrics,
    optimization,
    trackRender,
    trackInteraction,
    endInteraction,
    deferOperation,
    batchOperations,
  } = useOptimizedPerformance({
    enableRenderTracking: true,
    enableFPSTracking: true,
    enableInteractionTracking: true,
  });

  // ============================================================================
  // STATE
  // ============================================================================
  
  const [formData, setFormData] = useState<ExampleFormData>({
    email: '',
    password: '',
    rememberMe: false,
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  // ============================================================================
  // MEMOIZED VALUES
  // ============================================================================
  
  const styles = useMemo(() => createStyles(isDarkMode, width, height), [isDarkMode, width, height]);
  
  const performanceMetrics: PerformanceMetrics = useMemo(() => ({
    renderCount: metrics.renderCount,
    averageRenderTime: metrics.averageRenderTime,
    fps: metrics.fps,
    interactionCount: metrics.interactionCount,
  }), [metrics]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================
  
  const handleInputChange = useCallback((field: keyof ExampleFormData, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setValidationErrors([]);
  }, []);

  const handleLogin = useCallback(async () => {
    const interaction = trackInteraction('login_attempt', { email: formData.email });
    
    try {
      setIsSubmitting(true);
      
      // Validate form data with Zod
      const validation = validateFormData(LoginFormSchema, formData);
      
      if (!validation.success) {
        setValidationErrors(validation.errors || []);
        return;
      }

      // Defer the login operation for better performance
      deferOperation(async () => {
        await login(formData.email, formData.password);
        
        if (formData.rememberMe) {
          await secureStorage.setUserData(formData);
        }
      });
      
    } catch (error) {
      Alert.alert(
        t('errors.unknownError'),
        error instanceof Error ? error.message : 'An unexpected error occurred'
      );
    } finally {
      setIsSubmitting(false);
      endInteraction(interaction);
    }
  }, [formData, login, trackInteraction, endInteraction, deferOperation, t]);

  const handleLogout = useCallback(async () => {
    const interaction = trackInteraction('logout', { userId: user?.id });
    
    try {
      await secureStorage.clearAllAuthData();
      logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      endInteraction(interaction);
    }
  }, [logout, user?.id, trackInteraction, endInteraction]);

  const handleThemeToggle = useCallback(() => {
    const interaction = trackInteraction('theme_toggle', { 
      from: effectiveTheme, 
      to: effectiveTheme === 'dark' ? 'light' : 'dark' 
    });
    
    setMode(effectiveTheme === 'dark' ? 'light' : 'dark');
    endInteraction(interaction);
  }, [effectiveTheme, setMode, trackInteraction, endInteraction]);

  const handleNotificationToggle = useCallback((type: keyof ReturnType<typeof useNotifications>) => {
    const interaction = trackInteraction('notification_toggle', { type });
    toggleNotification(type);
    endInteraction(interaction);
  }, [toggleNotification, trackInteraction, endInteraction]);

  const handlePerformanceOptimization = useCallback(() => {
    const operations = [
      () => console.log('Clearing caches...'),
      () => console.log('Optimizing memory...'),
      () => console.log('Updating performance metrics...'),
    ];
    
    batchOperations(operations);
  }, [batchOperations]);

  // ============================================================================
  // RENDER TRACKING
  // ============================================================================
  
  React.useEffect(() => {
    trackRender();
  });

  // ============================================================================
  // RENDER
  // ============================================================================
  
  return (
    <ErrorBoundary>
      <SafeAreaView style={styles.container}>
        <ScrollView 
          style={styles.scrollView} 
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Header Section */}
          <View style={styles.header}>
            <Text style={styles.title}>Blaze AI Mobile</Text>
            <Text style={styles.subtitle}>
              {t('common.welcome')} {user?.firstName || 'User'}
            </Text>
          </View>

          {/* Performance Metrics Card */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Performance Metrics</Text>
            <View style={styles.metricsGrid}>
              <View style={styles.metricItem}>
                <Text style={styles.metricLabel}>Renders</Text>
                <Text style={styles.metricValue}>{performanceMetrics.renderCount}</Text>
              </View>
              <View style={styles.metricItem}>
                <Text style={styles.metricLabel}>Avg Render Time</Text>
                <Text style={styles.metricValue}>{performanceMetrics.averageRenderTime.toFixed(2)}ms</Text>
              </View>
              <View style={styles.metricItem}>
                <Text style={styles.metricLabel}>FPS</Text>
                <Text style={styles.metricValue}>{performanceMetrics.fps || 'N/A'}</Text>
              </View>
              <View style={styles.metricItem}>
                <Text style={styles.metricLabel}>Interactions</Text>
                <Text style={styles.metricValue}>{performanceMetrics.interactionCount}</Text>
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
          </View>

          {/* Authentication Section */}
          {!isAuthenticated ? (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>Authentication</Text>
              
              {validationErrors.length > 0 && (
                <View style={styles.errorContainer}>
                  {validationErrors.map((error, index) => (
                    <Text key={index} style={styles.errorText}>{error}</Text>
                  ))}
                </View>
              )}
              
              {error && (
                <Text style={styles.errorText}>{error}</Text>
              )}
              
              <View style={styles.form}>
                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>{t('auth.email')}</Text>
                  <View style={styles.inputContainer}>
                    <Text
                      style={styles.input}
                      onPress={() => handleInputChange('email', 'user@example.com')}
                    >
                      {formData.email || t('auth.email')}
                    </Text>
                  </View>
                </View>
                
                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>{t('auth.password')}</Text>
                  <View style={styles.inputContainer}>
                    <Text
                      style={styles.input}
                      onPress={() => handleInputChange('password', 'password123')}
                    >
                      {formData.password ? '••••••••' : t('auth.password')}
                    </Text>
                  </View>
                </View>
                
                <View style={styles.checkboxContainer}>
                  <Text
                    style={styles.checkbox}
                    onPress={() => handleInputChange('rememberMe', !formData.rememberMe)}
                  >
                    {formData.rememberMe ? '☑️' : '☐'} {t('auth.rememberMe')}
                  </Text>
                </View>
                
                <AccessibleButton
                  title={t('auth.login')}
                  onPress={handleLogin}
                  isLoading={isLoading || isSubmitting}
                  isDisabled={!formData.email || !formData.password}
                  variant="primary"
                  size="large"
                  isFullWidth
                  accessibilityLabel={t('auth.login')}
                  accessibilityHint={t('auth.loginError')}
                />
              </View>
            </View>
          ) : (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>Welcome Back!</Text>
              <Text style={styles.userInfo}>
                {user?.firstName} {user?.lastName} ({user?.email})
              </Text>
              <Text style={styles.userInfo}>
                Role: {user?.role} | Verified: {user?.isEmailVerified ? 'Yes' : 'No'}
              </Text>
              
              <AccessibleButton
                title={t('auth.logout')}
                onPress={handleLogout}
                variant="danger"
                size="medium"
                isFullWidth
                accessibilityLabel={t('auth.logout')}
                accessibilityHint="Tap to sign out of your account"
              />
            </View>
          )}

          {/* Theme Controls */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Theme Settings</Text>
            <View style={styles.controlsRow}>
              <AccessibleButton
                title={`Switch to ${effectiveTheme === 'dark' ? 'Light' : 'Dark'} Mode`}
                onPress={handleThemeToggle}
                variant="outline"
                size="medium"
                hasIcon
                iconName="color-palette-outline"
                accessibilityLabel={`Switch to ${effectiveTheme === 'dark' ? 'light' : 'dark'} mode`}
                accessibilityHint="Tap to toggle between light and dark themes"
              />
            </View>
            <Text style={styles.currentTheme}>
              Current Theme: {effectiveTheme} {isDarkMode ? '🌙' : '☀️'}
            </Text>
          </View>

          {/* Notification Controls */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Notification Settings</Text>
            <View style={styles.controlsGrid}>
              {(['email', 'push', 'sms', 'marketing', 'security', 'updates'] as const).map((type) => (
                <AccessibleButton
                  key={type}
                  title={type.charAt(0).toUpperCase() + type.slice(1)}
                  onPress={() => handleNotificationToggle(type)}
                  variant="outline"
                  size="small"
                  accessibilityLabel={`Toggle ${type} notifications`}
                  accessibilityHint={`Tap to enable or disable ${type} notifications`}
                />
              ))}
            </View>
          </View>

          {/* Performance Controls */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Performance Controls</Text>
            <AccessibleButton
              title="Optimize Performance"
              onPress={handlePerformanceOptimization}
              variant="success"
              size="medium"
              hasIcon
              iconName="speedometer-outline"
              accessibilityLabel="Optimize app performance"
              accessibilityHint="Tap to run performance optimization tasks"
            />
          </View>

          {/* Platform Information */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Platform Information</Text>
            <Text style={styles.platformInfo}>
              Platform: {Platform.OS} {Platform.Version}
            </Text>
            <Text style={styles.platformInfo}>
              Screen: {width} × {height}
            </Text>
            <Text style={styles.platformInfo}>
              Locale: {t('locale')}
            </Text>
          </View>
        </ScrollView>
      </SafeAreaView>
    </ErrorBoundary>
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
    },
    subtitle: {
      fontSize: 16,
      color: isDark ? '#8E8E93' : '#6C6C70',
      textAlign: 'center',
    },
    card: {
      backgroundColor: isDark ? '#1C1C1E' : '#F8F9FA',
      borderRadius: 16,
      padding: 20,
      marginBottom: 16,
      borderWidth: 1,
      borderColor: isDark ? '#3A3A3C' : '#E5E5EA',
      shadowColor: isDark ? '#000000' : '#000000',
      shadowOffset: {
        width: 0,
        height: 2,
      },
      shadowOpacity: isDark ? 0.3 : 0.1,
      shadowRadius: 4,
      elevation: 2,
    },
    cardTitle: {
      fontSize: 20,
      fontWeight: '600',
      color: isDark ? '#FFFFFF' : '#000000',
      marginBottom: 16,
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
    form: {
      gap: 16,
    },
    inputGroup: {
      gap: 8,
    },
    inputLabel: {
      fontSize: 16,
      fontWeight: '500',
      color: isDark ? '#FFFFFF' : '#000000',
    },
    inputContainer: {
      backgroundColor: isDark ? '#2C2C2E' : '#FFFFFF',
      borderRadius: 12,
      borderWidth: 1,
      borderColor: isDark ? '#3A3A3C' : '#E5E5EA',
      padding: 16,
    },
    input: {
      fontSize: 16,
      color: isDark ? '#FFFFFF' : '#000000',
    },
    checkboxContainer: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    checkbox: {
      fontSize: 16,
      color: isDark ? '#FFFFFF' : '#000000',
    },
    errorContainer: {
      backgroundColor: isDark ? '#FF3B30' : '#FFE5E5',
      borderRadius: 8,
      padding: 12,
      marginBottom: 16,
    },
    errorText: {
      fontSize: 14,
      color: isDark ? '#FFFFFF' : '#FF3B30',
      marginBottom: 4,
    },
    userInfo: {
      fontSize: 16,
      color: isDark ? '#FFFFFF' : '#000000',
      marginBottom: 8,
    },
    controlsRow: {
      flexDirection: 'row',
      gap: 12,
      marginBottom: 16,
    },
    controlsGrid: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 8,
    },
    currentTheme: {
      fontSize: 14,
      color: isDark ? '#8E8E93' : '#6C6C70',
      textAlign: 'center',
      marginTop: 8,
    },
    platformInfo: {
      fontSize: 14,
      color: isDark ? '#8E8E93' : '#6C6C70',
      marginBottom: 4,
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
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import { ErrorBoundary } from '../error-boundary/error-boundary';
import { useAppStore, useAuth, useTheme, useNotifications } from '../../store/app-store';
import { useOptimizedPerformance } from '../../hooks/performance/use-optimized-performance';
import { useTranslation } from '../../lib/i18n/i18n-config';
import { validateFormData, LoginFormSchema, type LoginFormData } from '../../lib/validation/validation-schemas';
import { secureStorage } from '../../lib/security/secure-storage';

// ============================================================================
// TYPES
// ============================================================================

interface ExampleFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

interface PerformanceMetrics {
  renderCount: number;
  averageRenderTime: number;
  fps?: number;
  interactionCount: number;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function ComprehensiveExample(): JSX.Element {
  // ============================================================================
  // HOOKS
  // ============================================================================
  
  const { width, height } = useWindowDimensions();
  const { t } = useTranslation();
  const { isDarkMode, effectiveTheme, setMode } = useTheme();
  const { login, logout, isAuthenticated, user, isLoading, error } = useAuth();
  const { toggle: toggleNotification } = useNotifications();
  
  const {
    metrics,
    optimization,
    trackRender,
    trackInteraction,
    endInteraction,
    deferOperation,
    batchOperations,
  } = useOptimizedPerformance({
    enableRenderTracking: true,
    enableFPSTracking: true,
    enableInteractionTracking: true,
  });

  // ============================================================================
  // STATE
  // ============================================================================
  
  const [formData, setFormData] = useState<ExampleFormData>({
    email: '',
    password: '',
    rememberMe: false,
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  // ============================================================================
  // MEMOIZED VALUES
  // ============================================================================
  
  const styles = useMemo(() => createStyles(isDarkMode, width, height), [isDarkMode, width, height]);
  
  const performanceMetrics: PerformanceMetrics = useMemo(() => ({
    renderCount: metrics.renderCount,
    averageRenderTime: metrics.averageRenderTime,
    fps: metrics.fps,
    interactionCount: metrics.interactionCount,
  }), [metrics]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================
  
  const handleInputChange = useCallback((field: keyof ExampleFormData, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setValidationErrors([]);
  }, []);

  const handleLogin = useCallback(async () => {
    const interaction = trackInteraction('login_attempt', { email: formData.email });
    
    try {
      setIsSubmitting(true);
      
      // Validate form data with Zod
      const validation = validateFormData(LoginFormSchema, formData);
      
      if (!validation.success) {
        setValidationErrors(validation.errors || []);
        return;
      }

      // Defer the login operation for better performance
      deferOperation(async () => {
        await login(formData.email, formData.password);
        
        if (formData.rememberMe) {
          await secureStorage.setUserData(formData);
        }
      });
      
    } catch (error) {
      Alert.alert(
        t('errors.unknownError'),
        error instanceof Error ? error.message : 'An unexpected error occurred'
      );
    } finally {
      setIsSubmitting(false);
      endInteraction(interaction);
    }
  }, [formData, login, trackInteraction, endInteraction, deferOperation, t]);

  const handleLogout = useCallback(async () => {
    const interaction = trackInteraction('logout', { userId: user?.id });
    
    try {
      await secureStorage.clearAllAuthData();
      logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      endInteraction(interaction);
    }
  }, [logout, user?.id, trackInteraction, endInteraction]);

  const handleThemeToggle = useCallback(() => {
    const interaction = trackInteraction('theme_toggle', { 
      from: effectiveTheme, 
      to: effectiveTheme === 'dark' ? 'light' : 'dark' 
    });
    
    setMode(effectiveTheme === 'dark' ? 'light' : 'dark');
    endInteraction(interaction);
  }, [effectiveTheme, setMode, trackInteraction, endInteraction]);

  const handleNotificationToggle = useCallback((type: keyof ReturnType<typeof useNotifications>) => {
    const interaction = trackInteraction('notification_toggle', { type });
    toggleNotification(type);
    endInteraction(interaction);
  }, [toggleNotification, trackInteraction, endInteraction]);

  const handlePerformanceOptimization = useCallback(() => {
    const operations = [
      () => console.log('Clearing caches...'),
      () => console.log('Optimizing memory...'),
      () => console.log('Updating performance metrics...'),
    ];
    
    batchOperations(operations);
  }, [batchOperations]);

  // ============================================================================
  // RENDER TRACKING
  // ============================================================================
  
  React.useEffect(() => {
    trackRender();
  });

  // ============================================================================
  // RENDER
  // ============================================================================
  
  return (
    <ErrorBoundary>
      <SafeAreaView style={styles.container}>
        <ScrollView 
          style={styles.scrollView} 
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Header Section */}
          <View style={styles.header}>
            <Text style={styles.title}>Blaze AI Mobile</Text>
            <Text style={styles.subtitle}>
              {t('common.welcome')} {user?.firstName || 'User'}
            </Text>
          </View>

          {/* Performance Metrics Card */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Performance Metrics</Text>
            <View style={styles.metricsGrid}>
              <View style={styles.metricItem}>
                <Text style={styles.metricLabel}>Renders</Text>
                <Text style={styles.metricValue}>{performanceMetrics.renderCount}</Text>
              </View>
              <View style={styles.metricItem}>
                <Text style={styles.metricLabel}>Avg Render Time</Text>
                <Text style={styles.metricValue}>{performanceMetrics.averageRenderTime.toFixed(2)}ms</Text>
              </View>
              <View style={styles.metricItem}>
                <Text style={styles.metricLabel}>FPS</Text>
                <Text style={styles.metricValue}>{performanceMetrics.fps || 'N/A'}</Text>
              </View>
              <View style={styles.metricItem}>
                <Text style={styles.metricLabel}>Interactions</Text>
                <Text style={styles.metricValue}>{performanceMetrics.interactionCount}</Text>
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
          </View>

          {/* Authentication Section */}
          {!isAuthenticated ? (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>Authentication</Text>
              
              {validationErrors.length > 0 && (
                <View style={styles.errorContainer}>
                  {validationErrors.map((error, index) => (
                    <Text key={index} style={styles.errorText}>{error}</Text>
                  ))}
                </View>
              )}
              
              {error && (
                <Text style={styles.errorText}>{error}</Text>
              )}
              
              <View style={styles.form}>
                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>{t('auth.email')}</Text>
                  <View style={styles.inputContainer}>
                    <Text
                      style={styles.input}
                      onPress={() => handleInputChange('email', 'user@example.com')}
                    >
                      {formData.email || t('auth.email')}
                    </Text>
                  </View>
                </View>
                
                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>{t('auth.password')}</Text>
                  <View style={styles.inputContainer}>
                    <Text
                      style={styles.input}
                      onPress={() => handleInputChange('password', 'password123')}
                    >
                      {formData.password ? '••••••••' : t('auth.password')}
                    </Text>
                  </View>
                </View>
                
                <View style={styles.checkboxContainer}>
                  <Text
                    style={styles.checkbox}
                    onPress={() => handleInputChange('rememberMe', !formData.rememberMe)}
                  >
                    {formData.rememberMe ? '☑️' : '☐'} {t('auth.rememberMe')}
                  </Text>
                </View>
                
                <AccessibleButton
                  title={t('auth.login')}
                  onPress={handleLogin}
                  isLoading={isLoading || isSubmitting}
                  isDisabled={!formData.email || !formData.password}
                  variant="primary"
                  size="large"
                  isFullWidth
                  accessibilityLabel={t('auth.login')}
                  accessibilityHint={t('auth.loginError')}
                />
              </View>
            </View>
          ) : (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>Welcome Back!</Text>
              <Text style={styles.userInfo}>
                {user?.firstName} {user?.lastName} ({user?.email})
              </Text>
              <Text style={styles.userInfo}>
                Role: {user?.role} | Verified: {user?.isEmailVerified ? 'Yes' : 'No'}
              </Text>
              
              <AccessibleButton
                title={t('auth.logout')}
                onPress={handleLogout}
                variant="danger"
                size="medium"
                isFullWidth
                accessibilityLabel={t('auth.logout')}
                accessibilityHint="Tap to sign out of your account"
              />
            </View>
          )}

          {/* Theme Controls */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Theme Settings</Text>
            <View style={styles.controlsRow}>
              <AccessibleButton
                title={`Switch to ${effectiveTheme === 'dark' ? 'Light' : 'Dark'} Mode`}
                onPress={handleThemeToggle}
                variant="outline"
                size="medium"
                hasIcon
                iconName="color-palette-outline"
                accessibilityLabel={`Switch to ${effectiveTheme === 'dark' ? 'light' : 'dark'} mode`}
                accessibilityHint="Tap to toggle between light and dark themes"
              />
            </View>
            <Text style={styles.currentTheme}>
              Current Theme: {effectiveTheme} {isDarkMode ? '🌙' : '☀️'}
            </Text>
          </View>

          {/* Notification Controls */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Notification Settings</Text>
            <View style={styles.controlsGrid}>
              {(['email', 'push', 'sms', 'marketing', 'security', 'updates'] as const).map((type) => (
                <AccessibleButton
                  key={type}
                  title={type.charAt(0).toUpperCase() + type.slice(1)}
                  onPress={() => handleNotificationToggle(type)}
                  variant="outline"
                  size="small"
                  accessibilityLabel={`Toggle ${type} notifications`}
                  accessibilityHint={`Tap to enable or disable ${type} notifications`}
                />
              ))}
            </View>
          </View>

          {/* Performance Controls */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Performance Controls</Text>
            <AccessibleButton
              title="Optimize Performance"
              onPress={handlePerformanceOptimization}
              variant="success"
              size="medium"
              hasIcon
              iconName="speedometer-outline"
              accessibilityLabel="Optimize app performance"
              accessibilityHint="Tap to run performance optimization tasks"
            />
          </View>

          {/* Platform Information */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Platform Information</Text>
            <Text style={styles.platformInfo}>
              Platform: {Platform.OS} {Platform.Version}
            </Text>
            <Text style={styles.platformInfo}>
              Screen: {width} × {height}
            </Text>
            <Text style={styles.platformInfo}>
              Locale: {t('locale')}
            </Text>
          </View>
        </ScrollView>
      </SafeAreaView>
    </ErrorBoundary>
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
    },
    subtitle: {
      fontSize: 16,
      color: isDark ? '#8E8E93' : '#6C6C70',
      textAlign: 'center',
    },
    card: {
      backgroundColor: isDark ? '#1C1C1E' : '#F8F9FA',
      borderRadius: 16,
      padding: 20,
      marginBottom: 16,
      borderWidth: 1,
      borderColor: isDark ? '#3A3A3C' : '#E5E5EA',
      shadowColor: isDark ? '#000000' : '#000000',
      shadowOffset: {
        width: 0,
        height: 2,
      },
      shadowOpacity: isDark ? 0.3 : 0.1,
      shadowRadius: 4,
      elevation: 2,
    },
    cardTitle: {
      fontSize: 20,
      fontWeight: '600',
      color: isDark ? '#FFFFFF' : '#000000',
      marginBottom: 16,
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
    form: {
      gap: 16,
    },
    inputGroup: {
      gap: 8,
    },
    inputLabel: {
      fontSize: 16,
      fontWeight: '500',
      color: isDark ? '#FFFFFF' : '#000000',
    },
    inputContainer: {
      backgroundColor: isDark ? '#2C2C2E' : '#FFFFFF',
      borderRadius: 12,
      borderWidth: 1,
      borderColor: isDark ? '#3A3A3C' : '#E5E5EA',
      padding: 16,
    },
    input: {
      fontSize: 16,
      color: isDark ? '#FFFFFF' : '#000000',
    },
    checkboxContainer: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    checkbox: {
      fontSize: 16,
      color: isDark ? '#FFFFFF' : '#000000',
    },
    errorContainer: {
      backgroundColor: isDark ? '#FF3B30' : '#FFE5E5',
      borderRadius: 8,
      padding: 12,
      marginBottom: 16,
    },
    errorText: {
      fontSize: 14,
      color: isDark ? '#FFFFFF' : '#FF3B30',
      marginBottom: 4,
    },
    userInfo: {
      fontSize: 16,
      color: isDark ? '#FFFFFF' : '#000000',
      marginBottom: 8,
    },
    controlsRow: {
      flexDirection: 'row',
      gap: 12,
      marginBottom: 16,
    },
    controlsGrid: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 8,
    },
    currentTheme: {
      fontSize: 14,
      color: isDark ? '#8E8E93' : '#6C6C70',
      textAlign: 'center',
      marginTop: 8,
    },
    platformInfo: {
      fontSize: 14,
      color: isDark ? '#8E8E93' : '#6C6C70',
      marginBottom: 4,
    },
  });
}


