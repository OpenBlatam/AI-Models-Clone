// Calendar Types
export interface CalendarEvent {
  id: string;
  title: string;
  description: string;
  event_type: EventType;
  start_time: string;
  end_time: string;
  location?: string;
  attendees?: string[];
  reminders?: string[];
  protocol_requirements?: string[];
  wardrobe_requirements?: string;
  notes?: string;
}

export interface CalendarEventFormData {
  title: string;
  description: string;
  event_type: EventType;
  start_time: Date;
  end_time: Date;
  location?: string;
  attendees?: string[];
  protocol_requirements?: string[];
  wardrobe_requirements?: string;
  notes?: string;
}

export const EventTypeMap = {
  concert: 'Concert',
  interview: 'Interview',
  photoshoot: 'Photoshoot',
  rehearsal: 'Rehearsal',
  meeting: 'Meeting',
  travel: 'Travel',
  rest: 'Rest',
  other: 'Other',
} as const;

export type EventType = keyof typeof EventTypeMap;

// Routine Types
export interface RoutineTask {
  id: string;
  title: string;
  description: string;
  routine_type: RoutineType;
  scheduled_time: string;
  duration_minutes: number;
  priority: number;
  days_of_week: number[];
  is_required: boolean;
  reminders?: string[];
  notes?: string;
}

export interface RoutineTaskFormData {
  title: string;
  description: string;
  routine_type: RoutineType;
  scheduled_time: string;
  duration_minutes: number;
  priority: number;
  days_of_week: number[];
  is_required: boolean;
  notes?: string;
}

export const RoutineTypeMap = {
  morning: 'Morning',
  afternoon: 'Afternoon',
  evening: 'Evening',
  night: 'Night',
  daily: 'Daily',
  weekly: 'Weekly',
  custom: 'Custom',
} as const;

export type RoutineType = keyof typeof RoutineTypeMap;

export const RoutineStatusMap = {
  pending: 'Pending',
  in_progress: 'In Progress',
  completed: 'Completed',
  skipped: 'Skipped',
  overdue: 'Overdue',
} as const;

export type RoutineStatus = keyof typeof RoutineStatusMap;

// Protocol Types
export interface Protocol {
  id: string;
  title: string;
  description: string;
  category: ProtocolCategory;
  priority: ProtocolPriority;
  rules: string[];
  do_s?: string[];
  dont_s?: string[];
  context?: string;
  applicable_events?: string[];
  notes?: string;
}

export const ProtocolCategoryMap = {
  social_media: 'Social Media',
  interview: 'Interview',
  performance: 'Performance',
  public_appearance: 'Public Appearance',
  general: 'General',
} as const;

export type ProtocolCategory = keyof typeof ProtocolCategoryMap;

export const ProtocolPriorityMap = {
  critical: 'Critical',
  high: 'High',
  medium: 'Medium',
  low: 'Low',
} as const;

export type ProtocolPriority = keyof typeof ProtocolPriorityMap;

// Wardrobe Types
export interface WardrobeItem {
  id: string;
  name: string;
  category: string;
  color: string;
  brand?: string;
  size?: string;
  season: Season;
  dress_codes: DressCode[];
  notes?: string;
  image_url?: string;
  last_worn?: string;
  wear_count?: number;
}

export interface Outfit {
  id: string;
  name: string;
  items: string[];
  dress_code: DressCode;
  occasion: string;
  season: Season;
  notes?: string;
  image_url?: string;
  last_worn?: string;
  wear_count?: number;
}

export const DressCodeMap = {
  formal: 'Formal',
  smart_casual: 'Smart Casual',
  casual: 'Casual',
  sporty: 'Sporty',
  black_tie: 'Black Tie',
  business: 'Business',
} as const;

export type DressCode = keyof typeof DressCodeMap;

export const SeasonMap = {
  spring: 'Spring',
  summer: 'Summer',
  fall: 'Fall',
  winter: 'Winter',
  all_season: 'All Season',
} as const;

export type Season = keyof typeof SeasonMap;

// Dashboard Types
export interface DashboardData {
  upcoming_events: {
    count: number;
    events: CalendarEvent[];
  };
  routines: {
    pending_count: number;
    completed_today: number;
    total_routines: number;
  };
  protocols: {
    critical_count: number;
    total_protocols: number;
  };
  wardrobe: {
    total_items: number;
    total_outfits: number;
  };
}

export interface DailySummary {
  summary: string;
  events_count: number;
  pending_routines_count: number;
  recommendations: string[];
  motivation: string;
}


