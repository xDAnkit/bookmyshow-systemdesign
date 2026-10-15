import assert from "node:assert/strict";
import { test } from "node:test";
import { buildApp } from "../src/app.ts";

test("GET /health returns ok", async () => {
  const app = await buildApp();
  const response = await app.inject({ method: "GET", url: "/health" });

  assert.equal(response.statusCode, 200);
  assert.deepEqual(response.json(), { status: "ok" });
  await app.close();
});
