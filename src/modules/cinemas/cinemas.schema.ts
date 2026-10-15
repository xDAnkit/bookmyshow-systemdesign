import { errorSchema } from "../../shared/error.schema.ts";

const cinema = {
  type: "object",
  properties: {
    id: { type: "string" },
    cityId: { type: "string" },
    name: { type: "string" },
    address: { type: "string" },
  },
  required: ["id", "cityId", "name", "address"],
} as const;

export const listCinemasByCitySchema = {
  tags: ["Cinemas"],
  summary: "List cinemas in a city",
  params: {
    type: "object",
    properties: { cityId: { type: "string", minLength: 1, description: "City id, for example city_mumbai" } },
    required: ["cityId"],
  },
  response: { 200: { type: "array", items: cinema }, 404: errorSchema },
} as const;
