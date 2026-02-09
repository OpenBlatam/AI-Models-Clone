import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { calendarService } from '@/services/calendar-service';
import { CalendarEventFormData } from '@/types';

export function useCalendarEvents(date?: string, days?: number) {
  return useQuery({
    queryKey: ['calendar', 'events', date, days],
    queryFn: () => calendarService.getEvents(date, days),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

export function useCalendarEvent(eventId: string) {
  return useQuery({
    queryKey: ['calendar', 'events', eventId],
    queryFn: () => calendarService.getEvent(eventId),
    enabled: !!eventId,
  });
}

export function useCreateCalendarEvent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (eventData: CalendarEventFormData) => calendarService.createEvent(eventData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendar'] });
    },
  });
}

export function useUpdateCalendarEvent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ eventId, eventData }: { eventId: string; eventData: Partial<CalendarEventFormData> }) =>
      calendarService.updateEvent(eventId, eventData),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['calendar'] });
      queryClient.invalidateQueries({ queryKey: ['calendar', 'events', variables.eventId] });
    },
  });
}

export function useDeleteCalendarEvent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (eventId: string) => calendarService.deleteEvent(eventId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendar'] });
    },
  });
}

export function useWardrobeRecommendation(eventId: string) {
  return useQuery({
    queryKey: ['calendar', 'events', eventId, 'wardrobe-recommendation'],
    queryFn: () => calendarService.getWardrobeRecommendation(eventId),
    enabled: !!eventId,
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}


