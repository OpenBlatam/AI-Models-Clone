import React, { useCallback, useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ListRenderItem,
  RefreshControl,
} from 'react-native';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
  withDelay,
  runOnJS,
} from 'react-native-reanimated';
import { useStaggeredAnimation } from '../../lib/animations/advanced-animations';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';

interface StaggeredListProps<T> {
  data: T[];
  renderItem: ListRenderItem<T>;
  keyExtractor: (item: T, index: number) => string;
  onRefresh?: () => Promise<void>;
  refreshing?: boolean;
  onEndReached?: () => void;
  onEndReachedThreshold?: number;
  ListEmptyComponent?: React.ComponentType<any> | React.ReactElement | null;
  ListHeaderComponent?: React.ComponentType<any> | React.ReactElement | null;
  ListFooterComponent?: React.ComponentType<any> | React.ReactElement | null;
  numColumns?: number;
  horizontal?: boolean;
  showsVerticalScrollIndicator?: boolean;
  showsHorizontalScrollIndicator?: boolean;
  contentContainerStyle?: any;
  style?: any;
  testID?: string;
}

export function StaggeredList<T>({
  data,
  renderItem,
  keyExtractor,
  onRefresh,
  refreshing = false,
  onEndReached,
  onEndReachedThreshold = 0.5,
  ListEmptyComponent,
  ListHeaderComponent,
  ListFooterComponent,
  numColumns = 1,
  horizontal = false,
  showsVerticalScrollIndicator = true,
  showsHorizontalScrollIndicator = false,
  contentContainerStyle,
  style,
  testID,
}: StaggeredListProps<T>) {
  const { theme } = useAppStore();
  const { t } = useI18n();
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [visibleItems, setVisibleItems] = useState<Set<string>>(new Set());

  // Staggered animation
  const { animateIn, animateOut, getAnimatedStyle } = useStaggeredAnimation(
    data.length,
    100
  );

  // List animation
  const listOpacity = useSharedValue(0);
  const listTranslateY = useSharedValue(50);

  useEffect(() => {
    if (data.length > 0 && isInitialLoad) {
      // Animate list in
      listOpacity.value = withTiming(1, { duration: 300 });
      listTranslateY.value = withSpring(0, { damping: 15, stiffness: 150 });
      
      // Animate items in with stagger
      setTimeout(() => {
        animateIn();
        setIsInitialLoad(false);
      }, 200);
    }
  }, [data.length, isInitialLoad, listOpacity, listTranslateY, animateIn]);

  const handleRefresh = useCallback(async () => {
    if (onRefresh) {
      // Animate out
      animateOut();
      listOpacity.value = withTiming(0.5, { duration: 200 });
      
      try {
        await onRefresh();
      } finally {
        // Animate back in
        listOpacity.value = withTiming(1, { duration: 200 });
        setTimeout(() => {
          animateIn();
        }, 100);
      }
    }
  }, [onRefresh, animateOut, animateIn, listOpacity]);

  const handleEndReached = useCallback(() => {
    if (onEndReached) {
      onEndReached();
    }
  }, [onEndReached]);

  const handleViewableItemsChanged = useCallback(({ viewableItems }: any) => {
    const newVisibleItems = new Set(viewableItems.map((item: any) => item.key));
    setVisibleItems(newVisibleItems);
  }, []);

  const animatedListStyle = useAnimatedStyle(() => ({
    opacity: listOpacity.value,
    transform: [{ translateY: listTranslateY.value }],
  }));

  const renderAnimatedItem: ListRenderItem<T> = useCallback(({ item, index }) => {
    const key = keyExtractor(item, index);
    const isVisible = visibleItems.has(key);
    
    const animatedStyle = getAnimatedStyle(index);
    
    return (
      <Animated.View style={animatedStyle}>
        {renderItem({ item, index })}
      </Animated.View>
    );
  }, [keyExtractor, visibleItems, getAnimatedStyle, renderItem]);

  const refreshControl = onRefresh ? (
    <RefreshControl
      refreshing={refreshing}
      onRefresh={handleRefresh}
      tintColor={theme.colors.primary}
      colors={[theme.colors.primary]}
      progressBackgroundColor={theme.colors.surface}
    />
  ) : undefined;

  return (
    <Animated.View style={[styles.container, style, animatedListStyle]}>
      <FlatList
        testID={testID}
        data={data}
        renderItem={renderAnimatedItem}
        keyExtractor={keyExtractor}
        onRefresh={handleRefresh}
        refreshing={refreshing}
        onEndReached={handleEndReached}
        onEndReachedThreshold={onEndReachedThreshold}
        onViewableItemsChanged={handleViewableItemsChanged}
        viewabilityConfig={{
          itemVisiblePercentThreshold: 50,
        }}
        ListEmptyComponent={ListEmptyComponent}
        ListHeaderComponent={ListHeaderComponent}
        ListFooterComponent={ListFooterComponent}
        numColumns={numColumns}
        horizontal={horizontal}
        showsVerticalScrollIndicator={showsVerticalScrollIndicator}
        showsHorizontalScrollIndicator={showsHorizontalScrollIndicator}
        contentContainerStyle={[
          styles.contentContainer,
          contentContainerStyle,
        ]}
        refreshControl={refreshControl}
        removeClippedSubviews={true}
        maxToRenderPerBatch={10}
        updateCellsBatchingPeriod={50}
        initialNumToRender={10}
        windowSize={10}
      />
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  contentContainer: {
    flexGrow: 1,
  },
});
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ListRenderItem,
  RefreshControl,
} from 'react-native';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
  withDelay,
  runOnJS,
} from 'react-native-reanimated';
import { useStaggeredAnimation } from '../../lib/animations/advanced-animations';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';

interface StaggeredListProps<T> {
  data: T[];
  renderItem: ListRenderItem<T>;
  keyExtractor: (item: T, index: number) => string;
  onRefresh?: () => Promise<void>;
  refreshing?: boolean;
  onEndReached?: () => void;
  onEndReachedThreshold?: number;
  ListEmptyComponent?: React.ComponentType<any> | React.ReactElement | null;
  ListHeaderComponent?: React.ComponentType<any> | React.ReactElement | null;
  ListFooterComponent?: React.ComponentType<any> | React.ReactElement | null;
  numColumns?: number;
  horizontal?: boolean;
  showsVerticalScrollIndicator?: boolean;
  showsHorizontalScrollIndicator?: boolean;
  contentContainerStyle?: any;
  style?: any;
  testID?: string;
}

export function StaggeredList<T>({
  data,
  renderItem,
  keyExtractor,
  onRefresh,
  refreshing = false,
  onEndReached,
  onEndReachedThreshold = 0.5,
  ListEmptyComponent,
  ListHeaderComponent,
  ListFooterComponent,
  numColumns = 1,
  horizontal = false,
  showsVerticalScrollIndicator = true,
  showsHorizontalScrollIndicator = false,
  contentContainerStyle,
  style,
  testID,
}: StaggeredListProps<T>) {
  const { theme } = useAppStore();
  const { t } = useI18n();
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [visibleItems, setVisibleItems] = useState<Set<string>>(new Set());

  // Staggered animation
  const { animateIn, animateOut, getAnimatedStyle } = useStaggeredAnimation(
    data.length,
    100
  );

  // List animation
  const listOpacity = useSharedValue(0);
  const listTranslateY = useSharedValue(50);

  useEffect(() => {
    if (data.length > 0 && isInitialLoad) {
      // Animate list in
      listOpacity.value = withTiming(1, { duration: 300 });
      listTranslateY.value = withSpring(0, { damping: 15, stiffness: 150 });
      
      // Animate items in with stagger
      setTimeout(() => {
        animateIn();
        setIsInitialLoad(false);
      }, 200);
    }
  }, [data.length, isInitialLoad, listOpacity, listTranslateY, animateIn]);

  const handleRefresh = useCallback(async () => {
    if (onRefresh) {
      // Animate out
      animateOut();
      listOpacity.value = withTiming(0.5, { duration: 200 });
      
      try {
        await onRefresh();
      } finally {
        // Animate back in
        listOpacity.value = withTiming(1, { duration: 200 });
        setTimeout(() => {
          animateIn();
        }, 100);
      }
    }
  }, [onRefresh, animateOut, animateIn, listOpacity]);

  const handleEndReached = useCallback(() => {
    if (onEndReached) {
      onEndReached();
    }
  }, [onEndReached]);

  const handleViewableItemsChanged = useCallback(({ viewableItems }: any) => {
    const newVisibleItems = new Set(viewableItems.map((item: any) => item.key));
    setVisibleItems(newVisibleItems);
  }, []);

  const animatedListStyle = useAnimatedStyle(() => ({
    opacity: listOpacity.value,
    transform: [{ translateY: listTranslateY.value }],
  }));

  const renderAnimatedItem: ListRenderItem<T> = useCallback(({ item, index }) => {
    const key = keyExtractor(item, index);
    const isVisible = visibleItems.has(key);
    
    const animatedStyle = getAnimatedStyle(index);
    
    return (
      <Animated.View style={animatedStyle}>
        {renderItem({ item, index })}
      </Animated.View>
    );
  }, [keyExtractor, visibleItems, getAnimatedStyle, renderItem]);

  const refreshControl = onRefresh ? (
    <RefreshControl
      refreshing={refreshing}
      onRefresh={handleRefresh}
      tintColor={theme.colors.primary}
      colors={[theme.colors.primary]}
      progressBackgroundColor={theme.colors.surface}
    />
  ) : undefined;

  return (
    <Animated.View style={[styles.container, style, animatedListStyle]}>
      <FlatList
        testID={testID}
        data={data}
        renderItem={renderAnimatedItem}
        keyExtractor={keyExtractor}
        onRefresh={handleRefresh}
        refreshing={refreshing}
        onEndReached={handleEndReached}
        onEndReachedThreshold={onEndReachedThreshold}
        onViewableItemsChanged={handleViewableItemsChanged}
        viewabilityConfig={{
          itemVisiblePercentThreshold: 50,
        }}
        ListEmptyComponent={ListEmptyComponent}
        ListHeaderComponent={ListHeaderComponent}
        ListFooterComponent={ListFooterComponent}
        numColumns={numColumns}
        horizontal={horizontal}
        showsVerticalScrollIndicator={showsVerticalScrollIndicator}
        showsHorizontalScrollIndicator={showsHorizontalScrollIndicator}
        contentContainerStyle={[
          styles.contentContainer,
          contentContainerStyle,
        ]}
        refreshControl={refreshControl}
        removeClippedSubviews={true}
        maxToRenderPerBatch={10}
        updateCellsBatchingPeriod={50}
        initialNumToRender={10}
        windowSize={10}
      />
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  contentContainer: {
    flexGrow: 1,
  },
});


