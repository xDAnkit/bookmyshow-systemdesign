import { errorSchema } from "../../shared/error.schema.ts";

const show = {
  type: "object",
  properties: {
    id: { type: "string" },
    cinemaId: { type: "string" },
    movieTitle: { type: "string" },
    language: { type: "string" },
    format: { type: "string" },
    startsAt: { type: "string" },
    price: { type: "number" },
  },
  required: ["id", "cinemaId", "movieTitle", "language", "format", "startsAt", "price"],
} as const;

export const listShowsByCinemaSchema = {
  tags: ["Shows"],
  summary: "List shows in a cinema",
  params: {
    type: "object",
    properties: { cinemaId: { type: "string", minLength: 1, description: "Cinema id, for example cinema_mumbai_1" } },
    required: ["cinemaId"],
  },
  response: { 200: { type: "array", items: show }, 404: errorSchema },
} as const;
