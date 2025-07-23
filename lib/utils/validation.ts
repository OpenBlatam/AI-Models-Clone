import { z } from 'zod';

// Base validation schemas
export const emailSchema = z.string().email('Invalid email format');
export const passwordSchema = z.string().min(8, 'Password must be at least 8 characters');
export const urlSchema = z.string().url('Invalid URL format');

// User validation
export const userSchema = z.object({
  id: z.string().uuid(),
  email: emailSchema,
  name: z.string().min(1, 'Name is required'),
  image: z.string().url().optional(),
  createdAt: z.date(),
  updatedAt: z.date(),
});

export const createUserSchema = userSchema.omit({ 
  id: true, 
  createdAt: true, 
  updatedAt: true 
});

// Form validation helpers
export const validateForm = <T>(schema: z.ZodSchema<T>, data: unknown): T => {
  return schema.parse(data);
};

export const validateFormSafe = <T>(schema: z.ZodSchema<T>, data: unknown) => {
  return schema.safeParse(data);
};

// Type inference
export type User = z.infer<typeof userSchema>;
export type CreateUser = z.infer<typeof createUserSchema>; 