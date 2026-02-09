import { useQuery } from '@tanstack/react-query';
import { reportsService } from '@/services/reports-service';
import { DashboardStats, ShipmentReport } from '@/types';

export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () => reportsService.getDashboardStats(),
    refetchInterval: 60000, // Refetch every minute
  });
}

export function useShipmentReport() {
  return useQuery({
    queryKey: ['dashboard', 'shipment-report'],
    queryFn: () => reportsService.getShipmentReport(),
  });
}


