import { apiClient } from '@/utils/api-client';
import { BookingRequest, BookingResponse } from '@/types';

export const bookingsService = {
  createBooking: async (request: BookingRequest): Promise<BookingResponse> => {
    return apiClient.post<BookingResponse>('/forwarding/bookings', request);
  },

  getBooking: async (bookingId: string): Promise<BookingResponse> => {
    return apiClient.get<BookingResponse>(`/forwarding/bookings/${bookingId}`);
  },
};


