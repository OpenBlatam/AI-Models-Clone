import { useQuery } from '@tanstack/react-query';
import { View, Text, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { dashboardService } from '@/services/dashboard-service';
import { LoadingSpinner } from '@/components/loading-spinner';
import { ErrorMessage } from '@/components/error-message';
import { Card } from '@/components/card';
import { Colors } from '@/constants/colors';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { format } from 'date-fns';
import { useMemo } from 'react';

export default function DashboardScreen() {
  const { isDark } = useColorScheme();
  const colors = isDark ? Colors.dark : Colors.light;

  const { data, isLoading, error, refetch, isRefetching } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => dashboardService.getDashboard(),
    refetchInterval: 1000 * 60 * 5, // Refetch every 5 minutes
  });

  const upcomingEvents = useMemo(() => {
    if (!data?.upcoming_events?.events) return [];
    return data.upcoming_events.events.slice(0, 5);
  }, [data]);

  if (isLoading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]} edges={['top']}>
        <LoadingSpinner fullScreen />
      </SafeAreaView>
    );
  }

  if (error) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]} edges={['top']}>
        <ErrorMessage message="Failed to load dashboard" onRetry={() => refetch()} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]} edges={['top']}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={isRefetching} onRefresh={refetch} tintColor={colors.primary} />
        }
      >
        <View style={styles.header}>
          <Text style={[styles.title, { color: colors.text }]}>Dashboard</Text>
          <Text style={[styles.subtitle, { color: colors.icon }]}>
            {format(new Date(), 'EEEE, MMMM d, yyyy')}
          </Text>
        </View>

        <View style={styles.statsContainer}>
          <Card>
            <Text style={[styles.statLabel, { color: colors.icon }]}>Upcoming Events</Text>
            <Text style={[styles.statValue, { color: colors.text }]}>
              {data?.upcoming_events?.count ?? 0}
            </Text>
          </Card>

          <Card>
            <Text style={[styles.statLabel, { color: colors.icon }]}>Pending Routines</Text>
            <Text style={[styles.statValue, { color: colors.text }]}>
              {data?.routines?.pending_count ?? 0}
            </Text>
          </Card>

          <Card>
            <Text style={[styles.statLabel, { color: colors.icon }]}>Critical Protocols</Text>
            <Text style={[styles.statValue, { color: colors.text }]}>
              {data?.protocols?.critical_count ?? 0}
            </Text>
          </Card>

          <Card>
            <Text style={[styles.statLabel, { color: colors.icon }]}>Wardrobe Items</Text>
            <Text style={[styles.statValue, { color: colors.text }]}>
              {data?.wardrobe?.total_items ?? 0}
            </Text>
          </Card>
        </View>

        {upcomingEvents.length > 0 && (
          <View style={styles.section}>
            <Text style={[styles.sectionTitle, { color: colors.text }]}>Upcoming Events</Text>
            {upcomingEvents.map((event) => (
              <Card key={event.id}>
                <Text style={[styles.eventTitle, { color: colors.text }]}>{event.title}</Text>
                <Text style={[styles.eventTime, { color: colors.icon }]}>
                  {format(new Date(event.start_time), 'MMM d, h:mm a')}
                </Text>
                {event.location && (
                  <Text style={[styles.eventLocation, { color: colors.icon }]}>{event.location}</Text>
                )}
              </Card>
            ))}
          </View>
        )}
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
  header: {
    padding: 20,
    paddingBottom: 10,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
  },
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
    marginBottom: 20,
  },
  statLabel: {
    fontSize: 14,
    marginBottom: 8,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 12,
    paddingHorizontal: 16,
  },
  eventTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 4,
  },
  eventTime: {
    fontSize: 14,
    marginBottom: 2,
  },
  eventLocation: {
    fontSize: 14,
  },
});


