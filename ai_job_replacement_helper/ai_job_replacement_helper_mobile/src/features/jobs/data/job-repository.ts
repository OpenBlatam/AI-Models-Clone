import { BaseRepository } from '@/core/repository/base-repository';
import { ENDPOINTS } from '@/constants/config';
import type { Job, JobSwipeResponse } from '@/types';
import type { JobSearchParams, JobSwipeAction, JobApplication } from '../domain/job-types';

export class JobRepository extends BaseRepository {
  constructor() {
    super();
  }

  async searchJobs(userId: string, params: JobSearchParams): Promise<{ jobs: Job[]; total: number }> {
    return this.get<{ jobs: Job[]; total: number }>(`${ENDPOINTS.JOBS.SEARCH}/${userId}`, {
      params,
    });
  }

  async swipeJob(userId: string, action: JobSwipeAction): Promise<JobSwipeResponse> {
    return this.post<JobSwipeResponse>(`${ENDPOINTS.JOBS.SWIPE}/${userId}`, {
      job_id: action.jobId,
      action: action.action,
    });
  }

  async applyToJob(userId: string, application: JobApplication): Promise<{ success: boolean; message: string }> {
    return this.post<{ success: boolean; message: string }>(
      `${ENDPOINTS.JOBS.APPLY}/${userId}`,
      null,
      {
        params: {
          job_id: application.jobId,
          cover_letter: application.coverLetter,
        },
      }
    );
  }

  async getSavedJobs(userId: string): Promise<Job[]> {
    const response = await this.get<{ jobs: Job[] }>(`${ENDPOINTS.JOBS.SAVED}/${userId}`);
    return response.jobs || [];
  }

  async getLikedJobs(userId: string): Promise<Job[]> {
    const response = await this.get<{ jobs: Job[] }>(`${ENDPOINTS.JOBS.LIKED}/${userId}`);
    return response.jobs || [];
  }

  async getMatches(userId: string): Promise<Job[]> {
    const response = await this.get<{ matches: Job[] }>(`${ENDPOINTS.JOBS.MATCHES}/${userId}`);
    return response.matches || [];
  }
}

