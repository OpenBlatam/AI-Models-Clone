import { z } from 'zod';

// Calendar Event Validation
export const calendarEventSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title too long'),
  description: z.string().max(1000, 'Description too long').optional(),
  event_type: z.enum(['concert', 'interview', 'photoshoot', 'rehearsal', 'meeting', 'travel', 'rest', 'other']),
  start_time: z.date(),
  end_time: z.date(),
  location: z.string().max(200).optional(),
  attendees: z.array(z.string()).optional(),
  protocol_requirements: z.array(z.string()).optional(),
  wardrobe_requirements: z.string().max(500).optional(),
  notes: z.string().max(1000).optional(),
}).refine((data) => data.end_time > data.start_time, {
  message: 'End time must be after start time',
  path: ['end_time'],
});

// Routine Task Validation
export const routineTaskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title too long'),
  description: z.string().max(1000, 'Description too long').optional(),
  routine_type: z.enum(['morning', 'afternoon', 'evening', 'night', 'daily', 'weekly', 'custom']),
  scheduled_time: z.string().regex(/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$/, 'Invalid time format'),
  duration_minutes: z.number().int().min(1).max(1440),
  priority: z.number().int().min(1).max(10),
  days_of_week: z.array(z.number().int().min(0).max(6)),
  is_required: z.boolean(),
  notes: z.string().max(1000).optional(),
});

// Protocol Validation
export const protocolSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title too long'),
  description: z.string().max(1000, 'Description too long').optional(),
  category: z.enum(['social_media', 'interview', 'performance', 'public_appearance', 'general']),
  priority: z.enum(['critical', 'high', 'medium', 'low']),
  rules: z.array(z.string().min(1)).min(1, 'At least one rule is required'),
  do_s: z.array(z.string()).optional(),
  dont_s: z.array(z.string()).optional(),
  context: z.string().max(500).optional(),
  applicable_events: z.array(z.string()).optional(),
  notes: z.string().max(1000).optional(),
});

// Wardrobe Item Validation
export const wardrobeItemSchema = z.object({
  name: z.string().min(1, 'Name is required').max(200, 'Name too long'),
  category: z.string().min(1, 'Category is required'),
  color: z.string().min(1, 'Color is required'),
  brand: z.string().max(100).optional(),
  size: z.string().max(50).optional(),
  season: z.enum(['spring', 'summer', 'fall', 'winter', 'all_season']),
  dress_codes: z.array(z.enum(['formal', 'smart_casual', 'casual', 'sporty', 'black_tie', 'business'])),
  notes: z.string().max(1000).optional(),
  image_url: z.string().url('Invalid URL').optional().or(z.literal('')),
});

// Outfit Validation
export const outfitSchema = z.object({
  name: z.string().min(1, 'Name is required').max(200, 'Name too long'),
  items: z.array(z.string()).min(1, 'At least one item is required'),
  dress_code: z.enum(['formal', 'smart_casual', 'casual', 'sporty', 'black_tie', 'business']),
  occasion: z.string().min(1, 'Occasion is required'),
  season: z.enum(['spring', 'summer', 'fall', 'winter', 'all_season']),
  notes: z.string().max(1000).optional(),
  image_url: z.string().url('Invalid URL').optional().or(z.literal('')),
});

// Type exports
export type CalendarEventFormData = z.infer<typeof calendarEventSchema>;
export type RoutineTaskFormData = z.infer<typeof routineTaskSchema>;
export type ProtocolFormData = z.infer<typeof protocolSchema>;
export type WardrobeItemFormData = z.infer<typeof wardrobeItemSchema>;
export type OutfitFormData = z.infer<typeof outfitSchema>;


