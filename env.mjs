import { createEnv } from "@t3-oss/env-nextjs";
import { z } from "zod";

const isDevelopment = process.env.NODE_ENV === "development";

export const env = createEnv({
  server: {
    AUTH_SECRET: isDevelopment 
      ? z.string().default("development-secret")
      : z.string().min(1, "AUTH_SECRET is required"),
    GOOGLE_CLIENT_ID: isDevelopment
      ? z.string().default("development-client-id")
      : z.string().min(1, "GOOGLE_CLIENT_ID is required"),
    GOOGLE_CLIENT_SECRET: isDevelopment
      ? z.string().default("development-client-secret")
      : z.string().min(1, "GOOGLE_CLIENT_SECRET is required"),
    DATABASE_URL: isDevelopment
      ? z.string().default("postgresql://postgres:postgres@localhost:5432/postgres")
      : z.string().min(1, "DATABASE_URL is required"),
  },
  client: {
    NEXT_PUBLIC_APP_URL: z.string().url().default("http://localhost:3000"),
  },
  runtimeEnv: {
    AUTH_SECRET: process.env.AUTH_SECRET,
    GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET,
    DATABASE_URL: process.env.DATABASE_URL,
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
  },
  skipValidation: !!process.env.SKIP_ENV_VALIDATION,
});
