import { apiClient } from './api-client';
import { API_ENDPOINTS } from '../constants/config';
import type {
  TrackSearchRequest,
  TrackSearchResponse,
  TrackAnalysis,
  TrackComparison,
  RecommendationsResponse,
  HealthCheck,
  Track,
} from '../types/api';

export interface AnalyzeTrackRequest {
  track_id?: string;
  track_name?: string;
  include_coaching?: boolean;
}

export interface CompareTracksRequest {
  track_ids: string[];
}

class MusicApiService {
  async searchTracks(
    request: TrackSearchRequest
  ): Promise<TrackSearchResponse> {
    return apiClient.post<TrackSearchResponse>(
      API_ENDPOINTS.SEARCH,
      request
    );
  }

  async analyzeTrack(
    request: AnalyzeTrackRequest
  ): Promise<TrackAnalysis> {
    return apiClient.post<TrackAnalysis>(API_ENDPOINTS.ANALYZE, request);
  }

  async analyzeTrackById(
    trackId: string,
    includeCoaching = true
  ): Promise<TrackAnalysis> {
    return apiClient.get<TrackAnalysis>(
      `${API_ENDPOINTS.ANALYZE_BY_ID(trackId)}?include_coaching=${includeCoaching}`
    );
  }

  async getTrackInfo(trackId: string): Promise<Track> {
    return apiClient.get<Track>(API_ENDPOINTS.TRACK_INFO(trackId));
  }

  async getAudioFeatures(trackId: string): Promise<unknown> {
    return apiClient.get(API_ENDPOINTS.AUDIO_FEATURES(trackId));
  }

  async getRecommendations(
    trackId: string
  ): Promise<RecommendationsResponse> {
    return apiClient.get<RecommendationsResponse>(
      API_ENDPOINTS.RECOMMENDATIONS(trackId)
    );
  }

  async compareTracks(
    request: CompareTracksRequest
  ): Promise<TrackComparison> {
    return apiClient.post<TrackComparison>(API_ENDPOINTS.COMPARE, request);
  }

  async healthCheck(): Promise<HealthCheck> {
    return apiClient.get<HealthCheck>(API_ENDPOINTS.HEALTH);
  }

  async getCoaching(request: AnalyzeTrackRequest): Promise<TrackAnalysis> {
    return apiClient.post<TrackAnalysis>(API_ENDPOINTS.COACHING, request);
  }

  async getAudioAnalysis(trackId: string): Promise<unknown> {
    return apiClient.get(API_ENDPOINTS.AUDIO_ANALYSIS(trackId));
  }

  async getHistory(limit = 50): Promise<HistoryResponse> {
    return apiClient.get<HistoryResponse>(
      `${API_ENDPOINTS.HISTORY}?limit=${limit}`
    );
  }

  async getHistoryStats(): Promise<HistoryStats> {
    return apiClient.get<HistoryStats>(API_ENDPOINTS.HISTORY_STATS);
  }

  async exportAnalysis(
    trackId: string,
    format: 'json' | 'text' | 'markdown' = 'json',
    includeCoaching = true
  ): Promise<ExportResponse> {
    const separator = format ? '&' : '?';
    return apiClient.post<ExportResponse>(
      `${API_ENDPOINTS.EXPORT(trackId, format)}${separator}include_coaching=${includeCoaching}`
    );
  }

  async getContextualRecommendations(
    request: ContextualRecommendationRequest
  ): Promise<RecommendationsResponse> {
    return apiClient.post<RecommendationsResponse>(
      API_ENDPOINTS.CONTEXTUAL_RECOMMENDATIONS,
      request
    );
  }

  async getTimeOfDayRecommendations(
    timeOfDay: string,
    limit = 20
  ): Promise<RecommendationsResponse> {
    return apiClient.get<RecommendationsResponse>(
      `${API_ENDPOINTS.TIME_OF_DAY_RECOMMENDATIONS}?time_of_day=${timeOfDay}&limit=${limit}`
    );
  }

  async getActivityRecommendations(
    activity: string,
    limit = 20
  ): Promise<RecommendationsResponse> {
    return apiClient.get<RecommendationsResponse>(
      `${API_ENDPOINTS.ACTIVITY_RECOMMENDATIONS}?activity=${activity}&limit=${limit}`
    );
  }

  async getMoodRecommendations(
    mood: string,
    limit = 20
  ): Promise<RecommendationsResponse> {
    return apiClient.get<RecommendationsResponse>(
      `${API_ENDPOINTS.MOOD_RECOMMENDATIONS}?mood=${mood}&limit=${limit}`
    );
  }

  async discoverSimilarArtists(
    artistId: string,
    limit = 20
  ): Promise<TrackSearchResponse> {
    return apiClient.get<TrackSearchResponse>(
      `${API_ENDPOINTS.DISCOVERY_SIMILAR_ARTISTS}?artist_id=${artistId}&limit=${limit}`
    );
  }

  async discoverUnderground(limit = 20): Promise<TrackSearchResponse> {
    return apiClient.get<TrackSearchResponse>(
      `${API_ENDPOINTS.DISCOVERY_UNDERGROUND}?limit=${limit}`
    );
  }

  async discoverMoodTransition(
    fromMood: string,
    toMood: string,
    limit = 20
  ): Promise<TrackSearchResponse> {
    return apiClient.get<TrackSearchResponse>(
      `${API_ENDPOINTS.DISCOVERY_MOOD_TRANSITION}?from_mood=${fromMood}&to_mood=${toMood}&limit=${limit}`
    );
  }

  async discoverFresh(limit = 20): Promise<TrackSearchResponse> {
    return apiClient.get<TrackSearchResponse>(
      `${API_ENDPOINTS.DISCOVERY_FRESH}?limit=${limit}`
    );
  }

  async compareArtists(
    request: ArtistComparisonRequest
  ): Promise<unknown> {
    return apiClient.post(API_ENDPOINTS.ARTIST_COMPARE, request);
  }

  async getArtistEvolution(
    artistId: string
  ): Promise<unknown> {
    return apiClient.get(
      `${API_ENDPOINTS.ARTIST_EVOLUTION}?artist_id=${artistId}`
    );
  }

  async getTrendsPopularity(
    timeRange: 'short_term' | 'medium_term' | 'long_term' = 'medium_term',
    limit = 20
  ): Promise<unknown> {
    return apiClient.get(
      `${API_ENDPOINTS.TRENDS_POPULARITY}?time_range=${timeRange}&limit=${limit}`
    );
  }

  async getTrendsArtists(
    timeRange: 'short_term' | 'medium_term' | 'long_term' = 'medium_term',
    limit = 20
  ): Promise<unknown> {
    return apiClient.get(
      `${API_ENDPOINTS.TRENDS_ARTISTS}?time_range=${timeRange}&limit=${limit}`
    );
  }
}

export interface ContextualRecommendationRequest {
  context: string;
  limit?: number;
}

export interface ArtistComparisonRequest {
  artist_ids: string[];
}

export const musicApiService = new MusicApiService();

