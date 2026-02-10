import { BaseRepository } from '@/core/repository/base-repository';
import type { User, Session } from '@/types';
import { ENDPOINTS } from '@/constants/config';
import type { LoginCredentials, RegisterData } from '../domain/auth-types';

export class AuthRepository extends BaseRepository {
  constructor() {
    super();
  }

  async login(credentials: LoginCredentials): Promise<Session> {
    return this.post<Session>(
      ENDPOINTS.AUTH.LOGIN,
      null,
      {
        params: {
          email: credentials.email,
          password: credentials.password,
        },
      }
    );
  }

  async register(data: RegisterData): Promise<User> {
    return this.post<User>(
      ENDPOINTS.AUTH.REGISTER,
      null,
      {
        params: {
          email: data.email,
          username: data.username,
          password: data.password,
        },
      }
    );
  }

  async logout(sessionId: string): Promise<{ success: boolean }> {
    return this.post<{ success: boolean }>(
      ENDPOINTS.AUTH.LOGOUT,
      null,
      {
        params: { session_id: sessionId },
      }
    );
  }

  async verifySession(sessionId: string): Promise<User> {
    return this.get<User>(`${ENDPOINTS.AUTH.VERIFY}/${sessionId}`);
  }

  async getUser(userId: string): Promise<User> {
    return this.get<User>(`${ENDPOINTS.AUTH.USER}/${userId}`);
  }
}

