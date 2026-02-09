'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { musicApiService, type Track } from '@/lib/api/music-api';
import { Search, Loader2, Music } from 'lucide-react';
import { debounce } from '@/lib/utils';
import toast from 'react-hot-toast';

interface TrackSearchProps {
  onTrackSelect: (track: Track) => void;
  onSearchResults?: (results: Track[]) => void;
}

export function TrackSearch({ onTrackSelect, onSearchResults }: TrackSearchProps) {
  const [query, setQuery] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const debouncedSearch = debounce((value: string) => {
    setSearchQuery(value);
  }, 500);

  const { data, isLoading, error } = useQuery({
    queryKey: ['music-search', searchQuery],
    queryFn: () => musicApiService.searchTracks(searchQuery, 10),
    enabled: searchQuery.length > 0,
    onSuccess: (data) => {
      if (onSearchResults && data.results) {
        onSearchResults(data.results);
      }
    },
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    debouncedSearch(value);
  };

  const handleTrackClick = (track: Track) => {
    onTrackSelect(track);
    setQuery('');
    setSearchQuery('');
  };

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
      <h2 className="text-2xl font-semibold text-white mb-4 flex items-center gap-2">
        <Search className="w-6 h-6" />
        Buscar Canciones
      </h2>
      
      <div className="relative mb-4">
        <input
          type="text"
          value={query}
          onChange={handleInputChange}
          placeholder="Busca canciones, artistas o álbumes..."
          className="w-full px-4 py-3 pl-12 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-400"
        />
        <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-300" />
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 text-purple-300 animate-spin" />
        </div>
      )}

      {error && (
        <div className="text-red-300 text-sm py-4">
          Error al buscar canciones. Intenta de nuevo.
        </div>
      )}

      {data && data.results.length > 0 && (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {data.results.map((track) => (
            <button
              key={track.id}
              onClick={() => handleTrackClick(track)}
              className="w-full flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-left"
            >
              {track.images && track.images[0] ? (
                <img
                  src={track.images[0].url}
                  alt={track.name}
                  className="w-12 h-12 rounded"
                />
              ) : (
                <div className="w-12 h-12 rounded bg-purple-500 flex items-center justify-center">
                  <Music className="w-6 h-6 text-white" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium truncate">{track.name}</p>
                <p className="text-sm text-gray-300 truncate">
                  {track.artists.join(', ')}
                </p>
              </div>
            </button>
          ))}
        </div>
      )}

      {data && data.results.length === 0 && searchQuery && (
        <div className="text-center py-8 text-gray-300">
          No se encontraron resultados
        </div>
      )}
    </div>
  );
}

