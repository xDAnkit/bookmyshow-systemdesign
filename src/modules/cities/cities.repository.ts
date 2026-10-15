import type { FastifyInstance } from "fastify";
import { getDb } from "../../bootstrap/mongodb.ts";
import type { City } from "./cities.types.ts";

export function citiesRepository(app: FastifyInstance) {
  const collection = () => getDb(app).collection("cities");

  return {
    list: () => collection().find<City>({}, { projection: { _id: 0 } }).sort({ name: 1 }).toArray(),
    findById: (id: string) => collection().findOne<City>({ id }, { projection: { _id: 0 } }),
  };
}
