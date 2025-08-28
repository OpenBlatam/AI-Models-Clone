import React, { useCallback, useMemo } from 'react';
import { View, Text, StyleSheet, RefreshControl } from 'react-native';
import { FlashList } from '@shopify/flash-list';
import SkeletonPlaceholder from 'react-native-skeleton-placeholder';

interface ListItemConfig<T> {
  key: string;
  render: (item: T, index: number) => React.ReactElement;
  height?: number;
}

interface OptimizedListProps<T> {
  data: T[];
  renderItem: (item: T, index: number) => React.ReactElement;
  keyExtractor: (item: T, index: number) => string;
  isLoading?: boolean;
  isError?: boolean;
  errorMessage?: string;
  emptyMessage?: string;
  estimatedItemSize?: number;
  onEndReached?: () => void;
  onEndReachedThreshold?: number;
  onRefresh?: () => void;
  refreshing?: boolean;
  ListHeaderComponent?: React.ComponentType<any> | React.ReactElement;
  ListFooterComponent?: React.ComponentType<any> | React.ReactElement;
  ListEmptyComponent?: React.ComponentType<any> | React.ReactElement;
  itemConfigs?: ListItemConfig<T>[];
}

// Modular list item components
const createListItemComponent = <T,>(
  config: ListItemConfig<T>
) => {
  return React.memo<{ item: T; index: number }>(({ item, index }) => {
    return (
      <View style={[styles.listItem, { height: config.height }]}>
        {config.render(item, index)}
      </View>
    );
  });
};

// Modular list configurations
const createListConfig = <T,>(config: {
  estimatedItemSize: number;
  onEndReachedThreshold?: number;
  removeClippedSubviews?: boolean;
  maxToRenderPerBatch?: number;
  windowSize?: number;
  initialNumToRender?: number;
  updateCellsBatchingPeriod?: number;
}) => {
  return {
    estimatedItemSize: config.estimatedItemSize,
    onEndReachedThreshold: config.onEndReachedThreshold || 0.5,
    removeClippedSubviews: config.removeClippedSubviews ?? true,
    maxToRenderPerBatch: config.maxToRenderPerBatch || 10,
    windowSize: config.windowSize || 10,
    initialNumToRender: config.initialNumToRender || 5,
    updateCellsBatchingPeriod: config.updateCellsBatchingPeriod || 50,
  };
};

// Modular loading component
const createLoadingComponent = (config: {
  lines?: number;
  lineHeight?: number;
  lineSpacing?: number;
}) => {
  return React.memo(() => (
    <View style={styles.loadingContainer}>
      <SkeletonPlaceholder>
        {Array.from({ length: config.lines || 3 }, (_, index) => (
          <View
            key={index}
            style={{
              width: '100%',
              height: config.lineHeight || 16,
              borderRadius: 4,
              marginBottom: index < (config.lines || 3) - 1 ? (config.lineSpacing || 8) : 0,
            }}
          />
        ))}
      </SkeletonPlaceholder>
    </View>
  ));
};

// Modular error component
const createErrorComponent = (message: string) => {
  return React.memo(() => (
    <View style={styles.errorContainer}>
      <Text style={styles.errorText}>{message}</Text>
    </View>
  ));
};

// Modular empty component
const createEmptyComponent = (message: string) => {
  return React.memo(() => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyText}>{message}</Text>
    </View>
  ));
};

export const OptimizedList = <T,>({
  data,
  renderItem,
  keyExtractor,
  isLoading = false,
  isError = false,
  errorMessage = 'Failed to load data',
  emptyMessage = 'No data available',
  estimatedItemSize = 100,
  onEndReached,
  onEndReachedThreshold,
  onRefresh,
  refreshing = false,
  ListHeaderComponent,
  ListFooterComponent,
  ListEmptyComponent,
  itemConfigs = [],
}: OptimizedListProps<T>) => {
  // Create modular components using iteration
  const listConfig = useMemo(() => createListConfig({
    estimatedItemSize,
    onEndReachedThreshold,
  }), [estimatedItemSize, onEndReachedThreshold]);

  const LoadingComponent = useMemo(() => createLoadingComponent({
    lines: 5,
    lineHeight: 20,
    lineSpacing: 12,
  }), []);

  const ErrorComponent = useMemo(() => createErrorComponent(errorMessage), [errorMessage]);
  const EmptyComponent = useMemo(() => createEmptyComponent(emptyMessage), [emptyMessage]);

  // Create modular list item components using iteration
  const listItemComponents = useMemo(() => {
    return itemConfigs.map(config => createListItemComponent(config));
  }, [itemConfigs]);

  const renderItemCallback = useCallback(({ item, index }: { item: T; index: number }) => {
    // Use modular item components if available
    const matchingConfig = itemConfigs.find(config => config.key === keyExtractor(item, index));
    if (matchingConfig) {
      const ItemComponent = createListItemComponent(matchingConfig);
      return <ItemComponent item={item} index={index} />;
    }
    
    return renderItem(item, index);
  }, [renderItem, keyExtractor, itemConfigs]);

  const keyExtractorCallback = useCallback((item: T, index: number) => {
    return keyExtractor(item, index);
  }, [keyExtractor]);

  const refreshControl = useMemo(() => {
    if (!onRefresh) return undefined;
    
    return (
      <RefreshControl
        refreshing={refreshing}
        onRefresh={onRefresh}
        tintColor="#007AFF"
        colors={['#007AFF']}
      />
    );
  }, [refreshing, onRefresh]);

  // Modular rendering logic
  if (isLoading) {
    return <LoadingComponent />;
  }

  if (isError) {
    return <ErrorComponent />;
  }

  return (
    <FlashList
      data={data}
      renderItem={renderItemCallback}
      keyExtractor={keyExtractorCallback}
      estimatedItemSize={listConfig.estimatedItemSize}
      onEndReached={onEndReached}
      onEndReachedThreshold={listConfig.onEndReachedThreshold}
      refreshControl={refreshControl}
      ListHeaderComponent={ListHeaderComponent}
      ListFooterComponent={ListFooterComponent}
      ListEmptyComponent={ListEmptyComponent || EmptyComponent}
      showsVerticalScrollIndicator={false}
      removeClippedSubviews={listConfig.removeClippedSubviews}
      maxToRenderPerBatch={listConfig.maxToRenderPerBatch}
      windowSize={listConfig.windowSize}
      initialNumToRender={listConfig.initialNumToRender}
      updateCellsBatchingPeriod={listConfig.updateCellsBatchingPeriod}
      contentContainerStyle={styles.listContent}
    />
  );
};

// Modular list factories
export const createListFactory = <T,>() => {
  return {
    withItemConfig: (config: ListItemConfig<T>) => {
      return (props: Omit<OptimizedListProps<T>, 'itemConfigs'>) => (
        <OptimizedList {...props} itemConfigs={[config]} />
      );
    },
    withMultipleItemConfigs: (configs: ListItemConfig<T>[]) => {
      return (props: Omit<OptimizedListProps<T>, 'itemConfigs'>) => (
        <OptimizedList {...props} itemConfigs={configs} />
      );
    },
    withLoadingConfig: (loadingConfig: { lines: number; lineHeight: number; lineSpacing: number }) => {
      return (props: OptimizedListProps<T>) => (
        <OptimizedList
          {...props}
          isLoading={props.isLoading}
          ListEmptyComponent={createLoadingComponent(loadingConfig)}
        />
      );
    },
    withErrorConfig: (errorConfig: { message: string; retryAction?: () => void }) => {
      return (props: OptimizedListProps<T>) => (
        <OptimizedList
          {...props}
          isError={props.isError}
          errorMessage={errorConfig.message}
          ListEmptyComponent={createErrorComponent(errorConfig.message)}
        />
      );
    },
  };
};

// Example usage of modular list configurations
export const createUserList = createListFactory<{ id: string; name: string; avatar: string }>();

export const UserList = createUserList.withItemConfig({
  key: 'user-item',
  render: (user) => (
    <View style={styles.userItem}>
      <Text style={styles.userName}>{user.name}</Text>
    </View>
  ),
  height: 60,
});

const styles = StyleSheet.create({
  listContent: {
    flexGrow: 1,
  },
  listItem: {
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  loadingContainer: {
    padding: 16,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  errorText: {
    fontSize: 16,
    color: '#FF3B30',
    textAlign: 'center',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  emptyText: {
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
  },
  userItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  userName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#000000',
  },
}); 