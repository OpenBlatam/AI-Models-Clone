import { apiClient } from '@/utils/api-client';
import { AlertRequest, AlertResponse } from '@/types';

export interface AlertFilters {
  is_read?: boolean;
  severity?: string;
  shipment_id?: string;
  container_id?: string;
}

export const alertsService = {
  createAlert: async (request: AlertRequest): Promise<AlertResponse> => {
    return apiClient.post<AlertResponse>('/alerts', request);
  },

  getAlerts: async (filters?: AlertFilters): Promise<AlertResponse[]> => {
    const params = new URLSearchParams();
    if (filters?.is_read !== undefined) params.append('is_read', filters.is_read.toString());
    if (filters?.severity) params.append('severity', filters.severity);
    if (filters?.shipment_id) params.append('shipment_id', filters.shipment_id);
    if (filters?.container_id) params.append('container_id', filters.container_id);

    const queryString = params.toString();
    const url = `/alerts${queryString ? `?${queryString}` : ''}`;
    return apiClient.get<AlertResponse[]>(url);
  },

  getAlert: async (alertId: string): Promise<AlertResponse> => {
    return apiClient.get<AlertResponse>(`/alerts/${alertId}`);
  },

  markAsRead: async (alertId: string): Promise<AlertResponse> => {
    return apiClient.patch<AlertResponse>(`/alerts/${alertId}/read`);
  },

  deleteAlert: async (alertId: string): Promise<void> => {
    return apiClient.delete<void>(`/alerts/${alertId}`);
  },
};


