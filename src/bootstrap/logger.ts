import type { FastifyServerOptions } from "fastify";
import { env } from "../config/env.ts";

// Logs go to stdout. Docker or the host collects them. Pretty output only in development.
export const loggerOptions: FastifyServerOptions["logger"] =
  env.nodeEnv === "development"
    ? { level: env.logLevel, transport: { target: "pino-pretty" } }
    : { level: env.logLevel };
