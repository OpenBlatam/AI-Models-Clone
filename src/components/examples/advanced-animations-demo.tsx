import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { GestureCard } from '../animations/gesture-card';
import { MorphingButton } from '../animations/morphing-button';
import { StaggeredList } from '../animations/staggered-list';
import { LoadingSpinner } from '../animations/loading-spinner';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';
import { useOptimizedPerformance } from '../../hooks/performance/use-optimized-performance';

interface DemoItem {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
}

const mockData: DemoItem[] = Array.from({ length: 20 }, (_, i) => ({
  id: `item-${i}`,
  title: `Advanced Item ${i + 1}`,
  description: `This is a demonstration of advanced animations and gestures in React Native. Item ${i + 1} showcases various interaction patterns.`,
  imageUrl: `https://picsum.photos/300/200?random=${i}`,
}));

export function AdvancedAnimationsDemo() {
  const { theme } = useAppStore();
  const { t } = useI18n();
  const { trackInteraction } = useOptimizedPerformance();
  
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [data, setData] = useState(mockData);
  const [selectedVariant, setSelectedVariant] = useState<'primary' | 'secondary' | 'success' | 'warning' | 'error'>('primary');
  const [selectedSize, setSelectedSize] = useState<'small' | 'medium' | 'large'>('medium');
  const [selectedShape, setSelectedShape] = useState<'rectangle' | 'rounded' | 'pill' | 'circle'>('rounded');

  const handleCardDismiss = useCallback((id: string) => {
    trackInteraction('card_dismissed');
    setData(prev => prev.filter(item => item.id !== id));
    Alert.alert('Card Dismissed', `Card ${id} has been dismissed`);
  }, [trackInteraction]);

  const handleCardPress = useCallback((id: string) => {
    trackInteraction('card_pressed');
    Alert.alert('Card Pressed', `You pressed card ${id}`);
  }, [trackInteraction]);

  const handleCardLongPress = useCallback((id: string) => {
    trackInteraction('card_long_pressed');
    Alert.alert('Long Press', `Long press detected on card ${id}`);
  }, [trackInteraction]);

  const handleAsyncPress = useCallback(async () => {
    trackInteraction('async_button_pressed');
    setLoading(true);
    
    try {
      // Simulate async operation
      await new Promise(resolve => setTimeout(resolve, 2000));
      Alert.alert('Success', 'Async operation completed successfully!');
    } catch (error) {
      Alert.alert('Error', 'Async operation failed');
    } finally {
      setLoading(false);
    }
  }, [trackInteraction]);

  const handleRefresh = useCallback(async () => {
    trackInteraction('list_refreshed');
    setRefreshing(true);
    
    try {
      // Simulate refresh
      await new Promise(resolve => setTimeout(resolve, 1000));
      setData(mockData);
    } finally {
      setRefreshing(false);
    }
  }, [trackInteraction]);

  const handleVariantChange = useCallback((variant: typeof selectedVariant) => {
    trackInteraction('variant_changed');
    setSelectedVariant(variant);
  }, [trackInteraction]);

  const handleSizeChange = useCallback((size: typeof selectedSize) => {
    trackInteraction('size_changed');
    setSelectedSize(size);
  }, [trackInteraction]);

  const handleShapeChange = useCallback((shape: typeof selectedShape) => {
    trackInteraction('shape_changed');
    setSelectedShape(shape);
  }, [trackInteraction]);

  const renderDemoItem = useCallback(({ item }: { item: DemoItem }) => (
    <GestureCard
      key={item.id}
      id={item.id}
      title={item.title}
      description={item.description}
      imageUrl={item.imageUrl}
      onDismiss={handleCardDismiss}
      onPress={handleCardPress}
      onLongPress={handleCardLongPress}
      testID={`demo-card-${item.id}`}
    />
  ), [handleCardDismiss, handleCardPress, handleCardLongPress]);

  const renderVariantButton = useCallback((variant: typeof selectedVariant, label: string) => (
    <MorphingButton
      key={variant}
      title={label}
      variant={variant}
      size="small"
      shape="rounded"
      onPress={() => handleVariantChange(variant)}
      testID={`variant-${variant}`}
    />
  ), [handleVariantChange]);

  const renderSizeButton = useCallback((size: typeof selectedSize, label: string) => (
    <MorphingButton
      key={size}
      title={label}
      variant="secondary"
      size={size}
      shape="rounded"
      onPress={() => handleSizeChange(size)}
      testID={`size-${size}`}
    />
  ), [handleSizeChange]);

  const renderShapeButton = useCallback((shape: typeof selectedShape, label: string) => (
    <MorphingButton
      key={shape}
      title={label}
      variant="secondary"
      size="small"
      shape={shape}
      onPress={() => handleShapeChange(shape)}
      testID={`shape-${shape}`}
    />
  ), [handleShapeChange]);

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={[styles.title, { color: theme.colors.text }]}>
            {t('animations.title')}
          </Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            {t('animations.subtitle')}
          </Text>
        </View>

        {/* Loading Spinners Demo */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            {t('animations.loadingSpinners')}
          </Text>
          
          <View style={styles.spinnerContainer}>
            <View style={styles.spinnerGroup}>
              <LoadingSpinner variant="spinner" size="small" testID="spinner-small" />
              <Text style={[styles.spinnerLabel, { color: theme.colors.textSecondary }]}>
                {t('animations.spinner')}
              </Text>
            </View>
            
            <View style={styles.spinnerGroup}>
              <LoadingSpinner variant="dots" size="medium" testID="dots-medium" />
              <Text style={[styles.spinnerLabel, { color: theme.colors.textSecondary }]}>
                {t('animations.dots')}
              </Text>
            </View>
            
            <View style={styles.spinnerGroup}>
              <LoadingSpinner variant="pulse" size="large" testID="pulse-large" />
              <Text style={[styles.spinnerLabel, { color: theme.colors.textSecondary }]}>
                {t('animations.pulse')}
              </Text>
            </View>
            
            <View style={styles.spinnerGroup}>
              <LoadingSpinner variant="wave" size="medium" testID="wave-medium" />
              <Text style={[styles.spinnerLabel, { color: theme.colors.textSecondary }]}>
                {t('animations.wave')}
              </Text>
            </View>
            
            <View style={styles.spinnerGroup}>
              <LoadingSpinner variant="bounce" size="small" testID="bounce-small" />
              <Text style={[styles.spinnerLabel, { color: theme.colors.textSecondary }]}>
                {t('animations.bounce')}
              </Text>
            </View>
          </View>
        </View>

        {/* Morphing Buttons Demo */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            {t('animations.morphingButtons')}
          </Text>
          
          {/* Variant Selection */}
          <View style={styles.buttonGroup}>
            <Text style={[styles.groupLabel, { color: theme.colors.textSecondary }]}>
              {t('animations.variants')}
            </Text>
            <View style={styles.buttonRow}>
              {renderVariantButton('primary', t('animations.primary'))}
              {renderVariantButton('secondary', t('animations.secondary'))}
              {renderVariantButton('success', t('animations.success'))}
              {renderVariantButton('warning', t('animations.warning'))}
              {renderVariantButton('error', t('animations.error'))}
            </View>
          </View>

          {/* Size Selection */}
          <View style={styles.buttonGroup}>
            <Text style={[styles.groupLabel, { color: theme.colors.textSecondary }]}>
              {t('animations.sizes')}
            </Text>
            <View style={styles.buttonRow}>
              {renderSizeButton('small', t('animations.small'))}
              {renderSizeButton('medium', t('animations.medium'))}
              {renderSizeButton('large', t('animations.large'))}
            </View>
          </View>

          {/* Shape Selection */}
          <View style={styles.buttonGroup}>
            <Text style={[styles.groupLabel, { color: theme.colors.textSecondary }]}>
              {t('animations.shapes')}
            </Text>
            <View style={styles.buttonRow}>
              {renderShapeButton('rectangle', t('animations.rectangle'))}
              {renderShapeButton('rounded', t('animations.rounded'))}
              {renderShapeButton('pill', t('animations.pill'))}
              {renderShapeButton('circle', t('animations.circle'))}
            </View>
          </View>

          {/* Demo Button */}
          <View style={styles.demoButtonContainer}>
            <MorphingButton
              title={t('animations.asyncDemo')}
              variant={selectedVariant}
              size={selectedSize}
              shape={selectedShape}
              onPressAsync={handleAsyncPress}
              loading={loading}
              testID="demo-async-button"
            />
          </View>
        </View>

        {/* Gesture Cards Demo */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            {t('animations.gestureCards')}
          </Text>
          <Text style={[styles.sectionDescription, { color: theme.colors.textSecondary }]}>
            {t('animations.gestureCardsDescription')}
          </Text>
        </View>

        {/* Staggered List */}
        <View style={styles.listContainer}>
          <StaggeredList
            data={data}
            renderItem={renderDemoItem}
            keyExtractor={(item) => item.id}
            onRefresh={handleRefresh}
            refreshing={refreshing}
            testID="staggered-demo-list"
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 20,
  },
  header: {
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  sectionDescription: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 16,
  },
  spinnerContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 20,
  },
  spinnerGroup: {
    alignItems: 'center',
    gap: 8,
  },
  spinnerLabel: {
    fontSize: 12,
    fontWeight: '500',
  },
  buttonGroup: {
    marginBottom: 20,
  },
  groupLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
  },
  buttonRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  demoButtonContainer: {
    alignItems: 'center',
    marginTop: 20,
  },
  listContainer: {
    flex: 1,
    minHeight: 400,
  },
});
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { GestureCard } from '../animations/gesture-card';
import { MorphingButton } from '../animations/morphing-button';
import { StaggeredList } from '../animations/staggered-list';
import { LoadingSpinner } from '../animations/loading-spinner';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';
import { useOptimizedPerformance } from '../../hooks/performance/use-optimized-performance';

interface DemoItem {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
}

const mockData: DemoItem[] = Array.from({ length: 20 }, (_, i) => ({
  id: `item-${i}`,
  title: `Advanced Item ${i + 1}`,
  description: `This is a demonstration of advanced animations and gestures in React Native. Item ${i + 1} showcases various interaction patterns.`,
  imageUrl: `https://picsum.photos/300/200?random=${i}`,
}));

export function AdvancedAnimationsDemo() {
  const { theme } = useAppStore();
  const { t } = useI18n();
  const { trackInteraction } = useOptimizedPerformance();
  
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [data, setData] = useState(mockData);
  const [selectedVariant, setSelectedVariant] = useState<'primary' | 'secondary' | 'success' | 'warning' | 'error'>('primary');
  const [selectedSize, setSelectedSize] = useState<'small' | 'medium' | 'large'>('medium');
  const [selectedShape, setSelectedShape] = useState<'rectangle' | 'rounded' | 'pill' | 'circle'>('rounded');

  const handleCardDismiss = useCallback((id: string) => {
    trackInteraction('card_dismissed');
    setData(prev => prev.filter(item => item.id !== id));
    Alert.alert('Card Dismissed', `Card ${id} has been dismissed`);
  }, [trackInteraction]);

  const handleCardPress = useCallback((id: string) => {
    trackInteraction('card_pressed');
    Alert.alert('Card Pressed', `You pressed card ${id}`);
  }, [trackInteraction]);

  const handleCardLongPress = useCallback((id: string) => {
    trackInteraction('card_long_pressed');
    Alert.alert('Long Press', `Long press detected on card ${id}`);
  }, [trackInteraction]);

  const handleAsyncPress = useCallback(async () => {
    trackInteraction('async_button_pressed');
    setLoading(true);
    
    try {
      // Simulate async operation
      await new Promise(resolve => setTimeout(resolve, 2000));
      Alert.alert('Success', 'Async operation completed successfully!');
    } catch (error) {
      Alert.alert('Error', 'Async operation failed');
    } finally {
      setLoading(false);
    }
  }, [trackInteraction]);

  const handleRefresh = useCallback(async () => {
    trackInteraction('list_refreshed');
    setRefreshing(true);
    
    try {
      // Simulate refresh
      await new Promise(resolve => setTimeout(resolve, 1000));
      setData(mockData);
    } finally {
      setRefreshing(false);
    }
  }, [trackInteraction]);

  const handleVariantChange = useCallback((variant: typeof selectedVariant) => {
    trackInteraction('variant_changed');
    setSelectedVariant(variant);
  }, [trackInteraction]);

  const handleSizeChange = useCallback((size: typeof selectedSize) => {
    trackInteraction('size_changed');
    setSelectedSize(size);
  }, [trackInteraction]);

  const handleShapeChange = useCallback((shape: typeof selectedShape) => {
    trackInteraction('shape_changed');
    setSelectedShape(shape);
  }, [trackInteraction]);

  const renderDemoItem = useCallback(({ item }: { item: DemoItem }) => (
    <GestureCard
      key={item.id}
      id={item.id}
      title={item.title}
      description={item.description}
      imageUrl={item.imageUrl}
      onDismiss={handleCardDismiss}
      onPress={handleCardPress}
      onLongPress={handleCardLongPress}
      testID={`demo-card-${item.id}`}
    />
  ), [handleCardDismiss, handleCardPress, handleCardLongPress]);

  const renderVariantButton = useCallback((variant: typeof selectedVariant, label: string) => (
    <MorphingButton
      key={variant}
      title={label}
      variant={variant}
      size="small"
      shape="rounded"
      onPress={() => handleVariantChange(variant)}
      testID={`variant-${variant}`}
    />
  ), [handleVariantChange]);

  const renderSizeButton = useCallback((size: typeof selectedSize, label: string) => (
    <MorphingButton
      key={size}
      title={label}
      variant="secondary"
      size={size}
      shape="rounded"
      onPress={() => handleSizeChange(size)}
      testID={`size-${size}`}
    />
  ), [handleSizeChange]);

  const renderShapeButton = useCallback((shape: typeof selectedShape, label: string) => (
    <MorphingButton
      key={shape}
      title={label}
      variant="secondary"
      size="small"
      shape={shape}
      onPress={() => handleShapeChange(shape)}
      testID={`shape-${shape}`}
    />
  ), [handleShapeChange]);

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={[styles.title, { color: theme.colors.text }]}>
            {t('animations.title')}
          </Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            {t('animations.subtitle')}
          </Text>
        </View>

        {/* Loading Spinners Demo */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            {t('animations.loadingSpinners')}
          </Text>
          
          <View style={styles.spinnerContainer}>
            <View style={styles.spinnerGroup}>
              <LoadingSpinner variant="spinner" size="small" testID="spinner-small" />
              <Text style={[styles.spinnerLabel, { color: theme.colors.textSecondary }]}>
                {t('animations.spinner')}
              </Text>
            </View>
            
            <View style={styles.spinnerGroup}>
              <LoadingSpinner variant="dots" size="medium" testID="dots-medium" />
              <Text style={[styles.spinnerLabel, { color: theme.colors.textSecondary }]}>
                {t('animations.dots')}
              </Text>
            </View>
            
            <View style={styles.spinnerGroup}>
              <LoadingSpinner variant="pulse" size="large" testID="pulse-large" />
              <Text style={[styles.spinnerLabel, { color: theme.colors.textSecondary }]}>
                {t('animations.pulse')}
              </Text>
            </View>
            
            <View style={styles.spinnerGroup}>
              <LoadingSpinner variant="wave" size="medium" testID="wave-medium" />
              <Text style={[styles.spinnerLabel, { color: theme.colors.textSecondary }]}>
                {t('animations.wave')}
              </Text>
            </View>
            
            <View style={styles.spinnerGroup}>
              <LoadingSpinner variant="bounce" size="small" testID="bounce-small" />
              <Text style={[styles.spinnerLabel, { color: theme.colors.textSecondary }]}>
                {t('animations.bounce')}
              </Text>
            </View>
          </View>
        </View>

        {/* Morphing Buttons Demo */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            {t('animations.morphingButtons')}
          </Text>
          
          {/* Variant Selection */}
          <View style={styles.buttonGroup}>
            <Text style={[styles.groupLabel, { color: theme.colors.textSecondary }]}>
              {t('animations.variants')}
            </Text>
            <View style={styles.buttonRow}>
              {renderVariantButton('primary', t('animations.primary'))}
              {renderVariantButton('secondary', t('animations.secondary'))}
              {renderVariantButton('success', t('animations.success'))}
              {renderVariantButton('warning', t('animations.warning'))}
              {renderVariantButton('error', t('animations.error'))}
            </View>
          </View>

          {/* Size Selection */}
          <View style={styles.buttonGroup}>
            <Text style={[styles.groupLabel, { color: theme.colors.textSecondary }]}>
              {t('animations.sizes')}
            </Text>
            <View style={styles.buttonRow}>
              {renderSizeButton('small', t('animations.small'))}
              {renderSizeButton('medium', t('animations.medium'))}
              {renderSizeButton('large', t('animations.large'))}
            </View>
          </View>

          {/* Shape Selection */}
          <View style={styles.buttonGroup}>
            <Text style={[styles.groupLabel, { color: theme.colors.textSecondary }]}>
              {t('animations.shapes')}
            </Text>
            <View style={styles.buttonRow}>
              {renderShapeButton('rectangle', t('animations.rectangle'))}
              {renderShapeButton('rounded', t('animations.rounded'))}
              {renderShapeButton('pill', t('animations.pill'))}
              {renderShapeButton('circle', t('animations.circle'))}
            </View>
          </View>

          {/* Demo Button */}
          <View style={styles.demoButtonContainer}>
            <MorphingButton
              title={t('animations.asyncDemo')}
              variant={selectedVariant}
              size={selectedSize}
              shape={selectedShape}
              onPressAsync={handleAsyncPress}
              loading={loading}
              testID="demo-async-button"
            />
          </View>
        </View>

        {/* Gesture Cards Demo */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            {t('animations.gestureCards')}
          </Text>
          <Text style={[styles.sectionDescription, { color: theme.colors.textSecondary }]}>
            {t('animations.gestureCardsDescription')}
          </Text>
        </View>

        {/* Staggered List */}
        <View style={styles.listContainer}>
          <StaggeredList
            data={data}
            renderItem={renderDemoItem}
            keyExtractor={(item) => item.id}
            onRefresh={handleRefresh}
            refreshing={refreshing}
            testID="staggered-demo-list"
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 20,
  },
  header: {
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  sectionDescription: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 16,
  },
  spinnerContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 20,
  },
  spinnerGroup: {
    alignItems: 'center',
    gap: 8,
  },
  spinnerLabel: {
    fontSize: 12,
    fontWeight: '500',
  },
  buttonGroup: {
    marginBottom: 20,
  },
  groupLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
  },
  buttonRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  demoButtonContainer: {
    alignItems: 'center',
    marginTop: 20,
  },
  listContainer: {
    flex: 1,
    minHeight: 400,
  },
});


