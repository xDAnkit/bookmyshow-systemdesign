import type { FastifyInstance } from "fastify";
import { notFound } from "../../shared/errors.ts";
import { citiesRepository } from "../cities/cities.repository.ts";
import { cinemasRepository } from "./cinemas.repository.ts";

export function cinemasService(app: FastifyInstance) {
  const repository = cinemasRepository(app);
  const cities = citiesRepository(app);

  return {
    async listByCity(cityId: string) {
      if (!(await cities.findById(cityId))) {
        throw notFound(`City ${cityId} not found`);
      }
      return repository.listByCity(cityId);
    },
  };
}
