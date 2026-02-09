import { WardrobeItem, Outfit } from '@/types';
import { get, post, put, del } from '@/utils/api-client';
import { getArtistId } from '@/utils/storage';

const getArtistIdOrThrow = async (): Promise<string> => {
  const artistId = await getArtistId();
  if (!artistId) {
    throw new Error('Artist ID not found. Please login first.');
  }
  return artistId;
};

export const wardrobeService = {
  async getItems(category?: string, dressCode?: string): Promise<WardrobeItem[]> {
    const artistId = await getArtistIdOrThrow();
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (dressCode) params.append('dress_code', dressCode);
    const query = params.toString();
    return get<WardrobeItem[]>(`/wardrobe/${artistId}/items${query ? `?${query}` : ''}`);
  },

  async getItem(itemId: string): Promise<WardrobeItem> {
    const artistId = await getArtistIdOrThrow();
    return get<WardrobeItem>(`/wardrobe/${artistId}/items/${itemId}`);
  },

  async createItem(itemData: Omit<WardrobeItem, 'id'>): Promise<WardrobeItem> {
    const artistId = await getArtistIdOrThrow();
    return post<WardrobeItem>(`/wardrobe/${artistId}/items`, itemData);
  },

  async updateItem(itemId: string, itemData: Partial<WardrobeItem>): Promise<WardrobeItem> {
    const artistId = await getArtistIdOrThrow();
    return put<WardrobeItem>(`/wardrobe/${artistId}/items/${itemId}`, itemData);
  },

  async deleteItem(itemId: string): Promise<void> {
    const artistId = await getArtistIdOrThrow();
    await del(`/wardrobe/${artistId}/items/${itemId}`);
  },

  async getOutfits(dressCode?: string): Promise<Outfit[]> {
    const artistId = await getArtistIdOrThrow();
    const params = new URLSearchParams();
    if (dressCode) params.append('dress_code', dressCode);
    const query = params.toString();
    return get<Outfit[]>(`/wardrobe/${artistId}/outfits${query ? `?${query}` : ''}`);
  },

  async createOutfit(outfitData: Omit<Outfit, 'id'>): Promise<Outfit> {
    const artistId = await getArtistIdOrThrow();
    return post<Outfit>(`/wardrobe/${artistId}/outfits`, outfitData);
  },

  async markItemWorn(itemId: string): Promise<WardrobeItem> {
    const artistId = await getArtistIdOrThrow();
    return post<WardrobeItem>(`/wardrobe/${artistId}/items/${itemId}/mark-worn`);
  },

  async markOutfitWorn(outfitId: string): Promise<Outfit> {
    const artistId = await getArtistIdOrThrow();
    return post<Outfit>(`/wardrobe/${artistId}/outfits/${outfitId}/mark-worn`);
  },
};


