// Loads seeds/data/*.json into MongoDB. Safe to run many times: it only upserts by id.
// It never removes data. Run it yourself: pnpm run seed
import { readFile } from "node:fs/promises";
import { MongoClient } from "mongodb";

const uri = process.env.MONGODB_URI || "mongodb://localhost:27017";
const dbName = process.env.MONGODB_DB || "bookmyshow";

interface SeedDoc {
  id: string;
}

async function load(name: string): Promise<SeedDoc[]> {
  const file = new URL(`../seeds/data/${name}.json`, import.meta.url);
  return JSON.parse(await readFile(file, "utf8")) as SeedDoc[];
}

const client = new MongoClient(uri);
try {
  await client.connect();
  const db = client.db(dbName);

  for (const name of ["cities", "cinemas", "shows"]) {
    const docs = await load(name);
    const collection = db.collection(name);
    await collection.createIndex({ id: 1 }, { unique: true });
    await collection.bulkWrite(
      docs.map((doc) => ({
        updateOne: { filter: { id: doc.id }, update: { $set: doc }, upsert: true },
      })),
    );
    console.log(`${name}: ${docs.length} upserted`);
  }

  await db.collection("cinemas").createIndex({ cityId: 1 });
  await db.collection("shows").createIndex({ cinemaId: 1 });
} finally {
  await client.close();
}
