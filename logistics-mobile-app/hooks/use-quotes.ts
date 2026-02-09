import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { quotesService } from '@/services/quotes-service';
import { QuoteRequest, QuoteResponse } from '@/types';

export function useCreateQuote() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: QuoteRequest) => quotesService.createQuote(request),
    onSuccess: (data) => {
      queryClient.setQueryData(['quote', data.quote_id], data);
      queryClient.invalidateQueries({ queryKey: ['quotes'] });
    },
  });
}

export function useQuote(quoteId: string | null) {
  return useQuery({
    queryKey: ['quote', quoteId],
    queryFn: () => quotesService.getQuote(quoteId!),
    enabled: !!quoteId,
  });
}


