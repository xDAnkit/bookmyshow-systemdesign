# BookMyShow

A movie ticket booking system built for System Design learning.

## Stack

- Node.js (22.18 or newer), Fastify
- TypeScript 7 (stable, native compiler, command is `tsc`)
- Oxlint for linting
- MongoDB and Redis (Docker)
- **pnpm is the only package manager.** Do not use npm or yarn. A `preinstall` check stops them.

## Setup

```
pnpm add fastify @fastify/cors @fastify/helmet mongodb ioredis
pnpm add -D typescript@7 oxlint @types/node pino-pretty
corepack use pnpm@latest    # pins the pnpm version in package.json
cp .env.example .env
docker compose up -d        # starts MongoDB and Redis
pnpm run seed               # loads cities, cinemas, shows (safe to re-run)
pnpm run dev
```

The app also starts without MongoDB or Redis if `MONGODB_URI` or `REDIS_URL` is empty.
Data routes then answer 503.

Commit `pnpm-lock.yaml`. The Dockerfile installs with `--frozen-lockfile`.

## Scripts

| Script | What it does |
|---|---|
| `pnpm run dev` | Start with auto restart |
| `pnpm run build` | Compile to `dist/` |
| `pnpm start` | Run the compiled app |
| `pnpm run typecheck` | Type check only |
| `pnpm run lint` | Run Oxlint |
| `pnpm test` | Run tests (no database needed) |
| `pnpm run seed` | Load seed data into MongoDB |

## API

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Server health |
| GET | `/api/v1/cities` | All cities |
| GET | `/api/v1/cities/:cityId/cinemas` | Cinemas in a city |
| GET | `/api/v1/cinemas/:cinemaId/shows` | Shows in a cinema |

## Structure

| Folder | Purpose |
|---|---|
| `src/bootstrap/` | Startup pieces: logger, cors, helmet, mongodb, redis, error handler, routes |
| `src/modules/` | One folder per feature: routes, schema, types, service, repository |
| `src/shared/` | Errors and types used by more than one module |
| `src/config/` | Environment settings |
| `seeds/data/` | Seed data as JSON |
| `scripts/` | Common scripts, such as `seed.ts` |
| `docker/` | One folder per service, each with its own compose file |
| `test/` | Tests |

Logs go to stdout. Docker or the host collects them.
