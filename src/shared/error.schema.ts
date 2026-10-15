// Shape of every error response. Used in route schemas so Swagger documents it.
export const errorSchema = {
  type: "object",
  properties: {
    error: { type: "string" },
    message: { type: "string" },
  },
  required: ["error", "message"],
} as const;
