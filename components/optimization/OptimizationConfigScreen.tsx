import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Switch, TouchableOpacity, Alert } from 'react-native';
import { OptimizedTranslatedText } from '../i18n-components/OptimizedTranslatedText';
import { appOptimizer } from '../../utils/optimization/AppOptimizer';
import { componentOptimizer } from '../../utils/optimization/ComponentOptimizer';
import { bundleOptimizer } from '../../utils/optimization/BundleOptimizer';

interface OptimizationConfigScreenProps {
  onSave?: () => void;
  onCancel?: () => void;
  style?: any;
}

interface ConfigSectionProps {
  title: string;
  children: React.ReactNode;
}

const ConfigSection: React.FC<ConfigSectionProps> = ({ title, children }) => (
  <View style={styles.section}>
    <Text style={styles.sectionTitle}>{title}</Text>
    {children}
  </View>
);

interface ConfigItemProps {
  title: string;
  description: string;
  value: boolean;
  onValueChange: (value: boolean) => void;
}

const ConfigItem: React.FC<ConfigItemProps> = ({ title, description, value, onValueChange }) => (
  <View style={styles.configItem}>
    <View style={styles.configInfo}>
      <Text style={styles.configTitle}>{title}</Text>
      <Text style={styles.configDescription}>{description}</Text>
    </View>
    <Switch
      value={value}
      onValueChange={onValueChange}
      trackColor={{ false: '#e0e0e0', true: '#007AFF' }}
      thumbColor={value ? '#fff' : '#f4f3f4'}
    />
  </View>
);

interface SliderConfigItemProps {
  title: string;
  description: string;
  value: number;
  min: number;
  max: number;
  step: number;
  unit: string;
  onValueChange: (value: number) => void;
}

const SliderConfigItem: React.FC<SliderConfigItemProps> = ({
  title,
  description,
  value,
  min,
  max,
  step,
  unit,
  onValueChange,
}) => (
  <View style={styles.configItem}>
    <View style={styles.configInfo}>
      <Text style={styles.configTitle}>{title}</Text>
      <Text style={styles.configDescription}>{description}</Text>
      <Text style={styles.configValue}>{value} {unit}</Text>
    </View>
    <View style={styles.sliderContainer}>
      <TouchableOpacity
        style={styles.sliderButton}
        onPress={() => onValueChange(Math.max(min, value - step))}
      >
        <Text style={styles.sliderButtonText}>-</Text>
      </TouchableOpacity>
      <View style={styles.sliderTrack}>
        <View style={[styles.sliderFill, { width: `${((value - min) / (max - min)) * 100}%` }]} />
      </View>
      <TouchableOpacity
        style={styles.sliderButton}
        onPress={() => onValueChange(Math.min(max, value + step))}
      >
        <Text style={styles.sliderButtonText}>+</Text>
      </TouchableOpacity>
    </View>
  </View>
);

export const OptimizationConfigScreen: React.FC<OptimizationConfigScreenProps> = ({
  onSave,
  onCancel,
  style,
}) => {
  const [appConfig, setAppConfig] = useState(appOptimizer.getConfig());
  const [componentConfig, setComponentConfig] = useState(componentOptimizer.getConfig());
  const [bundleConfig, setBundleConfig] = useState(bundleOptimizer.getConfig());
  const [hasChanges, setHasChanges] = useState(false);

  // Track changes
  useEffect(() => {
    setHasChanges(true);
  }, [appConfig, componentConfig, bundleConfig]);

  // Update app config
  const updateAppConfig = (updates: Partial<typeof appConfig>) => {
    setAppConfig(prev => ({ ...prev, ...updates }));
  };

  // Update component config
  const updateComponentConfig = (updates: Partial<typeof componentConfig>) => {
    setComponentConfig(prev => ({ ...prev, ...updates }));
  };

  // Update bundle config
  const updateBundleConfig = (updates: Partial<typeof bundleConfig>) => {
    setBundleConfig(prev => ({ ...prev, ...updates }));
  };

  // Save configuration
  const handleSave = async () => {
    try {
      // Apply configurations
      appOptimizer.updateConfig(appConfig);
      componentOptimizer.updateConfig(componentConfig);
      bundleOptimizer.updateConfig(bundleConfig);

      Alert.alert(
        'Configuration Saved',
        'Optimization settings have been updated successfully.',
        [{ text: 'OK' }]
      );

      setHasChanges(false);
      onSave?.();
    } catch (error) {
      console.error('Failed to save configuration:', error);
      Alert.alert(
        'Save Failed',
        'Failed to save optimization settings. Please try again.',
        [{ text: 'OK' }]
      );
    }
  };

  // Reset to defaults
  const handleReset = () => {
    Alert.alert(
      'Reset Configuration',
      'Are you sure you want to reset all optimization settings to defaults?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Reset',
          style: 'destructive',
          onPress: () => {
            setAppConfig(appOptimizer.getConfig());
            setComponentConfig(componentOptimizer.getConfig());
            setBundleConfig(bundleOptimizer.getConfig());
            setHasChanges(false);
          },
        },
      ]
    );
  };

  return (
    <ScrollView style={[styles.container, style]} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <OptimizedTranslatedText
          translationKey="optimization.config.title"
          style={styles.title}
        />
        <Text style={styles.subtitle}>
          Configure optimization settings for maximum performance
        </Text>
      </View>

      {/* App Optimization Configuration */}
      <ConfigSection title="App Optimization">
        <ConfigItem
          title="Bundle Optimization"
          description="Enable bundle size optimization and code splitting"
          value={appConfig.enableBundleOptimization}
          onValueChange={(value) => updateAppConfig({ enableBundleOptimization: value })}
        />

        <ConfigItem
          title="Memory Optimization"
          description="Enable memory usage optimization and garbage collection"
          value={appConfig.enableMemoryOptimization}
          onValueChange={(value) => updateAppConfig({ enableMemoryOptimization: value })}
        />

        <ConfigItem
          title="Network Optimization"
          description="Enable network request optimization and caching"
          value={appConfig.enableNetworkOptimization}
          onValueChange={(value) => updateAppConfig({ enableNetworkOptimization: value })}
        />

        <ConfigItem
          title="Image Optimization"
          description="Enable image compression and lazy loading"
          value={appConfig.enableImageOptimization}
          onValueChange={(value) => updateAppConfig({ enableImageOptimization: value })}
        />

        <ConfigItem
          title="Cache Optimization"
          description="Enable intelligent caching strategies"
          value={appConfig.enableCaching}
          onValueChange={(value) => updateAppConfig({ enableCaching: value })}
        />

        <ConfigItem
          title="Code Splitting"
          description="Enable dynamic code splitting for better performance"
          value={appConfig.enableCodeSplitting}
          onValueChange={(value) => updateAppConfig({ enableCodeSplitting: value })}
        />

        <ConfigItem
          title="Lazy Loading"
          description="Enable lazy loading for components and resources"
          value={appConfig.enableLazyLoading}
          onValueChange={(value) => updateAppConfig({ enableLazyLoading: value })}
        />

        <ConfigItem
          title="Compression"
          description="Enable bundle compression for smaller file sizes"
          value={appConfig.enableCompression}
          onValueChange={(value) => updateAppConfig({ enableCompression: value })}
        />

        <SliderConfigItem
          title="Max Memory Usage"
          description="Maximum allowed memory usage for the application"
          value={appConfig.maxMemoryUsage}
          min={50}
          max={200}
          step={10}
          unit="MB"
          onValueChange={(value) => updateAppConfig({ maxMemoryUsage: value })}
        />

        <SliderConfigItem
          title="Max Bundle Size"
          description="Maximum allowed bundle size for the application"
          value={appConfig.maxBundleSize}
          min={5}
          max={20}
          step={1}
          unit="MB"
          onValueChange={(value) => updateAppConfig({ maxBundleSize: value })}
        />

        <SliderConfigItem
          title="Compression Level"
          description="Compression level for bundle optimization (0-9)"
          value={appConfig.compressionLevel}
          min={0}
          max={9}
          step={1}
          unit=""
          onValueChange={(value) => updateAppConfig({ compressionLevel: value })}
        />
      </ConfigSection>

      {/* Component Optimization Configuration */}
      <ConfigSection title="Component Optimization">
        <ConfigItem
          title="Component Memoization"
          description="Enable automatic component memoization"
          value={componentConfig.enableMemoization}
          onValueChange={(value) => updateComponentConfig({ enableMemoization: value })}
        />

        <ConfigItem
          title="Callback Optimization"
          description="Enable useCallback optimization for event handlers"
          value={componentConfig.enableCallbackOptimization}
          onValueChange={(value) => updateComponentConfig({ enableCallbackOptimization: value })}
        />

        <ConfigItem
          title="Render Optimization"
          description="Enable render performance monitoring and optimization"
          value={componentConfig.enableRenderOptimization}
          onValueChange={(value) => updateComponentConfig({ enableRenderOptimization: value })}
        />

        <ConfigItem
          title="Props Optimization"
          description="Enable props optimization and memoization"
          value={componentConfig.enablePropsOptimization}
          onValueChange={(value) => updateComponentConfig({ enablePropsOptimization: value })}
        />

        <ConfigItem
          title="State Optimization"
          description="Enable state optimization and immutable updates"
          value={componentConfig.enableStateOptimization}
          onValueChange={(value) => updateComponentConfig({ enableStateOptimization: value })}
        />

        <ConfigItem
          title="Auto Optimization"
          description="Enable automatic optimization for all components"
          value={componentConfig.enableAutoOptimization}
          onValueChange={(value) => updateComponentConfig({ enableAutoOptimization: value })}
        />

        <SliderConfigItem
          title="Max Render Time"
          description="Maximum allowed render time for components (60fps target)"
          value={componentConfig.maxRenderTime}
          min={8}
          max={33}
          step={1}
          unit="ms"
          onValueChange={(value) => updateComponentConfig({ maxRenderTime: value })}
        />

        <SliderConfigItem
          title="Max Re-render Count"
          description="Maximum allowed re-render count before optimization"
          value={componentConfig.maxReRenderCount}
          min={5}
          max={20}
          step={1}
          unit=""
          onValueChange={(value) => updateComponentConfig({ maxReRenderCount: value })}
        />
      </ConfigSection>

      {/* Bundle Optimization Configuration */}
      <ConfigSection title="Bundle Optimization">
        <ConfigItem
          title="Tree Shaking"
          description="Enable removal of unused code and dependencies"
          value={bundleConfig.enableTreeShaking}
          onValueChange={(value) => updateBundleConfig({ enableTreeShaking: value })}
        />

        <ConfigItem
          title="Code Splitting"
          description="Enable bundle splitting for better loading performance"
          value={bundleConfig.enableCodeSplitting}
          onValueChange={(value) => updateBundleConfig({ enableCodeSplitting: value })}
        />

        <ConfigItem
          title="Compression"
          description="Enable bundle compression for smaller file sizes"
          value={bundleConfig.enableCompression}
          onValueChange={(value) => updateBundleConfig({ enableCompression: value })}
        />

        <ConfigItem
          title="Minification"
          description="Enable code minification for smaller bundle size"
          value={bundleConfig.enableMinification}
          onValueChange={(value) => updateBundleConfig({ enableMinification: value })}
        />

        <ConfigItem
          title="Source Maps"
          description="Enable source maps for debugging (increases bundle size)"
          value={bundleConfig.enableSourceMaps}
          onValueChange={(value) => updateBundleConfig({ enableSourceMaps: value })}
        />

        <ConfigItem
          title="Split Chunks"
          description="Enable automatic chunk splitting for better caching"
          value={bundleConfig.splitChunks}
          onValueChange={(value) => updateBundleConfig({ splitChunks: value })}
        />

        <ConfigItem
          title="Lazy Load Modules"
          description="Enable lazy loading for non-critical modules"
          value={bundleConfig.lazyLoadModules}
          onValueChange={(value) => updateBundleConfig({ lazyLoadModules: value })}
        />

        <SliderConfigItem
          title="Max Bundle Size"
          description="Maximum allowed bundle size before optimization"
          value={bundleConfig.maxBundleSize}
          min={5}
          max={20}
          step={1}
          unit="MB"
          onValueChange={(value) => updateBundleConfig({ maxBundleSize: value })}
        />

        <SliderConfigItem
          title="Compression Level"
          description="Compression level for bundle optimization (0-9)"
          value={bundleConfig.compressionLevel}
          min={0}
          max={9}
          step={1}
          unit=""
          onValueChange={(value) => updateBundleConfig({ compressionLevel: value })}
        />
      </ConfigSection>

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <TouchableOpacity
          style={[styles.saveButton, !hasChanges && styles.disabledButton]}
          onPress={handleSave}
          disabled={!hasChanges}
        >
          <OptimizedTranslatedText
            translationKey="optimization.config.save"
            style={styles.saveButtonText}
          />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.resetButton}
          onPress={handleReset}
        >
          <OptimizedTranslatedText
            translationKey="optimization.config.reset"
            style={styles.resetButtonText}
          />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.cancelButton}
          onPress={onCancel}
        >
          <OptimizedTranslatedText
            translationKey="optimization.config.cancel"
            style={styles.cancelButtonText}
          />
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
  },
  section: {
    backgroundColor: '#fff',
    marginBottom: 10,
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 15,
  },
  configItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  configInfo: {
    flex: 1,
    marginRight: 15,
  },
  configTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5,
  },
  configDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  configValue: {
    fontSize: 12,
    color: '#007AFF',
    fontWeight: '600',
  },
  sliderContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    minWidth: 120,
  },
  sliderButton: {
    width: 30,
    height: 30,
    backgroundColor: '#007AFF',
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sliderButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  sliderTrack: {
    flex: 1,
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
    marginHorizontal: 10,
    overflow: 'hidden',
  },
  sliderFill: {
    height: '100%',
    backgroundColor: '#007AFF',
  },
  actionButtons: {
    padding: 20,
    backgroundColor: '#fff',
    marginBottom: 20,
  },
  saveButton: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10,
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  resetButton: {
    backgroundColor: '#FF9500',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10,
  },
  resetButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  cancelButton: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#007AFF',
    alignItems: 'center',
  },
  cancelButtonText: {
    color: '#007AFF',
    fontSize: 16,
    fontWeight: '600',
  },
}); 