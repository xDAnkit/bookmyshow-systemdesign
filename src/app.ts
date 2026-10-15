import Fastify, { type FastifyInstance } from "fastify";
import { bootstrap } from "./bootstrap/index.ts";

export async function buildApp(): Promise<FastifyInstance> {
  const app = Fastify({ logger: false });
  await bootstrap(app);
  return app;
}
