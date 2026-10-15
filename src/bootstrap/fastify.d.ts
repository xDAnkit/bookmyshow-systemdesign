import type { Redis } from "ioredis";
import type { Db } from "mongodb";

declare module "fastify" {
  interface FastifyInstance {
    // Set only when MONGODB_URI / REDIS_URL is configured.
    mongo?: Db;
    redis?: Redis;
  }
}
