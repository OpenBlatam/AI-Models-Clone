import { getArtistId } from '@/utils/storage';
import { ApiError } from '@/utils/api-client';

export class BaseService {
  protected async getArtistIdOrThrow(): Promise<string> {
    const artistId = await getArtistId();
    if (!artistId) {
      throw new ApiError(401, 'Unauthorized', undefined, 'Artist ID not found. Please login first.');
    }
    return artistId;
  }

  protected handleError(error: unknown): never {
    if (error instanceof ApiError) {
      throw error;
    }
    if (error instanceof Error) {
      throw new ApiError(500, 'Internal Server Error', undefined, error.message);
    }
    throw new ApiError(500, 'Internal Server Error', undefined, 'An unknown error occurred');
  }
}


