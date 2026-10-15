import type { FastifyInstance } from "fastify";
import { getDb } from "../../bootstrap/mongodb.ts";
import type { Show } from "./shows.types.ts";

export function showsRepository(app: FastifyInstance) {
  const collection = () => getDb(app).collection("shows");

  return {
    listByCinema: (cinemaId: string) =>
      collection().find<Show>({ cinemaId }, { projection: { _id: 0 } }).sort({ startsAt: 1 }).toArray(),
  };
}
