import { apiClient } from '@/utils/api-client';
import { ShipmentRequest, ShipmentResponse, ShipmentFilters, ShipmentStatus } from '@/types';

export const shipmentsService = {
  createShipment: async (request: ShipmentRequest): Promise<ShipmentResponse> => {
    return apiClient.post<ShipmentResponse>('/forwarding/shipments', request);
  },

  getShipments: async (filters?: ShipmentFilters): Promise<ShipmentResponse[]> => {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.transportation_mode) params.append('transportation_mode', filters.transportation_mode);
    if (filters?.origin_country) params.append('origin_country', filters.origin_country);
    if (filters?.destination_country) params.append('destination_country', filters.destination_country);
    if (filters?.page) params.append('page', filters.page.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());

    const queryString = params.toString();
    const url = `/forwarding/shipments${queryString ? `?${queryString}` : ''}`;
    return apiClient.get<ShipmentResponse[]>(url);
  },

  getShipment: async (shipmentId: string): Promise<ShipmentResponse> => {
    return apiClient.get<ShipmentResponse>(`/forwarding/shipments/${shipmentId}`);
  },

  updateShipmentStatus: async (shipmentId: string, status: ShipmentStatus): Promise<ShipmentResponse> => {
    return apiClient.patch<ShipmentResponse>(`/forwarding/shipments/${shipmentId}/status`, { status });
  },
};


