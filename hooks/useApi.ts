import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAppStore } from '../lib/store';

interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

interface ApiError {
  message: string;
  code?: string;
}

const API_BASE_URL = 'https://api.example.com';

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const { user } = useAppStore.getState();
    const token = user ? await this.getAuthToken() : null;

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Network error');
    }
  }

  private async getAuthToken(): Promise<string | null> {
    // Implement secure token storage
    return null;
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

const apiClient = new ApiClient();

export const useApi = {
  // Query hooks
  usePosts: () => {
    return useQuery({
      queryKey: ['posts'],
      queryFn: () => apiClient.get('/posts'),
      staleTime: 5 * 60 * 1000, // 5 minutes
    });
  },

  usePost: (id: string) => {
    return useQuery({
      queryKey: ['post', id],
      queryFn: () => apiClient.get(`/posts/${id}`),
      enabled: !!id,
    });
  },

  useUser: (id: string) => {
    return useQuery({
      queryKey: ['user', id],
      queryFn: () => apiClient.get(`/users/${id}`),
      enabled: !!id,
    });
  },

  // Mutation hooks
  useCreatePost: () => {
    const queryClient = useQueryClient();
    
    return useMutation({
      mutationFn: (data: { content: string; imageUrl?: string }) =>
        apiClient.post('/posts', data),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['posts'] });
      },
    });
  },

  useUpdatePost: () => {
    const queryClient = useQueryClient();
    
    return useMutation({
      mutationFn: ({ id, data }: { id: string; data: any }) =>
        apiClient.put(`/posts/${id}`, data),
      onSuccess: (_, { id }) => {
        queryClient.invalidateQueries({ queryKey: ['posts'] });
        queryClient.invalidateQueries({ queryKey: ['post', id] });
      },
    });
  },

  useDeletePost: () => {
    const queryClient = useQueryClient();
    
    return useMutation({
      mutationFn: (id: string) => apiClient.delete(`/posts/${id}`),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['posts'] });
      },
    });
  },

  useLogin: () => {
    const { setUser, setAuthenticated } = useAppStore();
    
    return useMutation({
      mutationFn: (credentials: { email: string; password: string }) =>
        apiClient.post('/auth/login', credentials),
      onSuccess: (data) => {
        setUser(data.data.user);
        setAuthenticated(true);
      },
    });
  },

  useLogout: () => {
    const { logout } = useAppStore();
    
    return useMutation({
      mutationFn: () => apiClient.post('/auth/logout', {}),
      onSuccess: () => {
        logout();
      },
    });
  },
}; 