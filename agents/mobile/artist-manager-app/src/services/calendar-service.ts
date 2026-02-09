import { CalendarEvent, CalendarEventFormData } from '@/types';
import { get, post, put, del } from '@/utils/api-client';
import { getArtistId } from '@/utils/storage';

const getArtistIdOrThrow = async (): Promise<string> => {
  const artistId = await getArtistId();
  if (!artistId) {
    throw new Error('Artist ID not found. Please login first.');
  }
  return artistId;
};

export const calendarService = {
  async getEvents(date?: string, days?: number): Promise<CalendarEvent[]> {
    const artistId = await getArtistIdOrThrow();
    const params = new URLSearchParams();
    if (date) params.append('date', date);
    if (days) params.append('days', days.toString());
    const query = params.toString();
    return get<CalendarEvent[]>(`/calendar/${artistId}/events${query ? `?${query}` : ''}`);
  },

  async getEvent(eventId: string): Promise<CalendarEvent> {
    const artistId = await getArtistIdOrThrow();
    return get<CalendarEvent>(`/calendar/${artistId}/events/${eventId}`);
  },

  async createEvent(eventData: CalendarEventFormData): Promise<CalendarEvent> {
    const artistId = await getArtistIdOrThrow();
    return post<CalendarEvent>(`/calendar/${artistId}/events`, {
      ...eventData,
      start_time: eventData.start_time.toISOString(),
      end_time: eventData.end_time.toISOString(),
    });
  },

  async updateEvent(eventId: string, eventData: Partial<CalendarEventFormData>): Promise<CalendarEvent> {
    const artistId = await getArtistIdOrThrow();
    const payload: Record<string, unknown> = { ...eventData };
    if (eventData.start_time) payload.start_time = eventData.start_time.toISOString();
    if (eventData.end_time) payload.end_time = eventData.end_time.toISOString();
    return put<CalendarEvent>(`/calendar/${artistId}/events/${eventId}`, payload);
  },

  async deleteEvent(eventId: string): Promise<void> {
    const artistId = await getArtistIdOrThrow();
    await del(`/calendar/${artistId}/events/${eventId}`);
  },

  async getWardrobeRecommendation(eventId: string): Promise<{
    dress_code: string;
    reasoning: string;
    recommended_items: string[];
    alternative_outfits: string[];
  }> {
    const artistId = await getArtistIdOrThrow();
    return get(`/calendar/${artistId}/events/${eventId}/wardrobe-recommendation`);
  },
};


