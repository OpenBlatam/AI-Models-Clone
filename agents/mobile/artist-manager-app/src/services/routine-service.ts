import { RoutineTask, RoutineTaskFormData, RoutineStatus } from '@/types';
import { get, post, put, del } from '@/utils/api-client';
import { getArtistId } from '@/utils/storage';

const getArtistIdOrThrow = async (): Promise<string> => {
  const artistId = await getArtistId();
  if (!artistId) {
    throw new Error('Artist ID not found. Please login first.');
  }
  return artistId;
};

export const routineService = {
  async getRoutines(routineType?: string, todayOnly = false): Promise<RoutineTask[]> {
    const artistId = await getArtistIdOrThrow();
    const params = new URLSearchParams();
    if (routineType) params.append('routine_type', routineType);
    if (todayOnly) params.append('today_only', 'true');
    const query = params.toString();
    return get<RoutineTask[]>(`/routines/${artistId}/tasks${query ? `?${query}` : ''}`);
  },

  async getRoutine(taskId: string): Promise<RoutineTask> {
    const artistId = await getArtistIdOrThrow();
    return get<RoutineTask>(`/routines/${artistId}/tasks/${taskId}`);
  },

  async createRoutine(routineData: RoutineTaskFormData): Promise<RoutineTask> {
    const artistId = await getArtistIdOrThrow();
    return post<RoutineTask>(`/routines/${artistId}/tasks`, routineData);
  },

  async updateRoutine(taskId: string, routineData: Partial<RoutineTaskFormData>): Promise<RoutineTask> {
    const artistId = await getArtistIdOrThrow();
    return put<RoutineTask>(`/routines/${artistId}/tasks/${taskId}`, routineData);
  },

  async deleteRoutine(taskId: string): Promise<void> {
    const artistId = await getArtistIdOrThrow();
    await del(`/routines/${artistId}/tasks/${taskId}`);
  },

  async completeRoutine(
    taskId: string,
    status: RoutineStatus = 'completed',
    notes?: string,
    actualDurationMinutes?: number
  ): Promise<{ task_id: string; completed_at: string; status: string }> {
    const artistId = await getArtistIdOrThrow();
    return post(`/routines/${artistId}/tasks/${taskId}/complete`, {
      status,
      notes,
      actual_duration_minutes: actualDurationMinutes,
    });
  },

  async getPendingRoutines(): Promise<RoutineTask[]> {
    const artistId = await getArtistIdOrThrow();
    return get<RoutineTask[]>(`/routines/${artistId}/pending`);
  },

  async getCompletionRate(taskId: string, days = 30): Promise<{
    task_id: string;
    completion_rate: number;
    days: number;
  }> {
    const artistId = await getArtistIdOrThrow();
    return get(`/routines/${artistId}/tasks/${taskId}/completion-rate?days=${days}`);
  },
};


