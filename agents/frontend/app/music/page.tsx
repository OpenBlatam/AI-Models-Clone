'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { musicApiService, type Track } from '@/lib/api/music-api';
import { Music, Sparkles, BarChart3, GitCompare, Brain, Heart, ListMusic, History, Compass, TrendingUp, Award, Network, Music2, User, BarChart, FileText, Bookmark, PieChart, Wand2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { TrackSearch } from '@/components/music/TrackSearch';
import { TrackAnalysis } from '@/components/music/TrackAnalysis';
import { MusicDashboard } from '@/components/music/MusicDashboard';
import { TrackComparison } from '@/components/music/TrackComparison';
import { Recommendations } from '@/components/music/Recommendations';
import { MLAnalysis } from '@/components/music/MLAnalysis';
import { FavoritesManager } from '@/components/music/FavoritesManager';
import { PlaylistManager } from '@/components/music/PlaylistManager';
import { HistoryView } from '@/components/music/HistoryView';
import { DiscoveryPanel } from '@/components/music/DiscoveryPanel';
import { ExportAnalysis } from '@/components/music/ExportAnalysis';
import { AudioFeaturesChart } from '@/components/music/AudioFeaturesChart';
import { TemporalEnergyChart } from '@/components/music/TemporalEnergyChart';
import { TrendsView } from '@/components/music/TrendsView';
import { QualityAnalysis } from '@/components/music/QualityAnalysis';
import { CollaborationNetwork } from '@/components/music/CollaborationNetwork';
import { CoverRemixAnalyzer } from '@/components/music/CoverRemixAnalyzer';
import { ArtistAnalysis } from '@/components/music/ArtistAnalysis';
import { AdvancedSearch } from '@/components/music/AdvancedSearch';
import { PlaylistAnalyzer } from '@/components/music/PlaylistAnalyzer';
import { ShareAnalysis } from '@/components/music/ShareAnalysis';
import { ThemeToggle } from '@/components/music/ThemeToggle';
import { KeyboardShortcuts, ShortcutsHelp } from '@/components/music/KeyboardShortcuts';
import { TemporalStructureView } from '@/components/music/TemporalStructureView';
import { AnimatedCard, FadeIn } from '@/components/music/AnimatedCard';
import { QuickActions } from '@/components/music/QuickActions';
import { TrackPreview } from '@/components/music/TrackPreview';
import { NotificationCenter } from '@/components/music/NotificationCenter';
import { StatsCard } from '@/components/music/StatsCard';
import { SearchSuggestions } from '@/components/music/SearchSuggestions';
import { FilterPanel } from '@/components/music/FilterPanel';
import { SortOptions } from '@/components/music/SortOptions';
import { BulkActions } from '@/components/music/BulkActions';
import { ComparisonMatrix } from '@/components/music/ComparisonMatrix';
import { AnalysisTimeline } from '@/components/music/AnalysisTimeline';
import { SmartRecommendations } from '@/components/music/SmartRecommendations';
import { PerformanceOptimizer } from '@/components/music/PerformanceOptimizer';
import { VoiceCommands } from '@/components/music/VoiceCommands';
import { SavedAnalyses } from '@/components/music/SavedAnalyses';
import { ExportManager } from '@/components/music/ExportManager';
import { RealTimeUpdates } from '@/components/music/RealTimeUpdates';
import { SearchHistory } from '@/components/music/SearchHistory';
import { WaveformVisualizer } from '@/components/music/WaveformVisualizer';
import { LyricsViewer } from '@/components/music/LyricsViewer';
import { SimilarityGraph } from '@/components/music/SimilarityGraph';
import { AnalysisInsights } from '@/components/music/AnalysisInsights';
import { BatchAnalyzer } from '@/components/music/BatchAnalyzer';
import { TagManager } from '@/components/music/TagManager';
import { NotesManager } from '@/components/music/NotesManager';
import { StatisticsView } from '@/components/music/StatisticsView';
import { QuickStats } from '@/components/music/QuickStats';
import { BookmarkManager } from '@/components/music/BookmarkManager';
import { AdvancedFilters } from '@/components/music/AdvancedFilters';
import { ShareMenu } from '@/components/music/ShareMenu';
import { PlaylistGenerator } from '@/components/music/PlaylistGenerator';
import { TrackRating } from '@/components/music/TrackRating';
import { CommentSection } from '@/components/music/CommentSection';
import { DownloadManager } from '@/components/music/DownloadManager';
import { AudioPlayer } from '@/components/music/AudioPlayer';
import { FavoriteGenres } from '@/components/music/FavoriteGenres';
import { RecentActivity } from '@/components/music/RecentActivity';
import { SearchFilters } from '@/components/music/SearchFilters';
import { TrendingTracks } from '@/components/music/TrendingTracks';
import { TopArtists } from '@/components/music/TopArtists';
import { QuickSearch } from '@/components/music/QuickSearch';
import { MusicLibrary } from '@/components/music/MusicLibrary';
import { PlaylistQueue } from '@/components/music/PlaylistQueue';
import { MusicPlayer } from '@/components/music/MusicPlayer';
import { Equalizer } from '@/components/music/Equalizer';
import { MusicStats } from '@/components/music/MusicStats';
import { LyricsSync } from '@/components/music/LyricsSync';
import { MusicVisualizer } from '@/components/music/MusicVisualizer';
import { PlaybackSpeed } from '@/components/music/PlaybackSpeed';
import { Crossfade } from '@/components/music/Crossfade';
import { SmartPlaylists } from '@/components/music/SmartPlaylists';
import { MusicMoods } from '@/components/music/MusicMoods';
import { MusicDiscovery } from '@/components/music/MusicDiscovery';
import { MusicInsights } from '@/components/music/MusicInsights';
import { MusicComparison } from '@/components/music/MusicComparison';
import { MusicTimeline } from '@/components/music/MusicTimeline';
import { MusicShare } from '@/components/music/MusicShare';
import { MusicExport } from '@/components/music/MusicExport';
import { MusicFilters } from '@/components/music/MusicFilters';
import { MusicSort } from '@/components/music/MusicSort';
import { MusicView } from '@/components/music/MusicView';
import { MusicPagination } from '@/components/music/MusicPagination';
import { MusicSearchAdvanced } from '@/components/music/MusicSearchAdvanced';
import { MusicRecommendationsAdvanced } from '@/components/music/MusicRecommendationsAdvanced';
import { MusicAnalytics } from '@/components/music/MusicAnalytics';
import { MusicSettings } from '@/components/music/MusicSettings';
import { MusicCollaboration } from '@/components/music/MusicCollaboration';
import { MusicCoverRemix } from '@/components/music/MusicCoverRemix';
import { MusicTrendsAdvanced } from '@/components/music/MusicTrendsAdvanced';
import { MusicQualityAdvanced } from '@/components/music/MusicQualityAdvanced';
import { MusicArtistEvolution } from '@/components/music/MusicArtistEvolution';
import { MusicPlaylistAnalysis } from '@/components/music/MusicPlaylistAnalysis';
import { MusicBatchOperations } from '@/components/music/MusicBatchOperations';
import { MusicNotifications } from '@/components/music/MusicNotifications';
import { MusicCoaching } from '@/components/music/MusicCoaching';
import { MusicContextual } from '@/components/music/MusicContextual';
import { MusicTemporal } from '@/components/music/MusicTemporal';
import { MusicMLAdvanced } from '@/components/music/MusicMLAdvanced';
import { MusicKeyboardShortcuts } from '@/components/music/MusicKeyboardShortcuts';
import { MusicAccessibility } from '@/components/music/MusicAccessibility';
import { MusicPerformance } from '@/components/music/MusicPerformance';
import { MusicHelp } from '@/components/music/MusicHelp';
import { MusicOffline } from '@/components/music/MusicOffline';
import { MusicSync } from '@/components/music/MusicSync';
import { MusicBackup } from '@/components/music/MusicBackup';
import { MusicThemes } from '@/components/music/MusicThemes';
import { MusicSearchHistory } from '@/components/music/MusicSearchHistory';
import { MusicFavoritesQuick } from '@/components/music/MusicFavoritesQuick';
import { MusicRecentSearches } from '@/components/music/MusicRecentSearches';
import { MusicWorkspace } from '@/components/music/MusicWorkspace';
import { MusicCompareAdvanced } from '@/components/music/MusicCompareAdvanced';
import { MusicExportAdvanced } from '@/components/music/MusicExportAdvanced';
import { MusicShareAdvanced } from '@/components/music/MusicShareAdvanced';
import { MusicQuickStats } from '@/components/music/MusicQuickStats';
import { MusicTutorial } from '@/components/music/MusicTutorial';
import { MusicTour } from '@/components/music/MusicTour';
import { MusicFeedback } from '@/components/music/MusicFeedback';
import { MusicWelcome } from '@/components/music/MusicWelcome';
import { MusicTips } from '@/components/music/MusicTips';
import { MusicAchievements } from '@/components/music/MusicAchievements';
import { MusicStreak } from '@/components/music/MusicStreak';
import { MusicLeaderboard } from '@/components/music/MusicLeaderboard';
import { MusicChallenges } from '@/components/music/MusicChallenges';
import { MusicProgress } from '@/components/music/MusicProgress';
import { MusicSocial } from '@/components/music/MusicSocial';
import { MusicActivity } from '@/components/music/MusicActivity';
import { MusicTrendingNow } from '@/components/music/MusicTrendingNow';
import { MusicDiscoverWeekly } from '@/components/music/MusicDiscoverWeekly';
import { MusicRadio } from '@/components/music/MusicRadio';

type TabType = 'search' | 'analysis' | 'compare' | 'recommendations' | 'ml' | 'favorites' | 'playlists' | 'history' | 'discovery' | 'trends' | 'quality' | 'collaborations' | 'covers' | 'artists' | 'playlist-analysis' | 'batch' | 'statistics' | 'bookmarks' | 'playlist-generator';

export default function MusicPage() {
  const [activeTab, setActiveTab] = useState<TabType>('search');
  const [selectedTrack, setSelectedTrack] = useState<Track | null>(null);
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [searchResults, setSearchResults] = useState<Track[]>([]);
  const [selectedTracks, setSelectedTracks] = useState<string[]>([]);
  const [filters, setFilters] = useState<any>({});
  const [query, setQuery] = useState('');
  const [playlistQueue, setPlaylistQueue] = useState<Track[]>([]);
  const [currentTrackIndex, setCurrentTrackIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [viewMode, setViewMode] = useState<'grid' | 'list' | 'compact'>('list');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(20);
  const [sortConfig, setSortConfig] = useState<{ field: string; order: 'asc' | 'desc' } | undefined>();

  const { data: analytics } = useQuery({
    queryKey: ['music-analytics'],
    queryFn: () => musicApiService.getAnalytics(),
    refetchInterval: 30000,
  });

  const handleTrackSelect = async (track: Track) => {
    setSelectedTrack(track);
    if (!playlistQueue.find((t) => t.id === track.id)) {
      setPlaylistQueue([...playlistQueue, track]);
    }
    try {
      const analysis = await musicApiService.analyzeTrack(track.id, undefined, true);
      setAnalysisData(analysis);
      toast.success('Análisis completado');
      setActiveTab('analysis');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Error al analizar la canción');
    }
  };

  const handleSearchResults = (results: Track[]) => {
    setSearchResults(results);
  };

  const tabs = [
    { id: 'search' as TabType, label: 'Buscar', icon: Music },
    { id: 'analysis' as TabType, label: 'Análisis', icon: BarChart3 },
    { id: 'compare' as TabType, label: 'Comparar', icon: GitCompare },
    { id: 'recommendations' as TabType, label: 'Recomendaciones', icon: Sparkles },
    { id: 'ml' as TabType, label: 'ML', icon: Brain },
    { id: 'favorites' as TabType, label: 'Favoritos', icon: Heart },
    { id: 'playlists' as TabType, label: 'Playlists', icon: ListMusic },
    { id: 'history' as TabType, label: 'Historial', icon: History },
    { id: 'discovery' as TabType, label: 'Descubrir', icon: Compass },
    { id: 'trends' as TabType, label: 'Tendencias', icon: TrendingUp },
    { id: 'quality' as TabType, label: 'Calidad', icon: Award },
    { id: 'collaborations' as TabType, label: 'Colaboraciones', icon: Network },
    { id: 'covers' as TabType, label: 'Covers/Remixes', icon: Music2 },
    { id: 'artists' as TabType, label: 'Artistas', icon: User },
    { id: 'playlist-analysis' as TabType, label: 'Análisis Playlist', icon: BarChart },
    { id: 'batch' as TabType, label: 'Análisis Lote', icon: FileText },
    { id: 'statistics' as TabType, label: 'Estadísticas', icon: PieChart },
    { id: 'bookmarks' as TabType, label: 'Marcadores', icon: Bookmark },
    { id: 'playlist-generator' as TabType, label: 'Generar Playlist', icon: Wand2 },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-pink-900 to-purple-900">
      <MusicOffline />
      <MusicWelcome />
      <MusicTutorial />
      <MusicFeedback />
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Music className="w-10 h-10 text-purple-300" />
              <div>
                <h1 className="text-4xl font-bold text-white">Music Analyzer AI</h1>
                <p className="text-gray-300">
                  Analiza canciones, obtén insights musicales y coaching personalizado
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
                      <MusicKeyboardShortcuts />
                      <MusicAccessibility />
                      <MusicSettings />
                      <MusicSync />
                      <RealTimeUpdates />
                      <VoiceCommands
                        onCommand={(command) => {
                          // Procesar comando de voz
                          if (command.toLowerCase().includes('buscar')) {
                            setActiveTab('search');
                          } else if (command.toLowerCase().includes('analizar')) {
                            if (selectedTrack) handleTrackSelect(selectedTrack);
                          }
                        }}
                      />
                      <MusicNotifications />
                      <MusicTour />
                      <MusicTips />
                      <NotificationCenter />
                      <ThemeToggle />
            </div>
          </div>
        </div>

        {/* Keyboard Shortcuts */}
        <KeyboardShortcuts
          onSearch={() => setActiveTab('search')}
          onAnalyze={() => selectedTrack && handleTrackSelect(selectedTrack)}
          onCompare={() => setActiveTab('compare')}
        />

        {/* Analytics Dashboard */}
        {analytics && (
          <FadeIn>
            <div className="grid md:grid-cols-4 gap-4 mb-6">
              <div className="md:col-span-3">
                <MusicDashboard analytics={analytics} />
              </div>
              <PerformanceOptimizer />
            </div>
            <QuickStats />
            <MusicStats />
            <div className="grid md:grid-cols-2 gap-4 mt-4">
              <FavoriteGenres />
              <RecentActivity />
            </div>
            <div className="grid md:grid-cols-2 gap-4 mt-4">
              <TrendingTracks onTrackSelect={handleTrackSelect} />
              <TopArtists />
            </div>
            <div className="grid md:grid-cols-2 gap-4 mt-4">
              <MusicMoods onMoodSelect={(mood) => {
                toast.info(`Mood seleccionado: ${mood}`);
              }} />
              <MusicInsights />
            </div>
            <div className="mt-4">
              <MusicFavoritesQuick onTrackSelect={handleTrackSelect} />
            </div>
            <div className="mt-4">
              <MusicQuickStats />
            </div>
            <div className="grid md:grid-cols-2 gap-4 mt-4">
              <MusicStreak />
              <MusicProgress />
            </div>
            <div className="grid md:grid-cols-2 gap-4 mt-4">
              <MusicAchievements />
              <MusicChallenges />
            </div>
            <div className="mt-4">
              <MusicLeaderboard />
            </div>
            <div className="grid md:grid-cols-2 gap-4 mt-4">
              <MusicTrendingNow onTrackSelect={handleTrackSelect} />
              <MusicDiscoverWeekly onTrackSelect={handleTrackSelect} />
            </div>
            <div className="grid md:grid-cols-2 gap-4 mt-4">
              <MusicSocial />
              <MusicActivity />
            </div>
            <div className="mt-4">
              <MusicRadio />
            </div>
          </FadeIn>
        )}

        {/* Tabs */}
        <div className="mb-6">
          <div className="flex gap-2 overflow-x-auto pb-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-colors whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'bg-purple-600 text-white'
                      : 'bg-white/10 text-gray-300 hover:bg-white/20'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === 'search' && (
            <div className="space-y-6">
              <MusicSearchAdvanced
                onTrackSelect={handleTrackSelect}
                onResults={handleSearchResults}
              />
              <div className="grid lg:grid-cols-2 gap-8">
                      <div className="space-y-4">
                        <QuickSearch onTrackSelect={handleTrackSelect} />
                        <MusicFilters onFilterChange={setFilters} />
                        <div className="flex gap-2 mb-4">
                          <MusicSort
                            onSortChange={(field, order) => {
                              setSortConfig({ field, order });
                            }}
                            currentSort={sortConfig}
                          />
                          <MusicView viewMode={viewMode} onViewModeChange={setViewMode} />
                        </div>
                        <SearchFilters onFilterChange={setFilters} />
                        <AdvancedFilters onFilterChange={setFilters} />
                        <div className="flex gap-2 mb-4">
                          <FilterPanel onFilterChange={setFilters} />
                          <SortOptions
                            onSortChange={(field, order) => {
                              setSortConfig({ field, order });
                            }}
                          />
                        </div>
                <TrackSearch
                  onTrackSelect={handleTrackSelect}
                  onSearchResults={handleSearchResults}
                />
                <AdvancedSearch onTrackSelect={handleTrackSelect} />
                <SearchSuggestions
                  onSelect={(query) => {
                    // Trigger search with query
                    setQuery(query);
                  }}
                />
                <SearchHistory
                  onSelect={(query) => {
                    // Trigger search with query from history
                    setQuery(query);
                  }}
                />
                <MusicSearchHistory
                  onSelect={(query) => {
                    setQuery(query);
                  }}
                />
                <MusicRecentSearches
                  onSelect={(query) => {
                    setQuery(query);
                  }}
                />
                {searchResults.length > 0 && (
                  <MusicPagination
                    currentPage={currentPage}
                    totalPages={Math.ceil(searchResults.length / itemsPerPage)}
                    onPageChange={setCurrentPage}
                    itemsPerPage={itemsPerPage}
                    onItemsPerPageChange={setItemsPerPage}
                  />
                )}
              </div>
              </div>
              {selectedTrack && (
                <AnimatedCard>
                  <div className="space-y-4">
                    <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                      <h3 className="text-xl font-semibold text-white mb-4">Canción Seleccionada</h3>
                      <div className="flex items-start gap-4">
                        {selectedTrack.images && selectedTrack.images[0] && (
                          <img
                            src={selectedTrack.images[0].url}
                            alt={selectedTrack.name}
                            className="w-24 h-24 rounded-lg"
                          />
                        )}
                        <div>
                          <h4 className="text-lg font-semibold text-white">{selectedTrack.name}</h4>
                          <p className="text-purple-200">{selectedTrack.artists.join(', ')}</p>
                          <p className="text-sm text-gray-400">{selectedTrack.album}</p>
                          <p className="text-sm text-gray-400 mt-2">
                            Popularidad: {selectedTrack.popularity}
                          </p>
                        </div>
                      </div>
                            </div>
                            <div className="flex items-center gap-2 mb-4">
                              <ShareMenu
                                url={`${window.location.origin}/music/analysis/${selectedTrack.id}`}
                                title={selectedTrack.name}
                                description={`${selectedTrack.artists.join(', ')} - ${selectedTrack.album}`}
                              />
                            </div>
                            <div className="grid lg:grid-cols-2 gap-6">
                              <MusicPlayer
                                track={selectedTrack}
                                queue={playlistQueue.length > 0 ? playlistQueue : [selectedTrack]}
                                currentIndex={currentTrackIndex}
                                onNext={() => {
                                  if (playlistQueue.length > 0) {
                                    setCurrentTrackIndex((prev) => (prev + 1) % playlistQueue.length);
                                  }
                                }}
                                onPrevious={() => {
                                  if (playlistQueue.length > 0) {
                                    setCurrentTrackIndex((prev) => (prev - 1 + playlistQueue.length) % playlistQueue.length);
                                  }
                                }}
                                onShuffle={() => {
                                  const shuffled = [...playlistQueue].sort(() => Math.random() - 0.5);
                                  setPlaylistQueue(shuffled);
                                }}
                                onRepeat={() => {}}
                              />
                              <Equalizer />
                            </div>
                            <div className="grid lg:grid-cols-3 gap-6">
                              <PlaybackSpeed onSpeedChange={setPlaybackSpeed} />
                              <Crossfade />
                              <div className="lg:col-span-1">
                                {/* Placeholder para más controles */}
                              </div>
                            </div>
                            {selectedTrack && (
                              <MusicVisualizer
                                audioElement={null}
                                isPlaying={isPlaying}
                              />
                            )}
                            <PlaylistQueue
                              tracks={playlistQueue.length > 0 ? playlistQueue : (selectedTrack ? [selectedTrack] : [])}
                              currentTrackId={playlistQueue.length > 0 ? playlistQueue[currentTrackIndex]?.id : selectedTrack?.id}
                              onTrackSelect={(track) => {
                                const index = playlistQueue.findIndex((t) => t.id === track.id);
                                if (index !== -1) {
                                  setCurrentTrackIndex(index);
                                } else {
                                  setPlaylistQueue([...playlistQueue, track]);
                                  setCurrentTrackIndex(playlistQueue.length);
                                }
                              }}
                              onRemove={(trackId) => {
                                setPlaylistQueue(playlistQueue.filter((t) => t.id !== trackId));
                              }}
                              onReorder={(from, to) => {
                                const newQueue = [...playlistQueue];
                                const [removed] = newQueue.splice(from, 1);
                                newQueue.splice(to, 0, removed);
                                setPlaylistQueue(newQueue);
                                setCurrentTrackIndex(to);
                              }}
                            />
                            <TrackPreview track={selectedTrack} />
                            <QuickActions
                      track={selectedTrack}
                      onAnalyze={() => handleTrackSelect(selectedTrack)}
                      onFavorite={() => {
                        musicApiService.addToFavorites('user123', selectedTrack.id, selectedTrack.name, selectedTrack.artists);
                        toast.success('Agregado a favoritos');
                      }}
                      onCompare={() => setActiveTab('compare')}
                      onRecommendations={() => setActiveTab('recommendations')}
                      onExport={() => {
                        musicApiService.exportAnalysis(selectedTrack.id, 'json', true);
                        toast.success('Exportando análisis...');
                      }}
                              onShare={() => {
                                // ShareMenu se maneja en el componente
                              }}
                    />
                  </div>
                </AnimatedCard>
              )}
            </div>
          )}

          {activeTab === 'analysis' && (
            <div className="space-y-6">
              {analysisData && selectedTrack ? (
                <>
                  <TrackAnalysis analysis={analysisData} track={selectedTrack} />
                  <AnalysisInsights analysis={analysisData} />
                  <div className="grid lg:grid-cols-2 gap-6">
                    <WaveformVisualizer track={selectedTrack} audioUrl={selectedTrack.preview_url} />
                    <LyricsViewer
                      trackId={selectedTrack.id}
                      trackName={selectedTrack.name}
                      artists={selectedTrack.artists}
                    />
                  </div>
                  {analysisData?.lyrics && (
                    <LyricsSync
                      lyrics={analysisData.lyrics}
                      currentTime={currentTime}
                      duration={0}
                    />
                  )}
                  <div className="grid lg:grid-cols-2 gap-6">
                    <TagManager resourceId={selectedTrack.id} resourceType="track" />
                    <NotesManager resourceId={selectedTrack.id} resourceType="track" />
                  </div>
                  <div className="space-y-6">
                    <TrackRating trackId={selectedTrack.id} />
                    <CommentSection resourceId={selectedTrack.id} resourceType="track" />
                    <MusicCoaching trackId={selectedTrack.id} trackName={selectedTrack.name} />
                    <MusicContextual
                      trackId={selectedTrack.id}
                      onTrackSelect={handleTrackSelect}
                    />
                    <MusicTemporal trackId={selectedTrack.id} />
                  </div>
                </>
              ) : (
                <div className="bg-white/10 backdrop-blur-lg rounded-xl p-12 border border-white/20 text-center">
                  <Sparkles className="w-16 h-16 text-purple-300 mx-auto mb-4" />
                  <p className="text-gray-300 text-lg">
                    Busca y selecciona una canción para ver su análisis completo
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'compare' && (
            <div className="space-y-6">
              <MusicComparison
                tracks={searchResults}
                onTracksChange={setSearchResults}
                onCompare={() => {
                  toast.info('Comparación iniciada');
                }}
              />
              {searchResults.length > 0 && (
                <>
                  <BulkActions
                    tracks={searchResults}
                    selectedTracks={selectedTracks}
                    onSelectionChange={setSelectedTracks}
                    onBulkAction={(action, trackIds) => {
                      toast.info(`Acción ${action} en ${trackIds.length} canciones`);
                    }}
                  />
                  <TrackComparison tracks={searchResults} />
                  {analysisData && Array.isArray(analysisData) && analysisData.length > 0 && (
                    <>
                      <ComparisonMatrix
                        tracks={searchResults.filter((t) => selectedTracks.includes(t.id) || selectedTracks.length === 0)}
                        analysisData={analysisData}
                      />
                      <MusicCompareAdvanced
                        tracks={searchResults.filter((t) => selectedTracks.includes(t.id) || selectedTracks.length === 0)}
                        analysisData={analysisData}
                      />
                      <SimilarityGraph
                        tracks={searchResults}
                        similarities={analysisData.map((a: any, idx: number) => ({
                          track1: searchResults[idx]?.id || '',
                          track2: searchResults[(idx + 1) % searchResults.length]?.id || '',
                          score: 0.8, // Simulado
                        }))}
                      />
                    </>
                  )}
                </>
              ) : (
                <div className="bg-white/10 backdrop-blur-lg rounded-xl p-12 border border-white/20 text-center">
                  <GitCompare className="w-16 h-16 text-purple-300 mx-auto mb-4" />
                  <p className="text-gray-300 text-lg">
                    Busca canciones primero para poder compararlas
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'recommendations' && (
            <div>
              {selectedTrack ? (
                <div className="space-y-6">
                  <Recommendations trackId={selectedTrack.id} track={selectedTrack} />
                  <SmartRecommendations
                    trackId={selectedTrack.id}
                    currentAnalysis={analysisData}
                  />
                  <MusicRecommendationsAdvanced
                    trackId={selectedTrack.id}
                    onTrackSelect={handleTrackSelect}
                  />
                </div>
              ) : (
                <div className="bg-white/10 backdrop-blur-lg rounded-xl p-12 border border-white/20 text-center">
                  <Sparkles className="w-16 h-16 text-purple-300 mx-auto mb-4" />
                  <p className="text-gray-300 text-lg">
                    Selecciona una canción para obtener recomendaciones
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'ml' && (
            <div>
              {selectedTrack ? (
                <div className="space-y-6">
                  <MLAnalysis trackId={selectedTrack.id} />
                  <MusicMLAdvanced trackId={selectedTrack.id} />
                </div>
              ) : (
                <div className="bg-white/10 backdrop-blur-lg rounded-xl p-12 border border-white/20 text-center">
                  <Brain className="w-16 h-16 text-purple-300 mx-auto mb-4" />
                  <p className="text-gray-300 text-lg">
                    Selecciona una canción para análisis con Machine Learning
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'favorites' && (
            <div className="space-y-6">
              <FavoritesManager />
              <MusicLibrary onTrackSelect={handleTrackSelect} />
              <MusicWorkspace />
            </div>
          )}

          {activeTab === 'playlists' && <PlaylistManager />}

          {activeTab === 'history' && (
            <div className="space-y-6">
              <HistoryView />
              <SavedAnalyses />
              <ExportManager analyses={[]} />
            </div>
          )}

          {activeTab === 'discovery' && (
            <div className="space-y-6">
              <DiscoveryPanel />
              <MusicDiscovery onTrackSelect={handleTrackSelect} />
            </div>
          )}

          {activeTab === 'trends' && (
            <div className="space-y-6">
              <TrendsView />
              <MusicTrendsAdvanced onTrackSelect={handleTrackSelect} />
            </div>
          )}

          {activeTab === 'quality' && (
            <div>
              {selectedTrack ? (
                <div className="space-y-6">
                  <QualityAnalysis trackId={selectedTrack.id} />
                  <MusicQualityAdvanced trackId={selectedTrack.id} />
                </div>
              ) : (
                <div className="bg-white/10 backdrop-blur-lg rounded-xl p-12 border border-white/20 text-center">
                  <Award className="w-16 h-16 text-purple-300 mx-auto mb-4" />
                  <p className="text-gray-300 text-lg">
                    Selecciona una canción para analizar su calidad
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'collaborations' && (
            <div className="space-y-6">
              <CollaborationNetwork />
              <MusicCollaboration onTrackSelect={handleTrackSelect} />
            </div>
          )}

          {activeTab === 'covers' && (
            <div className="space-y-6">
              <CoverRemixAnalyzer />
              {selectedTrack && (
                <MusicCoverRemix
                  trackId={selectedTrack.id}
                  onTrackSelect={handleTrackSelect}
                />
              )}
            </div>
          )}

          {activeTab === 'artists' && (
            <div className="space-y-6">
              <ArtistAnalysis />
              <MusicArtistEvolution />
            </div>
          )}

          {activeTab === 'playlist-analysis' && (
            <div className="space-y-6">
              <PlaylistAnalyzer />
              <MusicPlaylistAnalysis />
            </div>
          )}

          {activeTab === 'batch' && (
            <div className="space-y-6">
              <BatchAnalyzer />
              {searchResults.length > 0 && (
                <MusicBatchOperations tracks={searchResults} />
              )}
            </div>
          )}

          {activeTab === 'statistics' && (
            <div className="space-y-6">
              <StatisticsView />
              <MusicAnalytics />
            </div>
          )}

          {activeTab === 'bookmarks' && <BookmarkManager />}

          {activeTab === 'playlist-generator' && (
            <div className="space-y-6">
              <PlaylistGenerator />
              <SmartPlaylists />
            </div>
          )}
        </div>

        {/* Additional Features for Analysis Tab */}
        {activeTab === 'analysis' && analysisData && selectedTrack && (
          <div className="mt-6 space-y-6">
            <div className="grid lg:grid-cols-2 gap-6">
              <AudioFeaturesChart technicalAnalysis={analysisData.technical_analysis} />
              <TemporalEnergyChart trackId={selectedTrack.id} />
            </div>
            <TemporalStructureView trackId={selectedTrack.id} />
                    {analysisData.composition_analysis?.structure && (
                      <>
                        <AnalysisTimeline sections={analysisData.composition_analysis.structure} />
                        <MusicTimeline
                          sections={analysisData.composition_analysis.structure}
                          duration={selectedTrack.duration_ms / 1000}
                        />
                      </>
                    )}
                    <div className="grid lg:grid-cols-2 gap-6">
                      <ExportAnalysis trackId={selectedTrack.id} trackName={selectedTrack.name} />
                      <ShareAnalysis
                        trackId={selectedTrack.id}
                        trackName={selectedTrack.name}
                        analysisId={analysisData.analysis_id}
                      />
                      <MusicExport data={analysisData} filename={`${selectedTrack.name}-analysis`} />
                      <MusicExportAdvanced data={analysisData} filename={`${selectedTrack.name}-analysis`} />
                      <MusicShare
                        trackId={selectedTrack.id}
                        trackName={selectedTrack.name}
                        artists={selectedTrack.artists}
                        analysisId={analysisData.analysis_id}
                      />
                      <MusicShareAdvanced
                        url={`${typeof window !== 'undefined' ? window.location.origin : ''}/music/analysis/${selectedTrack.id}`}
                        title={selectedTrack.name}
                        description={`${selectedTrack.artists.join(', ')} - ${selectedTrack.album}`}
                      />
                    </div>
          </div>
        )}

        {/* Shortcuts Help */}
        <div className="mt-8 grid md:grid-cols-2 gap-6">
          <ShortcutsHelp />
          <MusicHelp />
          <MusicPerformance />
          <MusicBackup />
          <MusicThemes />
        </div>
      </div>

      {/* Download Manager */}
      <DownloadManager />
    </div>
  );
}

