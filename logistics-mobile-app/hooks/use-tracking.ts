import { useQuery } from '@tanstack/react-query';
import { trackingService, TrackingInfo, TrackingSummary } from '@/services/tracking-service';

export function useShipmentTracking(shipmentId: string | null) {
  return useQuery({
    queryKey: ['tracking', 'shipment', shipmentId],
    queryFn: () => trackingService.getShipmentTracking(shipmentId!),
    enabled: !!shipmentId,
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function useContainerTracking(containerId: string | null) {
  return useQuery({
    queryKey: ['tracking', 'container', containerId],
    queryFn: () => trackingService.getContainerTracking(containerId!),
    enabled: !!containerId,
    refetchInterval: 30000,
  });
}

export function useTrackingHistory(shipmentId: string | null) {
  return useQuery({
    queryKey: ['tracking', 'history', shipmentId],
    queryFn: () => trackingService.getTrackingHistory(shipmentId!),
    enabled: !!shipmentId,
  });
}

export function useTrackingSummary() {
  return useQuery({
    queryKey: ['tracking', 'summary'],
    queryFn: () => trackingService.getTrackingSummary(),
    refetchInterval: 60000, // Refetch every minute
  });
}


