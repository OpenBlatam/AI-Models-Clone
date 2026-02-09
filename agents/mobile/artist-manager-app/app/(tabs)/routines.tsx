import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { routineService } from '@/services/routine-service';
import { LoadingSpinner } from '@/components/loading-spinner';
import { ErrorMessage } from '@/components/error-message';
import { Card } from '@/components/card';
import { Button } from '@/components/button';
import { Colors } from '@/constants/colors';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { RoutineTask } from '@/types';
import { useRouter } from 'expo-router';

export default function RoutinesScreen() {
  const { isDark } = useColorScheme();
  const colors = isDark ? Colors.dark : Colors.light;
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: routines, isLoading, error, refetch } = useQuery({
    queryKey: ['routines'],
    queryFn: () => routineService.getRoutines(),
  });

  const { data: pendingRoutines } = useQuery({
    queryKey: ['routines', 'pending'],
    queryFn: () => routineService.getPendingRoutines(),
  });

  const completeMutation = useMutation({
    mutationFn: (taskId: string) => routineService.completeRoutine(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['routines'] });
    },
  });

  const handleComplete = (taskId: string) => {
    completeMutation.mutate(taskId);
  };

  const renderRoutine = ({ item }: { item: RoutineTask }) => {
    const isPending = pendingRoutines?.some((r) => r.id === item.id);

    return (
      <Card>
        <View style={styles.routineHeader}>
          <View style={styles.routineInfo}>
            <Text style={[styles.routineTitle, { color: colors.text }]}>{item.title}</Text>
            <Text style={[styles.routineTime, { color: colors.icon }]}>
              {item.scheduled_time} ({item.duration_minutes} min)
            </Text>
            {item.description && (
              <Text style={[styles.routineDescription, { color: colors.text }]}>
                {item.description}
              </Text>
            )}
          </View>
          {isPending && (
            <TouchableOpacity
              onPress={() => handleComplete(item.id)}
              style={[styles.completeButton, { backgroundColor: colors.success }]}
              disabled={completeMutation.isPending}
            >
              <Text style={styles.completeButtonText}>Complete</Text>
            </TouchableOpacity>
          )}
        </View>
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
        <ErrorMessage message="Failed to load routines" onRetry={() => refetch()} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]} edges={['top']}>
      <View style={styles.header}>
        <Text style={[styles.title, { color: colors.text }]}>Routines</Text>
        <Button
          title="Add Routine"
          onPress={() => router.push('/routines/create')}
          variant="primary"
        />
      </View>

      {pendingRoutines && pendingRoutines.length > 0 && (
        <View style={styles.pendingSection}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>
            Pending ({pendingRoutines.length})
          </Text>
        </View>
      )}

      {routines && routines.length > 0 ? (
        <FlatList
          data={routines}
          renderItem={renderRoutine}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
        />
      ) : (
        <View style={styles.emptyContainer}>
          <Text style={[styles.emptyText, { color: colors.icon }]}>No routines defined</Text>
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
  pendingSection: {
    paddingHorizontal: 16,
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
  },
  listContent: {
    paddingBottom: 20,
  },
  routineHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  routineInfo: {
    flex: 1,
  },
  routineTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 4,
  },
  routineTime: {
    fontSize: 14,
    marginBottom: 4,
  },
  routineDescription: {
    fontSize: 14,
    marginTop: 4,
  },
  completeButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  completeButtonText: {
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


