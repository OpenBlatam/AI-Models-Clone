import React, { useState, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Alert,
  useWindowDimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

// Import enhanced components
import { OptimizedButton } from '../optimized-ui/OptimizedButton';
import { OptimizedInput } from '../optimized-ui/OptimizedInput';
import { OptimizedCard } from '../overlays/OptimizedCard';

// Import hooks
import { useOptimizedTheme } from '../../hooks/theme-hooks/useOptimizedTheme';
import { useOptimizedPerformance } from '../../hooks/performance-hooks/useOptimizedPerformance';

// ============================================================================
// TYPES
// ============================================================================

interface FormData {
  name: string;
  email: string;
  message: string;
}

interface ExampleItem {
  id: string;
  title: string;
  description: string;
  status: 'active' | 'inactive' | 'error';
}

// ============================================================================
// STATIC CONTENT
// ============================================================================

const EXAMPLE_ITEMS: ExampleItem[] = [
  {
    id: '1',
    title: 'Performance Optimization',
    description: 'Advanced performance monitoring and optimization features',
    status: 'active',
  },
  {
    id: '2',
    title: 'Enhanced UI Components',
    description: 'Modern, accessible, and performant UI components',
    status: 'active',
  },
  {
    id: '3',
    title: 'Theme System',
    description: 'Comprehensive theming with dark mode support',
    status: 'active',
  },
  {
    id: '4',
    title: 'Accessibility Features',
    description: 'Full accessibility support with ARIA roles',
    status: 'active',
  },
  {
    id: '5',
    title: 'Animation System',
    description: 'Smooth animations with gesture support',
    status: 'inactive',
  },
];

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function AdvancedComponentsExample(): JSX.Element {
  const { theme, isDark, toggleTheme } = useOptimizedTheme();
  const { width, height } = useWindowDimensions();
  const { metrics, optimization, trackRender, trackInteraction, endInteraction } = useOptimizedPerformance({
    enableRenderTracking: true,
    enableFPSTracking: true,
    enableInteractionTracking: true,
  });

  // Form state
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    message: '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Memoized styles for performance
  const styles = useMemo(() => createStyles(theme, width, height), [theme, width, height]);

  // Form handlers
  const handleInputChange = useCallback((field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!formData.name || !formData.email || !formData.message) {
      Alert.alert('Validation Error', 'Please fill in all fields');
      return;
    }

    setIsSubmitting(true);
    trackInteraction('form_submit', { formData });

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      Alert.alert('Success', 'Form submitted successfully!');
      setFormData({ name: '', email: '', message: '' });
      
      endInteraction(trackInteraction('form_success', { formData }));
    } catch (error) {
      Alert.alert('Error', 'Failed to submit form');
      endInteraction(trackInteraction('form_error', { error: error.message }));
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, trackInteraction, endInteraction]);

  const handleThemeToggle = useCallback(() => {
    trackInteraction('theme_toggle', { from: isDark ? 'dark' : 'light' });
    toggleTheme();
  }, [isDark, toggleTheme, trackInteraction]);

  const handleCardPress = useCallback((item: ExampleItem) => {
    trackInteraction('card_press', { itemId: item.id, itemTitle: item.title });
    Alert.alert(item.title, item.description);
  }, [trackInteraction]);

  // Track render for performance monitoring
  React.useEffect(() => {
    trackRender();
  });

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView 
        style={styles.scrollView} 
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header Section */}
        <View style={styles.header}>
          <Text style={styles.title}>Advanced Components Example</Text>
          <Text style={styles.subtitle}>
            Demonstrating enhanced UI components and performance optimizations
          </Text>
          
          <OptimizedButton
            title={`Switch to ${isDark ? 'Light' : 'Dark'} Mode`}
            onPress={handleThemeToggle}
            variant="outline"
            size="medium"
            hasIcon={true}
            iconName="🌙"
            accessibilityLabel={`Switch to ${isDark ? 'light' : 'dark'} mode`}
            accessibilityHint="Toggles between light and dark theme"
            testID="theme-toggle-button"
          />
        </View>

        {/* Performance Metrics Section */}
        <OptimizedCard
          title="Performance Metrics"
          subtitle="Real-time performance monitoring"
          variant="elevated"
          size="large"
          hasShadow={true}
          containerStyle={styles.metricsCard}
        >
          <View style={styles.metricsGrid}>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>Render Count</Text>
              <Text style={styles.metricValue}>{metrics.renderCount}</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>Avg Render Time</Text>
              <Text style={styles.metricValue}>{metrics.averageRenderTime.toFixed(2)}ms</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>FPS</Text>
              <Text style={styles.metricValue}>{metrics.fps?.toFixed(1) || 'N/A'}</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>Optimization Level</Text>
              <Text style={[styles.metricValue, styles[`optimization${optimization.optimizationLevel}`]]}>
                {optimization.optimizationLevel.toUpperCase()}
              </Text>
            </View>
          </View>

          {optimization.shouldOptimize && (
            <View style={styles.recommendationsContainer}>
              <Text style={styles.recommendationsTitle}>Optimization Recommendations:</Text>
              {optimization.recommendations.map((recommendation, index) => (
                <Text key={index} style={styles.recommendation}>
                  • {recommendation}
                </Text>
              ))}
            </View>
          )}
        </OptimizedCard>

        {/* Form Section */}
        <OptimizedCard
          title="Contact Form"
          subtitle="Enhanced input components with validation"
          variant="filled"
          size="large"
          hasShadow={true}
          containerStyle={styles.formCard}
        >
          <View style={styles.formContainer}>
            <OptimizedInput
              label="Name"
              placeholder="Enter your name"
              value={formData.name}
              onChangeText={(value) => handleInputChange('name', value)}
              isRequired={true}
              variant="outlined"
              size="medium"
              hasIcon={true}
              iconName="👤"
              iconPosition="left"
              accessibilityLabel="Name input field"
              accessibilityHint="Enter your full name"
              testID="name-input"
            />

            <OptimizedInput
              label="Email"
              placeholder="Enter your email"
              value={formData.email}
              onChangeText={(value) => handleInputChange('email', value)}
              isRequired={true}
              variant="outlined"
              size="medium"
              hasIcon={true}
              iconName="📧"
              iconPosition="left"
              keyboardType="email-address"
              autoCapitalize="none"
              accessibilityLabel="Email input field"
              accessibilityHint="Enter your email address"
              testID="email-input"
            />

            <OptimizedInput
              label="Message"
              placeholder="Enter your message"
              value={formData.message}
              onChangeText={(value) => handleInputChange('message', value)}
              isRequired={true}
              variant="outlined"
              size="large"
              hasIcon={true}
              iconName="💬"
              iconPosition="left"
              multiline={true}
              numberOfLines={4}
              accessibilityLabel="Message input field"
              accessibilityHint="Enter your message"
              testID="message-input"
            />

            <View style={styles.buttonContainer}>
              <OptimizedButton
                title="Submit Form"
                onPress={handleSubmit}
                variant="primary"
                size="large"
                isLoading={isSubmitting}
                isFullWidth={true}
                hasIcon={true}
                iconName="🚀"
                iconPosition="right"
                accessibilityLabel="Submit form button"
                accessibilityHint="Submits the contact form"
                testID="submit-button"
              />
            </View>
          </View>
        </OptimizedCard>

        {/* Example Items Section */}
        <OptimizedCard
          title="Example Items"
          subtitle="Interactive cards with different variants"
          variant="outlined"
          size="large"
          hasBorder={true}
          containerStyle={styles.itemsCard}
        >
          <View style={styles.itemsContainer}>
            {EXAMPLE_ITEMS.map((item) => (
              <OptimizedCard
                key={item.id}
                title={item.title}
                subtitle={item.description}
                variant={item.status === 'active' ? 'elevated' : 'outlined'}
                size="medium"
                isPressable={true}
                onPress={() => handleCardPress(item)}
                hasShadow={item.status === 'active'}
                containerStyle={[
                  styles.itemCard,
                  item.status === 'error' && styles.errorCard,
                  item.status === 'inactive' && styles.inactiveCard,
                ]}
                accessibilityLabel={`${item.title} card`}
                accessibilityHint={`Tap to view details about ${item.title}`}
                testID={`item-card-${item.id}`}
              />
            ))}
          </View>
        </OptimizedCard>

        {/* Button Showcase Section */}
        <OptimizedCard
          title="Button Variants"
          subtitle="All available button styles and sizes"
          variant="glass"
          size="large"
          hasShadow={true}
          containerStyle={styles.buttonShowcaseCard}
        >
          <View style={styles.buttonShowcase}>
            <View style={styles.buttonRow}>
              <OptimizedButton
                title="Primary"
                onPress={() => trackInteraction('button_press', { variant: 'primary' })}
                variant="primary"
                size="small"
                testID="primary-button"
              />
              <OptimizedButton
                title="Secondary"
                onPress={() => trackInteraction('button_press', { variant: 'secondary' })}
                variant="secondary"
                size="small"
                testID="secondary-button"
              />
              <OptimizedButton
                title="Outline"
                onPress={() => trackInteraction('button_press', { variant: 'outline' })}
                variant="outline"
                size="small"
                testID="outline-button"
              />
            </View>

            <View style={styles.buttonRow}>
              <OptimizedButton
                title="Success"
                onPress={() => trackInteraction('button_press', { variant: 'success' })}
                variant="success"
                size="medium"
                testID="success-button"
              />
              <OptimizedButton
                title="Warning"
                onPress={() => trackInteraction('button_press', { variant: 'warning' })}
                variant="warning"
                size="medium"
                testID="warning-button"
              />
              <OptimizedButton
                title="Danger"
                onPress={() => trackInteraction('button_press', { variant: 'danger' })}
                variant="danger"
                size="medium"
                testID="danger-button"
              />
            </View>

            <View style={styles.buttonRow}>
              <OptimizedButton
                title="Large Button"
                onPress={() => trackInteraction('button_press', { size: 'large' })}
                variant="primary"
                size="large"
                hasRoundedCorners={true}
                testID="large-button"
              />
              <OptimizedButton
                title="XL Button"
                onPress={() => trackInteraction('button_press', { size: 'xl' })}
                variant="secondary"
                size="xl"
                hasRoundedCorners={true}
                testID="xl-button"
              />
            </View>
          </View>
        </OptimizedCard>
      </ScrollView>
    </SafeAreaView>
  );
}

// ============================================================================
// STYLES
// ============================================================================

function createStyles(theme: any, width: number, height: number) {
  return StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.background,
    },
    scrollView: {
      flex: 1,
    },
    scrollContent: {
      padding: theme.spacing.md,
      paddingBottom: theme.spacing.xxl,
    },
    header: {
      alignItems: 'center',
      marginBottom: theme.spacing.xl,
      padding: theme.spacing.lg,
    },
    title: {
      fontSize: theme.typography.h1.fontSize,
      fontWeight: theme.typography.h1.fontWeight,
      color: theme.colors.text,
      textAlign: 'center',
      marginBottom: theme.spacing.sm,
      includeFontPadding: false,
    },
    subtitle: {
      fontSize: theme.typography.body.fontSize,
      color: theme.colors.textSecondary,
      textAlign: 'center',
      marginBottom: theme.spacing.lg,
      includeFontPadding: false,
    },
    metricsCard: {
      marginBottom: theme.spacing.lg,
    },
    metricsGrid: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      justifyContent: 'space-between',
      marginTop: theme.spacing.md,
    },
    metricItem: {
      width: '48%',
      alignItems: 'center',
      padding: theme.spacing.sm,
      marginBottom: theme.spacing.sm,
    },
    metricLabel: {
      fontSize: theme.typography.caption.fontSize,
      color: theme.colors.textSecondary,
      marginBottom: theme.spacing.xs,
      includeFontPadding: false,
    },
    metricValue: {
      fontSize: theme.typography.h4.fontSize,
      fontWeight: theme.typography.h4.fontWeight,
      color: theme.colors.text,
      includeFontPadding: false,
    },
    optimizationlow: {
      color: theme.colors.success,
    },
    optimizationmedium: {
      color: theme.colors.warning,
    },
    optimizationhigh: {
      color: theme.colors.error,
    },
    recommendationsContainer: {
      marginTop: theme.spacing.md,
      padding: theme.spacing.md,
      backgroundColor: theme.colors.backgroundSecondary,
      borderRadius: theme.borderRadius.md,
    },
    recommendationsTitle: {
      fontSize: theme.typography.h6.fontSize,
      fontWeight: theme.typography.h6.fontWeight,
      color: theme.colors.text,
      marginBottom: theme.spacing.sm,
      includeFontPadding: false,
    },
    recommendation: {
      fontSize: theme.typography.bodySmall.fontSize,
      color: theme.colors.textSecondary,
      marginBottom: theme.spacing.xs,
      includeFontPadding: false,
    },
    formCard: {
      marginBottom: theme.spacing.lg,
    },
    formContainer: {
      marginTop: theme.spacing.md,
    },
    buttonContainer: {
      marginTop: theme.spacing.lg,
    },
    itemsCard: {
      marginBottom: theme.spacing.lg,
    },
    itemsContainer: {
      marginTop: theme.spacing.md,
    },
    itemCard: {
      marginBottom: theme.spacing.sm,
    },
    errorCard: {
      borderColor: theme.colors.error,
    },
    inactiveCard: {
      opacity: 0.6,
    },
    buttonShowcaseCard: {
      marginBottom: theme.spacing.lg,
    },
    buttonShowcase: {
      marginTop: theme.spacing.md,
    },
    buttonRow: {
      flexDirection: 'row',
      justifyContent: 'space-around',
      marginBottom: theme.spacing.md,
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
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

// Import enhanced components
import { OptimizedButton } from '../optimized-ui/OptimizedButton';
import { OptimizedInput } from '../optimized-ui/OptimizedInput';
import { OptimizedCard } from '../overlays/OptimizedCard';

// Import hooks
import { useOptimizedTheme } from '../../hooks/theme-hooks/useOptimizedTheme';
import { useOptimizedPerformance } from '../../hooks/performance-hooks/useOptimizedPerformance';

// ============================================================================
// TYPES
// ============================================================================

interface FormData {
  name: string;
  email: string;
  message: string;
}

interface ExampleItem {
  id: string;
  title: string;
  description: string;
  status: 'active' | 'inactive' | 'error';
}

// ============================================================================
// STATIC CONTENT
// ============================================================================

const EXAMPLE_ITEMS: ExampleItem[] = [
  {
    id: '1',
    title: 'Performance Optimization',
    description: 'Advanced performance monitoring and optimization features',
    status: 'active',
  },
  {
    id: '2',
    title: 'Enhanced UI Components',
    description: 'Modern, accessible, and performant UI components',
    status: 'active',
  },
  {
    id: '3',
    title: 'Theme System',
    description: 'Comprehensive theming with dark mode support',
    status: 'active',
  },
  {
    id: '4',
    title: 'Accessibility Features',
    description: 'Full accessibility support with ARIA roles',
    status: 'active',
  },
  {
    id: '5',
    title: 'Animation System',
    description: 'Smooth animations with gesture support',
    status: 'inactive',
  },
];

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function AdvancedComponentsExample(): JSX.Element {
  const { theme, isDark, toggleTheme } = useOptimizedTheme();
  const { width, height } = useWindowDimensions();
  const { metrics, optimization, trackRender, trackInteraction, endInteraction } = useOptimizedPerformance({
    enableRenderTracking: true,
    enableFPSTracking: true,
    enableInteractionTracking: true,
  });

  // Form state
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    message: '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Memoized styles for performance
  const styles = useMemo(() => createStyles(theme, width, height), [theme, width, height]);

  // Form handlers
  const handleInputChange = useCallback((field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!formData.name || !formData.email || !formData.message) {
      Alert.alert('Validation Error', 'Please fill in all fields');
      return;
    }

    setIsSubmitting(true);
    trackInteraction('form_submit', { formData });

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      Alert.alert('Success', 'Form submitted successfully!');
      setFormData({ name: '', email: '', message: '' });
      
      endInteraction(trackInteraction('form_success', { formData }));
    } catch (error) {
      Alert.alert('Error', 'Failed to submit form');
      endInteraction(trackInteraction('form_error', { error: error.message }));
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, trackInteraction, endInteraction]);

  const handleThemeToggle = useCallback(() => {
    trackInteraction('theme_toggle', { from: isDark ? 'dark' : 'light' });
    toggleTheme();
  }, [isDark, toggleTheme, trackInteraction]);

  const handleCardPress = useCallback((item: ExampleItem) => {
    trackInteraction('card_press', { itemId: item.id, itemTitle: item.title });
    Alert.alert(item.title, item.description);
  }, [trackInteraction]);

  // Track render for performance monitoring
  React.useEffect(() => {
    trackRender();
  });

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView 
        style={styles.scrollView} 
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header Section */}
        <View style={styles.header}>
          <Text style={styles.title}>Advanced Components Example</Text>
          <Text style={styles.subtitle}>
            Demonstrating enhanced UI components and performance optimizations
          </Text>
          
          <OptimizedButton
            title={`Switch to ${isDark ? 'Light' : 'Dark'} Mode`}
            onPress={handleThemeToggle}
            variant="outline"
            size="medium"
            hasIcon={true}
            iconName="🌙"
            accessibilityLabel={`Switch to ${isDark ? 'light' : 'dark'} mode`}
            accessibilityHint="Toggles between light and dark theme"
            testID="theme-toggle-button"
          />
        </View>

        {/* Performance Metrics Section */}
        <OptimizedCard
          title="Performance Metrics"
          subtitle="Real-time performance monitoring"
          variant="elevated"
          size="large"
          hasShadow={true}
          containerStyle={styles.metricsCard}
        >
          <View style={styles.metricsGrid}>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>Render Count</Text>
              <Text style={styles.metricValue}>{metrics.renderCount}</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>Avg Render Time</Text>
              <Text style={styles.metricValue}>{metrics.averageRenderTime.toFixed(2)}ms</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>FPS</Text>
              <Text style={styles.metricValue}>{metrics.fps?.toFixed(1) || 'N/A'}</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>Optimization Level</Text>
              <Text style={[styles.metricValue, styles[`optimization${optimization.optimizationLevel}`]]}>
                {optimization.optimizationLevel.toUpperCase()}
              </Text>
            </View>
          </View>

          {optimization.shouldOptimize && (
            <View style={styles.recommendationsContainer}>
              <Text style={styles.recommendationsTitle}>Optimization Recommendations:</Text>
              {optimization.recommendations.map((recommendation, index) => (
                <Text key={index} style={styles.recommendation}>
                  • {recommendation}
                </Text>
              ))}
            </View>
          )}
        </OptimizedCard>

        {/* Form Section */}
        <OptimizedCard
          title="Contact Form"
          subtitle="Enhanced input components with validation"
          variant="filled"
          size="large"
          hasShadow={true}
          containerStyle={styles.formCard}
        >
          <View style={styles.formContainer}>
            <OptimizedInput
              label="Name"
              placeholder="Enter your name"
              value={formData.name}
              onChangeText={(value) => handleInputChange('name', value)}
              isRequired={true}
              variant="outlined"
              size="medium"
              hasIcon={true}
              iconName="👤"
              iconPosition="left"
              accessibilityLabel="Name input field"
              accessibilityHint="Enter your full name"
              testID="name-input"
            />

            <OptimizedInput
              label="Email"
              placeholder="Enter your email"
              value={formData.email}
              onChangeText={(value) => handleInputChange('email', value)}
              isRequired={true}
              variant="outlined"
              size="medium"
              hasIcon={true}
              iconName="📧"
              iconPosition="left"
              keyboardType="email-address"
              autoCapitalize="none"
              accessibilityLabel="Email input field"
              accessibilityHint="Enter your email address"
              testID="email-input"
            />

            <OptimizedInput
              label="Message"
              placeholder="Enter your message"
              value={formData.message}
              onChangeText={(value) => handleInputChange('message', value)}
              isRequired={true}
              variant="outlined"
              size="large"
              hasIcon={true}
              iconName="💬"
              iconPosition="left"
              multiline={true}
              numberOfLines={4}
              accessibilityLabel="Message input field"
              accessibilityHint="Enter your message"
              testID="message-input"
            />

            <View style={styles.buttonContainer}>
              <OptimizedButton
                title="Submit Form"
                onPress={handleSubmit}
                variant="primary"
                size="large"
                isLoading={isSubmitting}
                isFullWidth={true}
                hasIcon={true}
                iconName="🚀"
                iconPosition="right"
                accessibilityLabel="Submit form button"
                accessibilityHint="Submits the contact form"
                testID="submit-button"
              />
            </View>
          </View>
        </OptimizedCard>

        {/* Example Items Section */}
        <OptimizedCard
          title="Example Items"
          subtitle="Interactive cards with different variants"
          variant="outlined"
          size="large"
          hasBorder={true}
          containerStyle={styles.itemsCard}
        >
          <View style={styles.itemsContainer}>
            {EXAMPLE_ITEMS.map((item) => (
              <OptimizedCard
                key={item.id}
                title={item.title}
                subtitle={item.description}
                variant={item.status === 'active' ? 'elevated' : 'outlined'}
                size="medium"
                isPressable={true}
                onPress={() => handleCardPress(item)}
                hasShadow={item.status === 'active'}
                containerStyle={[
                  styles.itemCard,
                  item.status === 'error' && styles.errorCard,
                  item.status === 'inactive' && styles.inactiveCard,
                ]}
                accessibilityLabel={`${item.title} card`}
                accessibilityHint={`Tap to view details about ${item.title}`}
                testID={`item-card-${item.id}`}
              />
            ))}
          </View>
        </OptimizedCard>

        {/* Button Showcase Section */}
        <OptimizedCard
          title="Button Variants"
          subtitle="All available button styles and sizes"
          variant="glass"
          size="large"
          hasShadow={true}
          containerStyle={styles.buttonShowcaseCard}
        >
          <View style={styles.buttonShowcase}>
            <View style={styles.buttonRow}>
              <OptimizedButton
                title="Primary"
                onPress={() => trackInteraction('button_press', { variant: 'primary' })}
                variant="primary"
                size="small"
                testID="primary-button"
              />
              <OptimizedButton
                title="Secondary"
                onPress={() => trackInteraction('button_press', { variant: 'secondary' })}
                variant="secondary"
                size="small"
                testID="secondary-button"
              />
              <OptimizedButton
                title="Outline"
                onPress={() => trackInteraction('button_press', { variant: 'outline' })}
                variant="outline"
                size="small"
                testID="outline-button"
              />
            </View>

            <View style={styles.buttonRow}>
              <OptimizedButton
                title="Success"
                onPress={() => trackInteraction('button_press', { variant: 'success' })}
                variant="success"
                size="medium"
                testID="success-button"
              />
              <OptimizedButton
                title="Warning"
                onPress={() => trackInteraction('button_press', { variant: 'warning' })}
                variant="warning"
                size="medium"
                testID="warning-button"
              />
              <OptimizedButton
                title="Danger"
                onPress={() => trackInteraction('button_press', { variant: 'danger' })}
                variant="danger"
                size="medium"
                testID="danger-button"
              />
            </View>

            <View style={styles.buttonRow}>
              <OptimizedButton
                title="Large Button"
                onPress={() => trackInteraction('button_press', { size: 'large' })}
                variant="primary"
                size="large"
                hasRoundedCorners={true}
                testID="large-button"
              />
              <OptimizedButton
                title="XL Button"
                onPress={() => trackInteraction('button_press', { size: 'xl' })}
                variant="secondary"
                size="xl"
                hasRoundedCorners={true}
                testID="xl-button"
              />
            </View>
          </View>
        </OptimizedCard>
      </ScrollView>
    </SafeAreaView>
  );
}

// ============================================================================
// STYLES
// ============================================================================

function createStyles(theme: any, width: number, height: number) {
  return StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.background,
    },
    scrollView: {
      flex: 1,
    },
    scrollContent: {
      padding: theme.spacing.md,
      paddingBottom: theme.spacing.xxl,
    },
    header: {
      alignItems: 'center',
      marginBottom: theme.spacing.xl,
      padding: theme.spacing.lg,
    },
    title: {
      fontSize: theme.typography.h1.fontSize,
      fontWeight: theme.typography.h1.fontWeight,
      color: theme.colors.text,
      textAlign: 'center',
      marginBottom: theme.spacing.sm,
      includeFontPadding: false,
    },
    subtitle: {
      fontSize: theme.typography.body.fontSize,
      color: theme.colors.textSecondary,
      textAlign: 'center',
      marginBottom: theme.spacing.lg,
      includeFontPadding: false,
    },
    metricsCard: {
      marginBottom: theme.spacing.lg,
    },
    metricsGrid: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      justifyContent: 'space-between',
      marginTop: theme.spacing.md,
    },
    metricItem: {
      width: '48%',
      alignItems: 'center',
      padding: theme.spacing.sm,
      marginBottom: theme.spacing.sm,
    },
    metricLabel: {
      fontSize: theme.typography.caption.fontSize,
      color: theme.colors.textSecondary,
      marginBottom: theme.spacing.xs,
      includeFontPadding: false,
    },
    metricValue: {
      fontSize: theme.typography.h4.fontSize,
      fontWeight: theme.typography.h4.fontWeight,
      color: theme.colors.text,
      includeFontPadding: false,
    },
    optimizationlow: {
      color: theme.colors.success,
    },
    optimizationmedium: {
      color: theme.colors.warning,
    },
    optimizationhigh: {
      color: theme.colors.error,
    },
    recommendationsContainer: {
      marginTop: theme.spacing.md,
      padding: theme.spacing.md,
      backgroundColor: theme.colors.backgroundSecondary,
      borderRadius: theme.borderRadius.md,
    },
    recommendationsTitle: {
      fontSize: theme.typography.h6.fontSize,
      fontWeight: theme.typography.h6.fontWeight,
      color: theme.colors.text,
      marginBottom: theme.spacing.sm,
      includeFontPadding: false,
    },
    recommendation: {
      fontSize: theme.typography.bodySmall.fontSize,
      color: theme.colors.textSecondary,
      marginBottom: theme.spacing.xs,
      includeFontPadding: false,
    },
    formCard: {
      marginBottom: theme.spacing.lg,
    },
    formContainer: {
      marginTop: theme.spacing.md,
    },
    buttonContainer: {
      marginTop: theme.spacing.lg,
    },
    itemsCard: {
      marginBottom: theme.spacing.lg,
    },
    itemsContainer: {
      marginTop: theme.spacing.md,
    },
    itemCard: {
      marginBottom: theme.spacing.sm,
    },
    errorCard: {
      borderColor: theme.colors.error,
    },
    inactiveCard: {
      opacity: 0.6,
    },
    buttonShowcaseCard: {
      marginBottom: theme.spacing.lg,
    },
    buttonShowcase: {
      marginTop: theme.spacing.md,
    },
    buttonRow: {
      flexDirection: 'row',
      justifyContent: 'space-around',
      marginBottom: theme.spacing.md,
    },
  });
}


