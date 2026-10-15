import type { FastifyInstance } from "fastify";
import { registerCors } from "./cors.ts";
import { registerErrorHandler } from "./error-handler.ts";
import { registerHelmet } from "./helmet.ts";
import { registerMongo } from "./mongodb.ts";
import { registerRedis } from "./redis.ts";
import { registerRoutes } from "./routes.ts";
import { registerSwagger } from "./swagger.ts";

// Order matters: error handling and security first, data stores next, swagger before routes.
// To add a new startup piece, create a file here and add one line below.
export async function bootstrap(app: FastifyInstance): Promise<void> {
  registerErrorHandler(app);
  await registerHelmet(app);
  await registerCors(app);
  await registerMongo(app);
  await registerRedis(app);
  await registerSwagger(app);
  await registerRoutes(app);
}
