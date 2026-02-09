import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  Alert,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useOfflineSync } from '../../hooks/offline/use-offline-sync';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';
import { MorphingButton } from '../animations/morphing-button';
import { OfflineIndicator } from '../offline/offline-indicator';
import { ConflictResolver } from '../offline/conflict-resolver';

interface DemoItem {
  id: string;
  title: string;
  description: string;
  timestamp: number;
}

export function OfflineDemo() {
  const { theme } = useAppStore();
  const { t } = useI18n();
  const {
    isOnline,
    isSyncing,
    pendingActions,
    failedActions,
    syncProgress,
    hasConflicts,
    conflicts,
    localDataCount,
    sync,
    forceSync,
    clearPendingActions,
    createData,
    updateData,
    deleteData,
    getAllData,
    queueAction,
  } = useOfflineSync();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [showConflictResolver, setShowConflictResolver] = useState(false);
  const [selectedItem, setSelectedItem] = useState<DemoItem | null>(null);

  const handleCreateItem = useCallback(async () => {
    if (!title.trim() || !description.trim()) {
      Alert.alert(t('offline.error'), t('offline.fillFields'));
      return;
    }

    try {
      const id = await createData('demo-item', {
        title: title.trim(),
        description: description.trim(),
        timestamp: Date.now(),
      });

      setTitle('');
      setDescription('');
      Alert.alert(t('offline.success'), t('offline.itemCreated', { id }));
    } catch (error) {
      Alert.alert(t('offline.error'), t('offline.createFailed'));
    }
  }, [title, description, createData, t]);

  const handleUpdateItem = useCallback(async (item: DemoItem) => {
    try {
      await updateData(item.id, {
        ...item,
        title: `${item.title} (Updated)`,
        timestamp: Date.now(),
      });
      Alert.alert(t('offline.success'), t('offline.itemUpdated'));
    } catch (error) {
      Alert.alert(t('offline.error'), t('offline.updateFailed'));
    }
  }, [updateData, t]);

  const handleDeleteItem = useCallback(async (item: DemoItem) => {
    Alert.alert(
      t('offline.confirmDelete'),
      t('offline.deleteMessage', { title: item.title }),
      [
        { text: t('offline.cancel'), style: 'cancel' },
        {
          text: t('offline.delete'),
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteData(item.id);
              Alert.alert(t('offline.success'), t('offline.itemDeleted'));
            } catch (error) {
              Alert.alert(t('offline.error'), t('offline.deleteFailed'));
            }
          },
        },
      ]
    );
  }, [deleteData, t]);

  const handleSync = useCallback(async () => {
    try {
      const result = await sync();
      Alert.alert(
        t('offline.syncCompleted'),
        t('offline.syncResult', {
          synced: result.synced,
          conflicts: result.conflicts,
          errors: result.errors,
        })
      );
    } catch (error) {
      Alert.alert(t('offline.error'), t('offline.syncFailed'));
    }
  }, [sync, t]);

  const handleQueueAction = useCallback(async () => {
    try {
      const actionId = await queueAction('demo-action', {
        message: 'This is a demo action',
        timestamp: Date.now(),
      }, 1);
      Alert.alert(t('offline.success'), t('offline.actionQueued', { id: actionId }));
    } catch (error) {
      Alert.alert(t('offline.error'), t('offline.queueFailed'));
    }
  }, [queueAction, t]);

  const handleClearPending = useCallback(async () => {
    Alert.alert(
      t('offline.confirmClear'),
      t('offline.clearMessage'),
      [
        { text: t('offline.cancel'), style: 'cancel' },
        {
          text: t('offline.clear'),
          style: 'destructive',
          onPress: async () => {
            try {
              await clearPendingActions();
              Alert.alert(t('offline.success'), t('offline.actionsCleared'));
            } catch (error) {
              Alert.alert(t('offline.error'), t('offline.clearFailed'));
            }
          },
        },
      ]
    );
  }, [clearPendingActions, t]);

  const renderItem = useCallback((item: DemoItem) => (
    <View
      key={item.id}
      style={[
        styles.item,
        { backgroundColor: theme.colors.surface, borderColor: theme.colors.border },
      ]}
    >
      <View style={styles.itemHeader}>
        <Text style={[styles.itemTitle, { color: theme.colors.text }]}>
          {item.title}
        </Text>
        <Text style={[styles.itemTimestamp, { color: theme.colors.textSecondary }]}>
          {new Date(item.timestamp).toLocaleString()}
        </Text>
      </View>
      
      <Text style={[styles.itemDescription, { color: theme.colors.textSecondary }]}>
        {item.description}
      </Text>
      
      <View style={styles.itemActions}>
        <MorphingButton
          title={t('offline.update')}
          variant="secondary"
          size="small"
          onPress={() => handleUpdateItem(item)}
          testID={`update-item-${item.id}`}
        />
        
        <MorphingButton
          title={t('offline.delete')}
          variant="error"
          size="small"
          onPress={() => handleDeleteItem(item)}
          testID={`delete-item-${item.id}`}
        />
      </View>
    </View>
  ), [theme.colors, handleUpdateItem, handleDeleteItem, t]);

  const items = getAllData('demo-item') as DemoItem[];

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <OfflineIndicator showDetails={true} testID="offline-indicator" />
      
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={[styles.title, { color: theme.colors.text }]}>
            {t('offline.title')}
          </Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            {t('offline.subtitle')}
          </Text>
        </View>

        {/* Status */}
        <View style={styles.statusSection}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            {t('offline.status')}
          </Text>
          
          <View style={styles.statusGrid}>
            <View style={[styles.statusItem, { backgroundColor: theme.colors.surface }]}>
              <Text style={[styles.statusLabel, { color: theme.colors.textSecondary }]}>
                {t('offline.connection')}
              </Text>
              <Text style={[
                styles.statusValue,
                { color: isOnline ? theme.colors.success : theme.colors.error }
              ]}>
                {isOnline ? t('offline.online') : t('offline.offline')}
              </Text>
            </View>
            
            <View style={[styles.statusItem, { backgroundColor: theme.colors.surface }]}>
              <Text style={[styles.statusLabel, { color: theme.colors.textSecondary }]}>
                {t('offline.syncing')}
              </Text>
              <Text style={[
                styles.statusValue,
                { color: isSyncing ? theme.colors.warning : theme.colors.text }
              ]}>
                {isSyncing ? t('offline.yes') : t('offline.no')}
              </Text>
            </View>
            
            <View style={[styles.statusItem, { backgroundColor: theme.colors.surface }]}>
              <Text style={[styles.statusLabel, { color: theme.colors.textSecondary }]}>
                {t('offline.pendingActions')}
              </Text>
              <Text style={[styles.statusValue, { color: theme.colors.text }]}>
                {pendingActions}
              </Text>
            </View>
            
            <View style={[styles.statusItem, { backgroundColor: theme.colors.surface }]}>
              <Text style={[styles.statusLabel, { color: theme.colors.textSecondary }]}>
                {t('offline.failedActions')}
              </Text>
              <Text style={[styles.statusValue, { color: theme.colors.text }]}>
                {failedActions}
              </Text>
            </View>
            
            <View style={[styles.statusItem, { backgroundColor: theme.colors.surface }]}>
              <Text style={[styles.statusLabel, { color: theme.colors.textSecondary }]}>
                {t('offline.conflicts')}
              </Text>
              <Text style={[styles.statusValue, { color: theme.colors.text }]}>
                {conflicts.length}
              </Text>
            </View>
            
            <View style={[styles.statusItem, { backgroundColor: theme.colors.surface }]}>
              <Text style={[styles.statusLabel, { color: theme.colors.textSecondary }]}>
                {t('offline.localData')}
              </Text>
              <Text style={[styles.statusValue, { color: theme.colors.text }]}>
                {localDataCount}
              </Text>
            </View>
          </View>
        </View>

        {/* Actions */}
        <View style={styles.actionsSection}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            {t('offline.actions')}
          </Text>
          
          <View style={styles.actionButtons}>
            <MorphingButton
              title={t('offline.sync')}
              variant="primary"
              size="medium"
              onPress={handleSync}
              loading={isSyncing}
              testID="sync-button"
            />
            
            <MorphingButton
              title={t('offline.forceSync')}
              variant="secondary"
              size="medium"
              onPress={forceSync}
              testID="force-sync-button"
            />
            
            <MorphingButton
              title={t('offline.queueAction')}
              variant="warning"
              size="medium"
              onPress={handleQueueAction}
              testID="queue-action-button"
            />
            
            <MorphingButton
              title={t('offline.clearPending')}
              variant="error"
              size="medium"
              onPress={handleClearPending}
              disabled={pendingActions === 0}
              testID="clear-pending-button"
            />
          </View>
        </View>

        {/* Create Item */}
        <View style={styles.createSection}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            {t('offline.createItem')}
          </Text>
          
          <TextInput
            style={[
              styles.input,
              { 
                backgroundColor: theme.colors.surface, 
                borderColor: theme.colors.border,
                color: theme.colors.text 
              }
            ]}
            placeholder={t('offline.titlePlaceholder')}
            placeholderTextColor={theme.colors.textSecondary}
            value={title}
            onChangeText={setTitle}
            testID="title-input"
          />
          
          <TextInput
            style={[
              styles.input,
              styles.textArea,
              { 
                backgroundColor: theme.colors.surface, 
                borderColor: theme.colors.border,
                color: theme.colors.text 
              }
            ]}
            placeholder={t('offline.descriptionPlaceholder')}
            placeholderTextColor={theme.colors.textSecondary}
            value={description}
            onChangeText={setDescription}
            multiline
            numberOfLines={3}
            testID="description-input"
          />
          
          <MorphingButton
            title={t('offline.create')}
            variant="success"
            size="large"
            onPress={handleCreateItem}
            testID="create-item-button"
          />
        </View>

        {/* Items List */}
        <View style={styles.itemsSection}>
          <View style={styles.itemsHeader}>
            <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
              {t('offline.items')}
            </Text>
            <Text style={[styles.itemsCount, { color: theme.colors.textSecondary }]}>
              {items.length} {t('offline.itemsCount')}
            </Text>
          </View>
          
          {items.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={[styles.emptyText, { color: theme.colors.textSecondary }]}>
                {t('offline.noItems')}
              </Text>
            </View>
          ) : (
            items.map(renderItem)
          )}
        </View>

        {/* Conflicts */}
        {hasConflicts && (
          <View style={styles.conflictsSection}>
            <Text style={[styles.sectionTitle, { color: theme.colors.error }]}>
              {t('offline.conflictsDetected')}
            </Text>
            <Text style={[styles.conflictsText, { color: theme.colors.textSecondary }]}>
              {t('offline.conflictsMessage', { count: conflicts.length })}
            </Text>
            
            <MorphingButton
              title={t('offline.resolveConflicts')}
              variant="error"
              size="large"
              onPress={() => setShowConflictResolver(true)}
              testID="resolve-conflicts-button"
            />
          </View>
        )}
      </ScrollView>

      <ConflictResolver
        visible={showConflictResolver}
        onClose={() => setShowConflictResolver(false)}
        testID="conflict-resolver"
      />
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
  statusSection: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  statusGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  statusItem: {
    flex: 1,
    minWidth: '45%',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  statusLabel: {
    fontSize: 12,
    fontWeight: '500',
    marginBottom: 4,
  },
  statusValue: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  actionsSection: {
    padding: 20,
  },
  actionButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  createSection: {
    padding: 20,
  },
  input: {
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
    fontSize: 16,
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  itemsSection: {
    padding: 20,
  },
  itemsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  itemsCount: {
    fontSize: 14,
  },
  emptyState: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    textAlign: 'center',
  },
  item: {
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 12,
  },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  itemTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1,
  },
  itemTimestamp: {
    fontSize: 12,
    marginLeft: 8,
  },
  itemDescription: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 12,
  },
  itemActions: {
    flexDirection: 'row',
    gap: 8,
  },
  conflictsSection: {
    padding: 20,
    margin: 20,
    borderRadius: 12,
    backgroundColor: '#fff3cd',
    borderWidth: 1,
    borderColor: '#ffeaa7',
  },
  conflictsText: {
    fontSize: 14,
    marginBottom: 16,
  },
});
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  Alert,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useOfflineSync } from '../../hooks/offline/use-offline-sync';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';
import { MorphingButton } from '../animations/morphing-button';
import { OfflineIndicator } from '../offline/offline-indicator';
import { ConflictResolver } from '../offline/conflict-resolver';

interface DemoItem {
  id: string;
  title: string;
  description: string;
  timestamp: number;
}

export function OfflineDemo() {
  const { theme } = useAppStore();
  const { t } = useI18n();
  const {
    isOnline,
    isSyncing,
    pendingActions,
    failedActions,
    syncProgress,
    hasConflicts,
    conflicts,
    localDataCount,
    sync,
    forceSync,
    clearPendingActions,
    createData,
    updateData,
    deleteData,
    getAllData,
    queueAction,
  } = useOfflineSync();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [showConflictResolver, setShowConflictResolver] = useState(false);
  const [selectedItem, setSelectedItem] = useState<DemoItem | null>(null);

  const handleCreateItem = useCallback(async () => {
    if (!title.trim() || !description.trim()) {
      Alert.alert(t('offline.error'), t('offline.fillFields'));
      return;
    }

    try {
      const id = await createData('demo-item', {
        title: title.trim(),
        description: description.trim(),
        timestamp: Date.now(),
      });

      setTitle('');
      setDescription('');
      Alert.alert(t('offline.success'), t('offline.itemCreated', { id }));
    } catch (error) {
      Alert.alert(t('offline.error'), t('offline.createFailed'));
    }
  }, [title, description, createData, t]);

  const handleUpdateItem = useCallback(async (item: DemoItem) => {
    try {
      await updateData(item.id, {
        ...item,
        title: `${item.title} (Updated)`,
        timestamp: Date.now(),
      });
      Alert.alert(t('offline.success'), t('offline.itemUpdated'));
    } catch (error) {
      Alert.alert(t('offline.error'), t('offline.updateFailed'));
    }
  }, [updateData, t]);

  const handleDeleteItem = useCallback(async (item: DemoItem) => {
    Alert.alert(
      t('offline.confirmDelete'),
      t('offline.deleteMessage', { title: item.title }),
      [
        { text: t('offline.cancel'), style: 'cancel' },
        {
          text: t('offline.delete'),
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteData(item.id);
              Alert.alert(t('offline.success'), t('offline.itemDeleted'));
            } catch (error) {
              Alert.alert(t('offline.error'), t('offline.deleteFailed'));
            }
          },
        },
      ]
    );
  }, [deleteData, t]);

  const handleSync = useCallback(async () => {
    try {
      const result = await sync();
      Alert.alert(
        t('offline.syncCompleted'),
        t('offline.syncResult', {
          synced: result.synced,
          conflicts: result.conflicts,
          errors: result.errors,
        })
      );
    } catch (error) {
      Alert.alert(t('offline.error'), t('offline.syncFailed'));
    }
  }, [sync, t]);

  const handleQueueAction = useCallback(async () => {
    try {
      const actionId = await queueAction('demo-action', {
        message: 'This is a demo action',
        timestamp: Date.now(),
      }, 1);
      Alert.alert(t('offline.success'), t('offline.actionQueued', { id: actionId }));
    } catch (error) {
      Alert.alert(t('offline.error'), t('offline.queueFailed'));
    }
  }, [queueAction, t]);

  const handleClearPending = useCallback(async () => {
    Alert.alert(
      t('offline.confirmClear'),
      t('offline.clearMessage'),
      [
        { text: t('offline.cancel'), style: 'cancel' },
        {
          text: t('offline.clear'),
          style: 'destructive',
          onPress: async () => {
            try {
              await clearPendingActions();
              Alert.alert(t('offline.success'), t('offline.actionsCleared'));
            } catch (error) {
              Alert.alert(t('offline.error'), t('offline.clearFailed'));
            }
          },
        },
      ]
    );
  }, [clearPendingActions, t]);

  const renderItem = useCallback((item: DemoItem) => (
    <View
      key={item.id}
      style={[
        styles.item,
        { backgroundColor: theme.colors.surface, borderColor: theme.colors.border },
      ]}
    >
      <View style={styles.itemHeader}>
        <Text style={[styles.itemTitle, { color: theme.colors.text }]}>
          {item.title}
        </Text>
        <Text style={[styles.itemTimestamp, { color: theme.colors.textSecondary }]}>
          {new Date(item.timestamp).toLocaleString()}
        </Text>
      </View>
      
      <Text style={[styles.itemDescription, { color: theme.colors.textSecondary }]}>
        {item.description}
      </Text>
      
      <View style={styles.itemActions}>
        <MorphingButton
          title={t('offline.update')}
          variant="secondary"
          size="small"
          onPress={() => handleUpdateItem(item)}
          testID={`update-item-${item.id}`}
        />
        
        <MorphingButton
          title={t('offline.delete')}
          variant="error"
          size="small"
          onPress={() => handleDeleteItem(item)}
          testID={`delete-item-${item.id}`}
        />
      </View>
    </View>
  ), [theme.colors, handleUpdateItem, handleDeleteItem, t]);

  const items = getAllData('demo-item') as DemoItem[];

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <OfflineIndicator showDetails={true} testID="offline-indicator" />
      
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={[styles.title, { color: theme.colors.text }]}>
            {t('offline.title')}
          </Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            {t('offline.subtitle')}
          </Text>
        </View>

        {/* Status */}
        <View style={styles.statusSection}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            {t('offline.status')}
          </Text>
          
          <View style={styles.statusGrid}>
            <View style={[styles.statusItem, { backgroundColor: theme.colors.surface }]}>
              <Text style={[styles.statusLabel, { color: theme.colors.textSecondary }]}>
                {t('offline.connection')}
              </Text>
              <Text style={[
                styles.statusValue,
                { color: isOnline ? theme.colors.success : theme.colors.error }
              ]}>
                {isOnline ? t('offline.online') : t('offline.offline')}
              </Text>
            </View>
            
            <View style={[styles.statusItem, { backgroundColor: theme.colors.surface }]}>
              <Text style={[styles.statusLabel, { color: theme.colors.textSecondary }]}>
                {t('offline.syncing')}
              </Text>
              <Text style={[
                styles.statusValue,
                { color: isSyncing ? theme.colors.warning : theme.colors.text }
              ]}>
                {isSyncing ? t('offline.yes') : t('offline.no')}
              </Text>
            </View>
            
            <View style={[styles.statusItem, { backgroundColor: theme.colors.surface }]}>
              <Text style={[styles.statusLabel, { color: theme.colors.textSecondary }]}>
                {t('offline.pendingActions')}
              </Text>
              <Text style={[styles.statusValue, { color: theme.colors.text }]}>
                {pendingActions}
              </Text>
            </View>
            
            <View style={[styles.statusItem, { backgroundColor: theme.colors.surface }]}>
              <Text style={[styles.statusLabel, { color: theme.colors.textSecondary }]}>
                {t('offline.failedActions')}
              </Text>
              <Text style={[styles.statusValue, { color: theme.colors.text }]}>
                {failedActions}
              </Text>
            </View>
            
            <View style={[styles.statusItem, { backgroundColor: theme.colors.surface }]}>
              <Text style={[styles.statusLabel, { color: theme.colors.textSecondary }]}>
                {t('offline.conflicts')}
              </Text>
              <Text style={[styles.statusValue, { color: theme.colors.text }]}>
                {conflicts.length}
              </Text>
            </View>
            
            <View style={[styles.statusItem, { backgroundColor: theme.colors.surface }]}>
              <Text style={[styles.statusLabel, { color: theme.colors.textSecondary }]}>
                {t('offline.localData')}
              </Text>
              <Text style={[styles.statusValue, { color: theme.colors.text }]}>
                {localDataCount}
              </Text>
            </View>
          </View>
        </View>

        {/* Actions */}
        <View style={styles.actionsSection}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            {t('offline.actions')}
          </Text>
          
          <View style={styles.actionButtons}>
            <MorphingButton
              title={t('offline.sync')}
              variant="primary"
              size="medium"
              onPress={handleSync}
              loading={isSyncing}
              testID="sync-button"
            />
            
            <MorphingButton
              title={t('offline.forceSync')}
              variant="secondary"
              size="medium"
              onPress={forceSync}
              testID="force-sync-button"
            />
            
            <MorphingButton
              title={t('offline.queueAction')}
              variant="warning"
              size="medium"
              onPress={handleQueueAction}
              testID="queue-action-button"
            />
            
            <MorphingButton
              title={t('offline.clearPending')}
              variant="error"
              size="medium"
              onPress={handleClearPending}
              disabled={pendingActions === 0}
              testID="clear-pending-button"
            />
          </View>
        </View>

        {/* Create Item */}
        <View style={styles.createSection}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            {t('offline.createItem')}
          </Text>
          
          <TextInput
            style={[
              styles.input,
              { 
                backgroundColor: theme.colors.surface, 
                borderColor: theme.colors.border,
                color: theme.colors.text 
              }
            ]}
            placeholder={t('offline.titlePlaceholder')}
            placeholderTextColor={theme.colors.textSecondary}
            value={title}
            onChangeText={setTitle}
            testID="title-input"
          />
          
          <TextInput
            style={[
              styles.input,
              styles.textArea,
              { 
                backgroundColor: theme.colors.surface, 
                borderColor: theme.colors.border,
                color: theme.colors.text 
              }
            ]}
            placeholder={t('offline.descriptionPlaceholder')}
            placeholderTextColor={theme.colors.textSecondary}
            value={description}
            onChangeText={setDescription}
            multiline
            numberOfLines={3}
            testID="description-input"
          />
          
          <MorphingButton
            title={t('offline.create')}
            variant="success"
            size="large"
            onPress={handleCreateItem}
            testID="create-item-button"
          />
        </View>

        {/* Items List */}
        <View style={styles.itemsSection}>
          <View style={styles.itemsHeader}>
            <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
              {t('offline.items')}
            </Text>
            <Text style={[styles.itemsCount, { color: theme.colors.textSecondary }]}>
              {items.length} {t('offline.itemsCount')}
            </Text>
          </View>
          
          {items.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={[styles.emptyText, { color: theme.colors.textSecondary }]}>
                {t('offline.noItems')}
              </Text>
            </View>
          ) : (
            items.map(renderItem)
          )}
        </View>

        {/* Conflicts */}
        {hasConflicts && (
          <View style={styles.conflictsSection}>
            <Text style={[styles.sectionTitle, { color: theme.colors.error }]}>
              {t('offline.conflictsDetected')}
            </Text>
            <Text style={[styles.conflictsText, { color: theme.colors.textSecondary }]}>
              {t('offline.conflictsMessage', { count: conflicts.length })}
            </Text>
            
            <MorphingButton
              title={t('offline.resolveConflicts')}
              variant="error"
              size="large"
              onPress={() => setShowConflictResolver(true)}
              testID="resolve-conflicts-button"
            />
          </View>
        )}
      </ScrollView>

      <ConflictResolver
        visible={showConflictResolver}
        onClose={() => setShowConflictResolver(false)}
        testID="conflict-resolver"
      />
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
  statusSection: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  statusGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  statusItem: {
    flex: 1,
    minWidth: '45%',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  statusLabel: {
    fontSize: 12,
    fontWeight: '500',
    marginBottom: 4,
  },
  statusValue: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  actionsSection: {
    padding: 20,
  },
  actionButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  createSection: {
    padding: 20,
  },
  input: {
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
    fontSize: 16,
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  itemsSection: {
    padding: 20,
  },
  itemsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  itemsCount: {
    fontSize: 14,
  },
  emptyState: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    textAlign: 'center',
  },
  item: {
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 12,
  },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  itemTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1,
  },
  itemTimestamp: {
    fontSize: 12,
    marginLeft: 8,
  },
  itemDescription: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 12,
  },
  itemActions: {
    flexDirection: 'row',
    gap: 8,
  },
  conflictsSection: {
    padding: 20,
    margin: 20,
    borderRadius: 12,
    backgroundColor: '#fff3cd',
    borderWidth: 1,
    borderColor: '#ffeaa7',
  },
  conflictsText: {
    fontSize: 14,
    marginBottom: 16,
  },
});


