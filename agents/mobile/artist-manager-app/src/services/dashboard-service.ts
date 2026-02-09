import { DashboardData, DailySummary } from '@/types';
import { get } from '@/utils/api-client';
import { getArtistId } from '@/utils/storage';

const getArtistIdOrThrow = async (): Promise<string> => {
  const artistId = await getArtistId();
  if (!artistId) {
    throw new Error('Artist ID not found. Please login first.');
  }
  return artistId;
};

export const dashboardService = {
  async getDashboard(): Promise<DashboardData> {
    const artistId = await getArtistIdOrThrow();
    return get<DashboardData>(`/dashboard/${artistId}`);
  },

  async getDailySummary(): Promise<DailySummary> {
    const artistId = await getArtistIdOrThrow();
    return get<DailySummary>(`/dashboard/${artistId}/daily-summary`);
  },
};


