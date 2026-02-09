import React from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useDashboardStats } from '@/hooks/use-dashboard';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton, SkeletonText } from '@/components/ui/skeleton';
import { ErrorMessage } from '@/components/ui/error-message';
import { useRouter } from 'expo-router';
import { useTheme } from '@/contexts/theme-context';
import { formatErrorMessage } from '@/utils/error-handler';

export default function DashboardScreen() {
  const { data: stats, isLoading, error, refetch, isRefetching } = useDashboardStats();
  const router = useRouter();
  const { theme } = useTheme();

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]} edges={['top']}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={isRefetching}
            onRefresh={refetch}
            tintColor={theme.colors.primary}
          />
        }
      >
        <Text style={[styles.title, { color: theme.colors.text }]}>Dashboard</Text>

        {isLoading ? (
          <View style={styles.statsContainer}>
            {Array.from({ length: 6 }).map((_, index) => (
              <Card key={index} variant="elevated">
                <SkeletonText lines={2} />
              </Card>
            ))}
          </View>
        ) : error ? (
          <ErrorMessage message={formatErrorMessage(error)} onRetry={() => refetch()} />
        ) : stats ? (
          <View style={styles.statsContainer}>
            <Card variant="elevated">
              <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>Total Shipments</Text>
              <Text style={[styles.statValue, { color: theme.colors.text }]}>{stats.total_shipments}</Text>
            </Card>

            <Card variant="elevated">
              <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>Active Shipments</Text>
              <Text style={[styles.statValue, { color: theme.colors.success }]}>{stats.active_shipments}</Text>
            </Card>

            <Card variant="elevated">
              <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>Pending Shipments</Text>
              <Text style={[styles.statValue, { color: theme.colors.warning }]}>{stats.pending_shipments}</Text>
            </Card>

            <Card variant="elevated">
              <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>Delivered Shipments</Text>
              <Text style={[styles.statValue, { color: theme.colors.success }]}>{stats.delivered_shipments}</Text>
            </Card>

            <Card variant="elevated">
              <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>Total Revenue</Text>
              <Text style={[styles.statValue, { color: theme.colors.primary }]}>
                ${stats.total_revenue.toLocaleString()}
              </Text>
            </Card>

            <Card variant="elevated">
              <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>Avg. Transit Time</Text>
              <Text style={[styles.statValue, { color: theme.colors.text }]}>
                {stats.average_transit_time} days
              </Text>
            </Card>
          </View>
        ) : null}

        <View style={styles.actions}>
          <Button
            title="Create Quote"
            onPress={() => router.push('/quote/create')}
            style={styles.actionButton}
          />
          <Button
            title="View Shipments"
            onPress={() => router.push('/shipments')}
            variant="outline"
            style={styles.actionButton}
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
  content: {
    padding: 16,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    marginBottom: 24,
  },
  statsContainer: {
    marginBottom: 24,
  },
  statLabel: {
    fontSize: 14,
    marginBottom: 8,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  statValue: {
    fontSize: 28,
    fontWeight: '700',
  },
  actions: {
    gap: 12,
  },
  actionButton: {
    width: '100%',
  },
});

