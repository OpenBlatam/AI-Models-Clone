import React from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useQuery } from '@tanstack/react-query';
import { alertsService } from '@/services/alerts-service';
import { AlertResponse } from '@/types';
import { Card } from '@/components/ui/card';
import { format } from 'date-fns';

export default function AlertsScreen() {
  const { data: alerts, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => alertsService.getAlerts({ is_read: false }),
  });

  function getSeverityColor(severity: string) {
    const colors: Record<string, string> = {
      low: '#34C759',
      medium: '#FF9500',
      high: '#FF3B30',
    };
    return colors[severity] || '#8E8E93';
  }

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <Text>Loading alerts...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Text style={styles.title}>Alerts</Text>
      <FlatList
        data={alerts}
        keyExtractor={(item) => item.alert_id}
        renderItem={({ item }) => (
          <Card>
            <View style={styles.alertHeader}>
              <Text style={styles.alertType}>{item.alert_type}</Text>
              <View
                style={[styles.severityBadge, { backgroundColor: getSeverityColor(item.severity) }]}
              >
                <Text style={styles.severityText}>{item.severity.toUpperCase()}</Text>
              </View>
            </View>
            <Text style={styles.alertMessage}>{item.message}</Text>
            <Text style={styles.alertDate}>
              {format(new Date(item.created_at), 'MMM dd, yyyy HH:mm')}
            </Text>
          </Card>
        )}
        contentContainerStyle={styles.listContent}
        refreshControl={<RefreshControl refreshing={isRefetching} onRefresh={refetch} />}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No alerts</Text>
          </View>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    padding: 16,
    color: '#000',
  },
  listContent: {
    padding: 16,
  },
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  alertType: {
    fontSize: 16,
    fontWeight: '700',
    color: '#000',
  },
  severityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  severityText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '600',
  },
  alertMessage: {
    fontSize: 14,
    color: '#000',
    marginBottom: 8,
  },
  alertDate: {
    fontSize: 12,
    color: '#8E8E93',
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 16,
    color: '#8E8E93',
  },
});


