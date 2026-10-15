// Load .env from the working directory so pm2 and `node dist/server.js` work like `pnpm dev`.
// Real environment variables win over the file. A missing .env is fine.
try {
  process.loadEnvFile();
} catch {}

const str = (key: string, fallback: string): string => process.env[key] || fallback;

const port = Number(str("PORT", "3000"));
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error(`Invalid PORT: ${process.env.PORT}`);
}

export const env = {
  nodeEnv: str("NODE_ENV", "development"),
  host: str("HOST", "127.0.0.1"),
  port,
  logLevel: str("LOG_LEVEL", "info"),
  corsOrigins: str("CORS_ORIGINS", "")
    .split(",")
    .map((origin) => origin.trim())
    .filter(Boolean),
  // An empty URL means the service is skipped at startup.
  mongodbUri: process.env.MONGODB_URI || undefined,
  mongodbDb: str("MONGODB_DB", "bookmyshow"),
  redisUrl: process.env.REDIS_URL || undefined,
};
