import cors from "@fastify/cors";
import type { FastifyInstance } from "fastify";
import { env } from "../config/env.ts";

export async function registerCors(app: FastifyInstance): Promise<void> {
  // No origins configured means no CORS headers at all.
  await app.register(cors, { origin: env.corsOrigins.length > 0 ? env.corsOrigins : false });
}
