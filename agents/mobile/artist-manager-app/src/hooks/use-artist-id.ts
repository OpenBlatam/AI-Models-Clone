import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getArtistId, setArtistId } from '@/utils/storage';

export function useArtistId() {
  const queryClient = useQueryClient();

  const { data: artistId, isLoading } = useQuery({
    queryKey: ['artistId'],
    queryFn: getArtistId,
    staleTime: Infinity,
    gcTime: Infinity,
  });

  const mutation = useMutation({
    mutationFn: setArtistId,
    onSuccess: (_, newArtistId) => {
      queryClient.setQueryData(['artistId'], newArtistId);
    },
  });

  return {
    artistId,
    isLoading,
    setArtistId: mutation.mutate,
    isSetting: mutation.isPending,
  };
}


