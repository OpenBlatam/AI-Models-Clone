import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { routineService } from '@/services/routine-service';
import { RoutineTaskFormData, RoutineStatus } from '@/types';

export function useRoutines(routineType?: string, todayOnly = false) {
  return useQuery({
    queryKey: ['routines', routineType, todayOnly],
    queryFn: () => routineService.getRoutines(routineType, todayOnly),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

export function useRoutine(taskId: string) {
  return useQuery({
    queryKey: ['routines', taskId],
    queryFn: () => routineService.getRoutine(taskId),
    enabled: !!taskId,
  });
}

export function usePendingRoutines() {
  return useQuery({
    queryKey: ['routines', 'pending'],
    queryFn: () => routineService.getPendingRoutines(),
    refetchInterval: 1000 * 60 * 5, // Refetch every 5 minutes
  });
}

export function useCreateRoutine() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (routineData: RoutineTaskFormData) => routineService.createRoutine(routineData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['routines'] });
    },
  });
}

export function useUpdateRoutine() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ taskId, routineData }: { taskId: string; routineData: Partial<RoutineTaskFormData> }) =>
      routineService.updateRoutine(taskId, routineData),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['routines'] });
      queryClient.invalidateQueries({ queryKey: ['routines', variables.taskId] });
    },
  });
}

export function useDeleteRoutine() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) => routineService.deleteRoutine(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['routines'] });
    },
  });
}

export function useCompleteRoutine() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      taskId,
      status,
      notes,
      actualDurationMinutes,
    }: {
      taskId: string;
      status?: RoutineStatus;
      notes?: string;
      actualDurationMinutes?: number;
    }) => routineService.completeRoutine(taskId, status, notes, actualDurationMinutes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['routines'] });
    },
  });
}


