import type { FastifyInstance } from "fastify";
import { listShowsByCinemaSchema } from "./shows.schema.ts";
import { showsService } from "./shows.service.ts";
import type { ShowsByCinemaParams } from "./shows.types.ts";

export async function showsRoutes(app: FastifyInstance): Promise<void> {
  const service = showsService(app);

  app.get<{ Params: ShowsByCinemaParams }>(
    "/cinemas/:cinemaId/shows",
    { schema: listShowsByCinemaSchema },
    (request) => service.listByCinema(request.params.cinemaId),
  );
}
