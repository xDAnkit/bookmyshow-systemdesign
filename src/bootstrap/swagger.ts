import swagger from "@fastify/swagger";
import swaggerUi from "@fastify/swagger-ui";
import type { FastifyInstance } from "fastify";
import { env } from "../config/env.ts";

// Must run before routes are registered, so Swagger can see every route.
// API docs are served at /docs and the raw spec at /docs/json. Off in production.
export async function registerSwagger(app: FastifyInstance): Promise<void> {
  if (env.nodeEnv === "production") {
    return;
  }
  await app.register(swagger, {
    openapi: {
      info: { title: "BookMyShow API", version: "0.1.0" },
      tags: [
        { name: "Health", description: "Server status" },
        { name: "Cities", description: "Cities where shows run" },
        { name: "Cinemas", description: "Cinemas in a city" },
        { name: "Shows", description: "Shows in a cinema" },
      ],
      // Adds the Authorize button. Paste a JWT there and Swagger sends it as "Authorization: Bearer <token>".
      components: {
        securitySchemes: {
          bearerAuth: { type: "http", scheme: "bearer", bearerFormat: "JWT" },
        },
      },
      // Applies the token to every route in Try it out. Public routes can set `security: []` in their schema.
      security: [{ bearerAuth: [] }],
    },
  });
  await app.register(swaggerUi, {
    routePrefix: "/docs",
    uiConfig: { persistAuthorization: true }, // keep the token after a page refresh
  });
}
