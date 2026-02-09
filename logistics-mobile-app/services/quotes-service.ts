import { apiClient } from '@/utils/api-client';
import { QuoteRequest, QuoteResponse } from '@/types';

export const quotesService = {
  createQuote: async (request: QuoteRequest): Promise<QuoteResponse> => {
    return apiClient.post<QuoteResponse>('/forwarding/quotes', request);
  },

  getQuote: async (quoteId: string): Promise<QuoteResponse> => {
    return apiClient.get<QuoteResponse>(`/forwarding/quotes/${quoteId}`);
  },
};


