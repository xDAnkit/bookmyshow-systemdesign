import { buildApp } from "./app.ts";
import { env } from "./config/env.ts";

const app = await buildApp();

for (const signal of ["SIGINT", "SIGTERM"] as const) {
  process.on(signal, () => {
    app.close().then(() => process.exit(0), () => process.exit(1));
  });
}

try {
  await app.listen({ host: env.host, port: env.port });
} catch (error) {
  app.log.error(error);
  process.exit(1);
}
