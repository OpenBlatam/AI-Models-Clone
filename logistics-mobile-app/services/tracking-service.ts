import { apiClient } from '@/utils/api-client';
import { TrackingEvent } from '@/types';

export interface TrackingInfo {
  shipment_id?: string;
  container_id?: string;
  current_status: string;
  current_location?: {
    country: string;
    city: string;
    port_code?: string;
  };
  estimated_arrival?: string;
  tracking_events: TrackingEvent[];
}

export interface TrackingSummary {
  departing: number;
  arriving: number;
  in_transit: number;
}

export const trackingService = {
  getShipmentTracking: async (shipmentId: string): Promise<TrackingInfo> => {
    return apiClient.get<TrackingInfo>(`/tracking/shipment/${shipmentId}`);
  },

  getContainerTracking: async (containerId: string): Promise<TrackingInfo> => {
    return apiClient.get<TrackingInfo>(`/tracking/container/${containerId}`);
  },

  getTrackingHistory: async (shipmentId: string): Promise<TrackingEvent[]> => {
    return apiClient.get<TrackingEvent[]>(`/tracking/shipment/${shipmentId}/history`);
  },

  addTrackingUpdate: async (shipmentId: string, event: Partial<TrackingEvent>): Promise<TrackingEvent> => {
    return apiClient.post<TrackingEvent>(`/tracking/shipment/${shipmentId}/update`, event);
  },

  getTrackingSummary: async (): Promise<TrackingSummary> => {
    return apiClient.get<TrackingSummary>('/tracking/summary');
  },
};


