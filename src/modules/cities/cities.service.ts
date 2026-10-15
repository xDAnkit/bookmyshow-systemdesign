import type { FastifyInstance } from "fastify";
import { citiesRepository } from "./cities.repository.ts";

export function citiesService(app: FastifyInstance) {
  const repository = citiesRepository(app);

  return {
    list: () => repository.list(),
  };
}
