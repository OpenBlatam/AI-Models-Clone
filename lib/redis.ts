import { Redis } from "ioredis";

const redisUrl = process.env.REDIS_URL || "redis://localhost:6379";

export const redis = new Redis(redisUrl, {
  retryStrategy: (times) => {
    const delay = Math.min(times * 50, 2000);
    return delay;
  },
  maxRetriesPerRequest: 3,
});

redis.on("error", (error) => {
  console.error("[REDIS_ERROR]", error);
});

redis.on("connect", () => {
  console.log("[REDIS] Connected successfully");
});

// Helper function to safely get data from Redis
export async function getFromRedis(key: string): Promise<any> {
  try {
    const data = await redis.get(key);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error("[REDIS_GET_ERROR]", error);
    return null;
  }
}

// Helper function to safely set data in Redis
export async function setInRedis(key: string, value: any, expireSeconds?: number): Promise<void> {
  try {
    const stringValue = JSON.stringify(value);
    if (expireSeconds) {
      await redis.set(key, stringValue, "EX", expireSeconds);
    } else {
      await redis.set(key, stringValue);
    }
  } catch (error) {
    console.error("[REDIS_SET_ERROR]", error);
  }
}

// Helper function to safely delete data from Redis
export async function deleteFromRedis(key: string): Promise<void> {
  try {
    await redis.del(key);
  } catch (error) {
    console.error("[REDIS_DELETE_ERROR]", error);
  }
} 