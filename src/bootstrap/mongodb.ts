import type { FastifyInstance } from "fastify";
import { MongoClient, type Db } from "mongodb";
import { env } from "../config/env.ts";
import { serviceUnavailable } from "../shared/errors.ts";

export async function registerMongo(app: FastifyInstance): Promise<void> {
  if (!env.mongodbUri) {
    app.log.warn("MONGODB_URI is not set, skipping MongoDB");
    return;
  }
  const client = new MongoClient(env.mongodbUri);
  await client.connect();
  app.decorate("mongo", client.db(env.mongodbDb));
  app.addHook("onClose", async () => {
    await client.close();
  });
}

// Repositories call this. It gives a clear 503 when MongoDB is not connected.
export function getDb(app: FastifyInstance): Db {
  if (!app.mongo) {
    throw serviceUnavailable("Database is not connected");
  }
  return app.mongo;
}
