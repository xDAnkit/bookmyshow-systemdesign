import type { FastifyInstance } from "fastify";
import { getDb } from "../../bootstrap/mongodb.ts";
import type { Cinema } from "./cinemas.types.ts";

export function cinemasRepository(app: FastifyInstance) {
  const collection = () => getDb(app).collection("cinemas");

  return {
    listByCity: (cityId: string) =>
      collection().find<Cinema>({ cityId }, { projection: { _id: 0 } }).sort({ name: 1 }).toArray(),
    findById: (id: string) => collection().findOne<Cinema>({ id }, { projection: { _id: 0 } }),
  };
}
