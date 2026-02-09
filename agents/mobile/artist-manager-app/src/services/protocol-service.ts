import { Protocol } from '@/types';
import { get, post, put, del } from '@/utils/api-client';
import { getArtistId } from '@/utils/storage';

const getArtistIdOrThrow = async (): Promise<string> => {
  const artistId = await getArtistId();
  if (!artistId) {
    throw new Error('Artist ID not found. Please login first.');
  }
  return artistId;
};

export const protocolService = {
  async getProtocols(category?: string, priority?: string, eventId?: string): Promise<Protocol[]> {
    const artistId = await getArtistIdOrThrow();
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (priority) params.append('priority', priority);
    if (eventId) params.append('event_id', eventId);
    const query = params.toString();
    return get<Protocol[]>(`/protocols/${artistId}${query ? `?${query}` : ''}`);
  },

  async getProtocol(protocolId: string): Promise<Protocol> {
    const artistId = await getArtistIdOrThrow();
    return get<Protocol>(`/protocols/${artistId}/${protocolId}`);
  },

  async createProtocol(protocolData: Omit<Protocol, 'id'>): Promise<Protocol> {
    const artistId = await getArtistIdOrThrow();
    return post<Protocol>(`/protocols/${artistId}`, protocolData);
  },

  async updateProtocol(protocolId: string, protocolData: Partial<Protocol>): Promise<Protocol> {
    const artistId = await getArtistIdOrThrow();
    return put<Protocol>(`/protocols/${artistId}/${protocolId}`, protocolData);
  },

  async deleteProtocol(protocolId: string): Promise<void> {
    const artistId = await getArtistIdOrThrow();
    await del(`/protocols/${artistId}/${protocolId}`);
  },

  async checkEventCompliance(eventId: string): Promise<{
    compliant: boolean;
    checked_protocols: Array<{ id: string; title: string; compliant: boolean; violations?: string[] }>;
    recommendations: string[];
    summary: string;
  }> {
    const artistId = await getArtistIdOrThrow();
    return post(`/protocols/${artistId}/events/${eventId}/check-compliance`);
  },

  async getComplianceRate(protocolId: string): Promise<{
    protocol_id: string;
    compliance_rate: number;
  }> {
    const artistId = await getArtistIdOrThrow();
    return get(`/protocols/${artistId}/${protocolId}/compliance-rate`);
  },
};


