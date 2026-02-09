import { apiClient } from '@/utils/api-client';
import { DashboardStats, ShipmentReport } from '@/types';

export const reportsService = {
  getDashboardStats: async (): Promise<DashboardStats> => {
    return apiClient.get<DashboardStats>('/reports/dashboard');
  },

  getShipmentReport: async (): Promise<ShipmentReport[]> => {
    return apiClient.get<ShipmentReport[]>('/reports/shipments');
  },
};


