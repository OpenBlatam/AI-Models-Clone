import { CalendarEvent, RoutineTask, Protocol, WardrobeItem, Outfit, DashboardData, DailySummary } from './index';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface CreateResponse {
  id: string;
  created_at: string;
}

export interface UpdateResponse {
  id: string;
  updated_at: string;
}

export interface DeleteResponse {
  id: string;
  deleted_at: string;
}

// Re-export domain types
export type {
  CalendarEvent,
  RoutineTask,
  Protocol,
  WardrobeItem,
  Outfit,
  DashboardData,
  DailySummary,
};


