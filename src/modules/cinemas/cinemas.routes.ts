import type { FastifyInstance } from "fastify";
import { listCinemasByCitySchema } from "./cinemas.schema.ts";
import { cinemasService } from "./cinemas.service.ts";
import type { CinemasByCityParams } from "./cinemas.types.ts";

export async function cinemasRoutes(app: FastifyInstance): Promise<void> {
  const service = cinemasService(app);

  app.get<{ Params: CinemasByCityParams }>(
    "/cities/:cityId/cinemas",
    { schema: listCinemasByCitySchema },
    (request) => service.listByCity(request.params.cityId),
  );
}
