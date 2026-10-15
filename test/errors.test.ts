import assert from "node:assert/strict";
import { test } from "node:test";
import { buildApp } from "../src/app.ts";

test("unknown route returns 404 in the common error shape", async () => {
  const app = await buildApp();
  const response = await app.inject({ method: "GET", url: "/nope" });

  assert.equal(response.statusCode, 404);
  assert.equal(response.json().error, "NOT_FOUND");
  await app.close();
});

test("data route returns 503 when MongoDB is not connected", async () => {
  const app = await buildApp();
  const response = await app.inject({ method: "GET", url: "/api/v1/cities" });

  assert.equal(response.statusCode, 503);
  assert.equal(response.json().error, "SERVICE_UNAVAILABLE");
  await app.close();
});
