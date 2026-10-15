import type { FastifyInstance } from "fastify";
import { notFound } from "../../shared/errors.ts";
import { cinemasRepository } from "../cinemas/cinemas.repository.ts";
import { showsRepository } from "./shows.repository.ts";

export function showsService(app: FastifyInstance) {
  const repository = showsRepository(app);
  const cinemas = cinemasRepository(app);

  return {
    async listByCinema(cinemaId: string) {
      if (!(await cinemas.findById(cinemaId))) {
        throw notFound(`Cinema ${cinemaId} not found`);
      }
      return repository.listByCinema(cinemaId);
    },
  };
}
