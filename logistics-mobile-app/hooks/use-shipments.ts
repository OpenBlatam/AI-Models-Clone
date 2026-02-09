import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { shipmentsService } from '@/services/shipments-service';
import { ShipmentRequest, ShipmentResponse, ShipmentFilters, ShipmentStatus } from '@/types';

export function useShipments(filters?: ShipmentFilters) {
  return useQuery({
    queryKey: ['shipments', filters],
    queryFn: () => shipmentsService.getShipments(filters),
  });
}

export function useShipment(shipmentId: string | null) {
  return useQuery({
    queryKey: ['shipment', shipmentId],
    queryFn: () => shipmentsService.getShipment(shipmentId!),
    enabled: !!shipmentId,
  });
}

export function useCreateShipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: ShipmentRequest) => shipmentsService.createShipment(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shipments'] });
    },
  });
}

export function useUpdateShipmentStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ shipmentId, status }: { shipmentId: string; status: ShipmentStatus }) =>
      shipmentsService.updateShipmentStatus(shipmentId, status),
    onSuccess: (data) => {
      queryClient.setQueryData(['shipment', data.shipment_id], data);
      queryClient.invalidateQueries({ queryKey: ['shipments'] });
    },
  });
}


