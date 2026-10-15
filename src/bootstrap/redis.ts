import type { FastifyInstance } from "fastify";
import { Redis } from "ioredis";
import { env } from "../config/env.ts";

export async function registerRedis(app: FastifyInstance): Promise<void> {
  if (!env.redisUrl) {
    app.log.warn("REDIS_URL is not set, skipping Redis");
    return;
  }
  const redis = new Redis(env.redisUrl, { maxRetriesPerRequest: 2 });
  await redis.ping();
  app.decorate("redis", redis);
  app.addHook("onClose", async () => {
    await redis.quit();
  });
}
