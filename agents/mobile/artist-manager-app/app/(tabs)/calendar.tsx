import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { calendarService } from '@/services/calendar-service';
import { LoadingSpinner } from '@/components/loading-spinner';
import { ErrorMessage } from '@/components/error-message';
import { Card } from '@/components/card';
import { Button } from '@/components/button';
import { Colors } from '@/constants/colors';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { format } from 'date-fns';
import { CalendarEvent } from '@/types';
import { useRouter } from 'expo-router';

export default function CalendarScreen() {
  const { isDark } = useColorScheme();
  const colors = isDark ? Colors.dark : Colors.light;
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: events, isLoading, error, refetch } = useQuery({
    queryKey: ['calendar', 'events'],
    queryFn: () => calendarService.getEvents(undefined, 30),
  });

  const deleteMutation = useMutation({
    mutationFn: (eventId: string) => calendarService.deleteEvent(eventId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendar'] });
    },
  });

  const handleDeleteEvent = (eventId: string) => {
    deleteMutation.mutate(eventId);
  };

  const renderEvent = ({ item }: { item: CalendarEvent }) => {
    const startDate = new Date(item.start_time);
    const endDate = new Date(item.end_time);

    return (
      <Card>
        <View style={styles.eventHeader}>
          <View style={styles.eventInfo}>
            <Text style={[styles.eventTitle, { color: colors.text }]}>{item.title}</Text>
            <Text style={[styles.eventTime, { color: colors.icon }]}>
              {format(startDate, 'MMM d, h:mm a')} - {format(endDate, 'h:mm a')}
            </Text>
            {item.location && (
              <Text style={[styles.eventLocation, { color: colors.icon }]}>{item.location}</Text>
            )}
          </View>
          <TouchableOpacity
            onPress={() => handleDeleteEvent(item.id)}
            style={[styles.deleteButton, { backgroundColor: colors.error }]}
          >
            <Text style={styles.deleteButtonText}>Delete</Text>
          </TouchableOpacity>
        </View>
        {item.description && (
          <Text style={[styles.eventDescription, { color: colors.text }]}>{item.description}</Text>
        )}
      </Card>
    );
  };

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
        <ErrorMessage message="Failed to load events" onRetry={() => refetch()} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]} edges={['top']}>
      <View style={styles.header}>
        <Text style={[styles.title, { color: colors.text }]}>Calendar</Text>
        <Button
          title="Add Event"
          onPress={() => router.push('/calendar/create')}
          variant="primary"
        />
      </View>

      {events && events.length > 0 ? (
        <FlatList
          data={events}
          renderItem={renderEvent}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={[styles.emptyText, { color: colors.icon }]}>No events scheduled</Text>
            </View>
          }
        />
      ) : (
        <View style={styles.emptyContainer}>
          <Text style={[styles.emptyText, { color: colors.icon }]}>No events scheduled</Text>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  listContent: {
    paddingBottom: 20,
  },
  eventHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  eventInfo: {
    flex: 1,
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
  eventDescription: {
    fontSize: 14,
    marginTop: 8,
  },
  deleteButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  deleteButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 16,
  },
});


