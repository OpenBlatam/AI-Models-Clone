'use client';

import { useState } from 'react';
import { Search, X, Filter } from 'lucide-react';
import toast from 'react-hot-toast';
import { type Track } from '@/lib/api/music-api';
import { musicApiService } from '@/lib/api/music-api';

interface MusicSearchAdvancedProps {
  onTrackSelect: (track: Track) => void;
  onResults: (tracks: Track[]) => void;
}

export function MusicSearchAdvanced({ onTrackSelect, onResults }: MusicSearchAdvancedProps) {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<Track[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    artist: '',
    album: '',
    year: '',
    genre: '',
  });

  const handleSearch = async () => {
    if (!query.trim()) {
      toast.error('Ingresa un término de búsqueda');
      return;
    }

    setIsSearching(true);
    try {
      const searchResults = await musicApiService.searchTracks(query, 50);
      setResults(searchResults.tracks || []);
      onResults(searchResults.tracks || []);
      toast.success(`Encontradas ${searchResults.tracks?.length || 0} canciones`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Error en la búsqueda');
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const clearSearch = () => {
    setQuery('');
    setResults([]);
    onResults([]);
  };

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
      <div className="flex items-center gap-2 mb-4">
        <Search className="w-5 h-5 text-purple-300" />
        <h3 className="text-lg font-semibold text-white">Búsqueda Avanzada</h3>
      </div>

      <div className="space-y-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Buscar canciones, artistas, álbumes..."
            className="flex-1 px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-400"
          />
          <button
            onClick={handleSearch}
            disabled={isSearching}
            className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            {isSearching ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Buscando...
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                Buscar
              </>
            )}
          </button>
          {query && (
            <button
              onClick={clearSearch}
              className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
        >
          <Filter className="w-4 h-4" />
          {showFilters ? 'Ocultar' : 'Mostrar'} Filtros
        </button>

        {showFilters && (
          <div className="grid md:grid-cols-2 gap-4 p-4 bg-white/5 rounded-lg">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Artista</label>
              <input
                type="text"
                value={filters.artist}
                onChange={(e) => setFilters({ ...filters, artist: e.target.value })}
                placeholder="Nombre del artista"
                className="w-full px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-400"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Álbum</label>
              <input
                type="text"
                value={filters.album}
                onChange={(e) => setFilters({ ...filters, album: e.target.value })}
                placeholder="Nombre del álbum"
                className="w-full px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-400"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Año</label>
              <input
                type="number"
                value={filters.year}
                onChange={(e) => setFilters({ ...filters, year: e.target.value })}
                placeholder="Año"
                className="w-full px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-400"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Género</label>
              <input
                type="text"
                value={filters.genre}
                onChange={(e) => setFilters({ ...filters, genre: e.target.value })}
                placeholder="Género"
                className="w-full px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-400"
              />
            </div>
          </div>
        )}

        {results.length > 0 && (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            <p className="text-sm text-gray-400 mb-2">
              {results.length} resultado{results.length !== 1 ? 's' : ''} encontrado{results.length !== 1 ? 's' : ''}
            </p>
            {results.map((track) => (
              <button
                key={track.id}
                onClick={() => onTrackSelect(track)}
                className="w-full flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-left"
              >
                {track.images && track.images[0] && (
                  <img
                    src={track.images[0].url}
                    alt={track.name}
                    className="w-12 h-12 rounded"
                  />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-white font-medium truncate">{track.name}</p>
                  <p className="text-sm text-gray-300 truncate">
                    {Array.isArray(track.artists) ? track.artists.join(', ') : track.artists}
                  </p>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}


