import type { FastifyInstance } from "fastify";
import { listCitiesSchema } from "./cities.schema.ts";
import { citiesService } from "./cities.service.ts";

export async function citiesRoutes(app: FastifyInstance): Promise<void> {
  const service = citiesService(app);

  app.get("/cities", { schema: listCitiesSchema }, () => service.list());
}
