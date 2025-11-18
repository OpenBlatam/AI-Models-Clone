import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useOfflineSync } from '../../hooks/offline/use-offline-sync';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';
import { MorphingButton } from '../animations/morphing-button';

interface ConflictResolverProps {
  visible: boolean;
  onClose: () => void;
  testID?: string;
}

export function ConflictResolver({ visible, onClose, testID }: ConflictResolverProps) {
  const { theme } = useAppStore();
  const { t } = useI18n();
  const { conflicts, resolveConflict } = useOfflineSync();
  
  const [selectedResolution, setSelectedResolution] = useState<{
    [key: string]: 'server' | 'client' | 'merge';
  }>({});

  const handleResolutionSelect = useCallback((conflictId: string, resolution: 'server' | 'client' | 'merge') => {
    setSelectedResolution(prev => ({
      ...prev,
      [conflictId]: resolution,
    }));
  }, []);

  const handleResolveAll = useCallback(async () => {
    try {
      for (const conflict of conflicts) {
        const resolution = selectedResolution[conflict.id];
        if (resolution) {
          await resolveConflict(conflict.id, resolution);
        }
      }
      
      setSelectedResolution({});
      onClose();
      Alert.alert(t('conflicts.resolved'), t('conflicts.allResolved'));
    } catch (error) {
      Alert.alert(t('conflicts.error'), t('conflicts.resolveFailed'));
    }
  }, [conflicts, selectedResolution, resolveConflict, onClose, t]);

  const handleResolveSingle = useCallback(async (conflictId: string) => {
    const resolution = selectedResolution[conflictId];
    if (!resolution) {
      Alert.alert(t('conflicts.error'), t('conflicts.selectResolution'));
      return;
    }

    try {
      await resolveConflict(conflictId, resolution);
      setSelectedResolution(prev => {
        const newState = { ...prev };
        delete newState[conflictId];
        return newState;
      });
      
      if (conflicts.length === 1) {
        onClose();
      }
    } catch (error) {
      Alert.alert(t('conflicts.error'), t('conflicts.resolveFailed'));
    }
  }, [selectedResolution, resolveConflict, conflicts.length, onClose, t]);

  const renderConflictItem = useCallback((conflict: any) => {
    const resolution = selectedResolution[conflict.id];
    
    return (
      <View
        key={conflict.id}
        style={[
          styles.conflictItem,
          { backgroundColor: theme.colors.surface, borderColor: theme.colors.border },
        ]}
      >
        <Text style={[styles.conflictTitle, { color: theme.colors.text }]}>
          {t('conflicts.item', { id: conflict.id })}
        </Text>
        
        <Text style={[styles.conflictType, { color: theme.colors.textSecondary }]}>
          {t('conflicts.type', { type: conflict.type })}
        </Text>

        <View style={styles.resolutionButtons}>
          <TouchableOpacity
            style={[
              styles.resolutionButton,
              { borderColor: theme.colors.border },
              resolution === 'server' && { backgroundColor: theme.colors.primary },
            ]}
            onPress={() => handleResolutionSelect(conflict.id, 'server')}
          >
            <Text
              style={[
                styles.resolutionButtonText,
                { color: theme.colors.text },
                resolution === 'server' && { color: 'white' },
              ]}
            >
              {t('conflicts.server')}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.resolutionButton,
              { borderColor: theme.colors.border },
              resolution === 'client' && { backgroundColor: theme.colors.primary },
            ]}
            onPress={() => handleResolutionSelect(conflict.id, 'client')}
          >
            <Text
              style={[
                styles.resolutionButtonText,
                { color: theme.colors.text },
                resolution === 'client' && { color: 'white' },
              ]}
            >
              {t('conflicts.client')}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.resolutionButton,
              { borderColor: theme.colors.border },
              resolution === 'merge' && { backgroundColor: theme.colors.primary },
            ]}
            onPress={() => handleResolutionSelect(conflict.id, 'merge')}
          >
            <Text
              style={[
                styles.resolutionButtonText,
                { color: theme.colors.text },
                resolution === 'merge' && { color: 'white' },
              ]}
            >
              {t('conflicts.merge')}
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.conflictData}>
          <Text style={[styles.dataLabel, { color: theme.colors.textSecondary }]}>
            {t('conflicts.localData')}
          </Text>
          <Text style={[styles.dataContent, { color: theme.colors.text }]}>
            {JSON.stringify(conflict.data, null, 2)}
          </Text>
        </View>

        <MorphingButton
          title={t('conflicts.resolve')}
          variant="primary"
          size="small"
          onPress={() => handleResolveSingle(conflict.id)}
          disabled={!resolution}
          testID={`resolve-conflict-${conflict.id}`}
        />
      </View>
    );
  }, [selectedResolution, handleResolutionSelect, handleResolveSingle, theme.colors, t]);

  const allResolved = conflicts.every(conflict => selectedResolution[conflict.id]);

  return (
    <Modal
      testID={testID}
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
        <View style={styles.header}>
          <Text style={[styles.title, { color: theme.colors.text }]}>
            {t('conflicts.title')}
          </Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            {t('conflicts.subtitle', { count: conflicts.length })}
          </Text>
        </View>

        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {conflicts.map(renderConflictItem)}
        </ScrollView>

        <View style={styles.footer}>
          <MorphingButton
            title={t('conflicts.resolveAll')}
            variant="success"
            size="large"
            onPress={handleResolveAll}
            disabled={!allResolved || conflicts.length === 0}
            testID="resolve-all-conflicts"
          />
          
          <MorphingButton
            title={t('conflicts.close')}
            variant="secondary"
            size="large"
            onPress={onClose}
            testID="close-conflict-resolver"
          />
        </View>
      </SafeAreaView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
  },
  conflictItem: {
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 16,
  },
  conflictTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  conflictType: {
    fontSize: 14,
    marginBottom: 16,
  },
  resolutionButtons: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  resolutionButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    alignItems: 'center',
  },
  resolutionButtonText: {
    fontSize: 14,
    fontWeight: '500',
  },
  conflictData: {
    marginBottom: 16,
  },
  dataLabel: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
  },
  dataContent: {
    fontSize: 12,
    fontFamily: 'monospace',
    backgroundColor: '#f5f5f5',
    padding: 8,
    borderRadius: 4,
  },
  footer: {
    padding: 20,
    gap: 12,
  },
});
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useOfflineSync } from '../../hooks/offline/use-offline-sync';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';
import { MorphingButton } from '../animations/morphing-button';

interface ConflictResolverProps {
  visible: boolean;
  onClose: () => void;
  testID?: string;
}

export function ConflictResolver({ visible, onClose, testID }: ConflictResolverProps) {
  const { theme } = useAppStore();
  const { t } = useI18n();
  const { conflicts, resolveConflict } = useOfflineSync();
  
  const [selectedResolution, setSelectedResolution] = useState<{
    [key: string]: 'server' | 'client' | 'merge';
  }>({});

  const handleResolutionSelect = useCallback((conflictId: string, resolution: 'server' | 'client' | 'merge') => {
    setSelectedResolution(prev => ({
      ...prev,
      [conflictId]: resolution,
    }));
  }, []);

  const handleResolveAll = useCallback(async () => {
    try {
      for (const conflict of conflicts) {
        const resolution = selectedResolution[conflict.id];
        if (resolution) {
          await resolveConflict(conflict.id, resolution);
        }
      }
      
      setSelectedResolution({});
      onClose();
      Alert.alert(t('conflicts.resolved'), t('conflicts.allResolved'));
    } catch (error) {
      Alert.alert(t('conflicts.error'), t('conflicts.resolveFailed'));
    }
  }, [conflicts, selectedResolution, resolveConflict, onClose, t]);

  const handleResolveSingle = useCallback(async (conflictId: string) => {
    const resolution = selectedResolution[conflictId];
    if (!resolution) {
      Alert.alert(t('conflicts.error'), t('conflicts.selectResolution'));
      return;
    }

    try {
      await resolveConflict(conflictId, resolution);
      setSelectedResolution(prev => {
        const newState = { ...prev };
        delete newState[conflictId];
        return newState;
      });
      
      if (conflicts.length === 1) {
        onClose();
      }
    } catch (error) {
      Alert.alert(t('conflicts.error'), t('conflicts.resolveFailed'));
    }
  }, [selectedResolution, resolveConflict, conflicts.length, onClose, t]);

  const renderConflictItem = useCallback((conflict: any) => {
    const resolution = selectedResolution[conflict.id];
    
    return (
      <View
        key={conflict.id}
        style={[
          styles.conflictItem,
          { backgroundColor: theme.colors.surface, borderColor: theme.colors.border },
        ]}
      >
        <Text style={[styles.conflictTitle, { color: theme.colors.text }]}>
          {t('conflicts.item', { id: conflict.id })}
        </Text>
        
        <Text style={[styles.conflictType, { color: theme.colors.textSecondary }]}>
          {t('conflicts.type', { type: conflict.type })}
        </Text>

        <View style={styles.resolutionButtons}>
          <TouchableOpacity
            style={[
              styles.resolutionButton,
              { borderColor: theme.colors.border },
              resolution === 'server' && { backgroundColor: theme.colors.primary },
            ]}
            onPress={() => handleResolutionSelect(conflict.id, 'server')}
          >
            <Text
              style={[
                styles.resolutionButtonText,
                { color: theme.colors.text },
                resolution === 'server' && { color: 'white' },
              ]}
            >
              {t('conflicts.server')}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.resolutionButton,
              { borderColor: theme.colors.border },
              resolution === 'client' && { backgroundColor: theme.colors.primary },
            ]}
            onPress={() => handleResolutionSelect(conflict.id, 'client')}
          >
            <Text
              style={[
                styles.resolutionButtonText,
                { color: theme.colors.text },
                resolution === 'client' && { color: 'white' },
              ]}
            >
              {t('conflicts.client')}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.resolutionButton,
              { borderColor: theme.colors.border },
              resolution === 'merge' && { backgroundColor: theme.colors.primary },
            ]}
            onPress={() => handleResolutionSelect(conflict.id, 'merge')}
          >
            <Text
              style={[
                styles.resolutionButtonText,
                { color: theme.colors.text },
                resolution === 'merge' && { color: 'white' },
              ]}
            >
              {t('conflicts.merge')}
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.conflictData}>
          <Text style={[styles.dataLabel, { color: theme.colors.textSecondary }]}>
            {t('conflicts.localData')}
          </Text>
          <Text style={[styles.dataContent, { color: theme.colors.text }]}>
            {JSON.stringify(conflict.data, null, 2)}
          </Text>
        </View>

        <MorphingButton
          title={t('conflicts.resolve')}
          variant="primary"
          size="small"
          onPress={() => handleResolveSingle(conflict.id)}
          disabled={!resolution}
          testID={`resolve-conflict-${conflict.id}`}
        />
      </View>
    );
  }, [selectedResolution, handleResolutionSelect, handleResolveSingle, theme.colors, t]);

  const allResolved = conflicts.every(conflict => selectedResolution[conflict.id]);

  return (
    <Modal
      testID={testID}
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
        <View style={styles.header}>
          <Text style={[styles.title, { color: theme.colors.text }]}>
            {t('conflicts.title')}
          </Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            {t('conflicts.subtitle', { count: conflicts.length })}
          </Text>
        </View>

        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {conflicts.map(renderConflictItem)}
        </ScrollView>

        <View style={styles.footer}>
          <MorphingButton
            title={t('conflicts.resolveAll')}
            variant="success"
            size="large"
            onPress={handleResolveAll}
            disabled={!allResolved || conflicts.length === 0}
            testID="resolve-all-conflicts"
          />
          
          <MorphingButton
            title={t('conflicts.close')}
            variant="secondary"
            size="large"
            onPress={onClose}
            testID="close-conflict-resolver"
          />
        </View>
      </SafeAreaView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
  },
  conflictItem: {
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 16,
  },
  conflictTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  conflictType: {
    fontSize: 14,
    marginBottom: 16,
  },
  resolutionButtons: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  resolutionButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    alignItems: 'center',
  },
  resolutionButtonText: {
    fontSize: 14,
    fontWeight: '500',
  },
  conflictData: {
    marginBottom: 16,
  },
  dataLabel: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
  },
  dataContent: {
    fontSize: 12,
    fontFamily: 'monospace',
    backgroundColor: '#f5f5f5',
    padding: 8,
    borderRadius: 4,
  },
  footer: {
    padding: 20,
    gap: 12,
  },
});


