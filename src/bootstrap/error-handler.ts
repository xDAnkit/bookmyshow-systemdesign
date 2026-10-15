import type { FastifyInstance } from "fastify";
import { AppError } from "../shared/errors.ts";
import type { ErrorBody } from "../shared/types.ts";

// Fastify gives the handler an `unknown` error. Schema validation failures carry a `validation` field.
function isValidationError(error: unknown): error is Error & { validation: unknown } {
  return error instanceof Error && "validation" in error && Boolean(error.validation);
}

export function registerErrorHandler(app: FastifyInstance): void {
  app.setNotFoundHandler((request, reply) => {
    const body: ErrorBody = {
      error: "NOT_FOUND",
      message: `Route ${request.method} ${request.url} not found`,
    };
    return reply.status(404).send(body);
  });

  app.setErrorHandler((error, request, reply) => {
    if (error instanceof AppError) {
      const body: ErrorBody = { error: error.code, message: error.message };
      return reply.status(error.statusCode).send(body);
    }
    if (isValidationError(error)) {
      const body: ErrorBody = { error: "BAD_REQUEST", message: error.message };
      return reply.status(400).send(body);
    }
    request.log.error(error);
    const body: ErrorBody = { error: "INTERNAL", message: "Something went wrong" };
    return reply.status(500).send(body);
  });
}
