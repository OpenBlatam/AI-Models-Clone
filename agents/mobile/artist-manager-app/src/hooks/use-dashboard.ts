import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '@/services/dashboard-service';

export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: () => dashboardService.getDashboard(),
    staleTime: 1000 * 60 * 2, // 2 minutes
    refetchInterval: 1000 * 60 * 5, // Refetch every 5 minutes
  });
}

export function useDailySummary() {
  return useQuery({
    queryKey: ['dashboard', 'daily-summary'],
    queryFn: () => dashboardService.getDailySummary(),
    staleTime: 1000 * 60 * 30, // 30 minutes (summary doesn't change often)
  });
}


