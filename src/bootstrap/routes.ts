import type { FastifyInstance } from "fastify";
import { cinemasRoutes } from "../modules/cinemas/cinemas.routes.ts";
import { citiesRoutes } from "../modules/cities/cities.routes.ts";
import { showsRoutes } from "../modules/shows/shows.routes.ts";

export async function registerRoutes(app: FastifyInstance): Promise<void> {
  app.get(
    "/health",
    { schema: { tags: ["Health"], summary: "Server health" } },
    async () => ({ status: "ok" }),
  );

  await app.register(
    async (api) => {
      await api.register(citiesRoutes);
      await api.register(cinemasRoutes);
      await api.register(showsRoutes);
    },
    { prefix: "/api/v1" },
  );
}
