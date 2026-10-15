const city = {
  type: "object",
  properties: {
    id: { type: "string" },
    name: { type: "string" },
    state: { type: "string" },
  },
  required: ["id", "name", "state"],
} as const;

export const listCitiesSchema = {
  tags: ["Cities"],
  summary: "List all cities",
  response: { 200: { type: "array", items: city } },
} as const;
