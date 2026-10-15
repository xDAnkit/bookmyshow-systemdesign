# BookMyShow (System Design S1)

A BookMyShow-style movie ticket booking system, built as a system design learning project.

This file is the single source of truth for all AI coding tools (Claude Code, Codex, Cursor, Antigravity, Grok, and others) and all their subagents. Edit rules here only.

## Project status

- Boilerplate in place: cities, cinemas, shows APIs with MongoDB and Redis wiring.
- Update this file as decisions are made.

## Stack

- Package manager: **pnpm only**. Never write or suggest `npm` or `yarn` commands, in code, docs, scripts, or Dockerfiles. Commit `pnpm-lock.yaml`.
- Node.js, Fastify, Oxlint.
- TypeScript **7 stable** (`typescript@7`, native compiler, command `tsc`). Do not use `tsgo` or `@typescript/native-preview`, those are old nightly builds. TS 7 has no stable programmatic API yet (expected in 7.1), so avoid tools that need it, such as typescript-eslint.
- Node runs `.ts` files directly (type stripping), so use only erasable syntax and `.ts` import extensions.
- MongoDB (official driver) and Redis (`ioredis`). Elasticsearch later.

## Where things go

| Kind of code | Folder |
|---|---|
| Starts with the app, connects or closes (cors, helmet, mongodb, redis, jwt plugin) | `src/bootstrap/` |
| Business feature with routes | `src/modules/<name>/` with `routes`, `schema`, `types`, `service`, `repository` files |
| Calls someone else's API (email, SMS, WhatsApp, payment) | `src/integrations/<service>/` (create on first use) |
| Small helper with no I/O | `src/shared/utils/` (create on first use) |
| Types used by one module | That module's `*.types.ts` |
| Types used by many modules | `src/shared/types.ts` |
| Settings and secrets | `src/config/env.ts`, `.env.example` |
| Seed data and seed script | `seeds/data/`, `scripts/seed.ts` |
| Other common scripts | `scripts/` |
| Docker | `docker/<service>/compose.yml`, included from root `docker-compose.yml`. Pin image versions, bind ports to 127.0.0.1 |
| Logs | stdout only. A local `logs/` folder is gitignored |

- Do not create empty folders ahead of time.
- Routes stay thin. Logic goes in the service. Data access goes in the repository.

## Conventions

- All files in the repo are written in English.
- Keep changes small and simple. No speculative abstractions.
- Ask before adding a new dependency.

## Guardrails (strict, no exceptions)

1. **Ask before executing.** Never run any command or tool without the user's permission.
2. **No git or GitHub commands.** Only read-only git is allowed: `status`, `diff`, `log`, `show`, `branch` (list). Everything else (add, commit, push, pull, reset, checkout, stash, and all `gh`) is run by the user only. If any agent tries, stop it.
3. **No direct database access.** Never touch the database directly. Never run or write delete operations (delete, drop, truncate, flush) unless the user explicitly instructs it. Hooks block this even in auto mode.
4. **No deleting.** Never delete any file or folder.
5. **Stay inside this folder.** Never read, write, or `cd` outside the project root. If something outside is needed, ask the user.
6. **Plan first, then go.** Never create or change anything until the user has seen a plan and approved it with a clear "go".
7. **Always ask when unsure.** If anything is missing or unclear, talk to the user first.
8. **No outside network.** No web, no MCP tools, no curl or ssh, unless the user opens the network (see below). Exception: pnpm may reach the package registry (see "pnpm is allowed").

## pnpm is allowed

- Allowed without `APPROVED` or `ALLOW_NET`: `pnpm install`, `add`, `update`, `run <script>`, `dev`, `build`, `test`, `start`, `lint`, `typecheck`.
- Still user-only: `pnpm seed` and `pnpm run seed` (writes to the database).
- Still gated: `pnpm dlx`, `pnpm exec`, `pnpm publish`, and anything with `npm` or `yarn`.
- Policy, not enforced by hooks: ask the user before adding a new dependency, and say why it is needed.
- Editing `package.json` scripts still needs `APPROVED`, so a script cannot be changed silently.

## How approval works

- The user creates `.agents/APPROVED` to give the "go". Agents cannot create it.
- The user removes `.agents/APPROVED` to lock the repo again.
- Without that file, hooks block all file writes and mutating shell commands.
- The user runs `touch .agents/ALLOW_NET` to open the network. It closes by itself after 30 minutes. Run `touch` again to renew.
- Database delete code and DB tools stay blocked even when `APPROVED` or `ALLOW_NET` exists.
- Hooks fail closed: if the guard crashes, the call is blocked.

## Hooks (safety net if a rule is bypassed)

- One shared script: `.agents/hooks/guard.py`. All tool configs only call it.
- Protected from agents: `.agents/`, `.claude/`, `.cursor/`, `.codex/`, `.gemini/`, `.grok/`. Only the user edits them.

| Tool | Config | Notes |
|---|---|---|
| Claude Code | `.claude/settings.json` | All tools, fail closed |
| Cursor | `.cursor/hooks.json` | `preToolUse` covers writes and deletes, `failClosed` on |
| Codex | `.codex/hooks.json`, `.codex/config.toml` | User must trust the hooks in `/hooks`. Hosted web search is not hookable |
| Antigravity | `.agents/hooks.json` | User must mark the workspace as trusted. Fail behavior is undocumented |
| Grok | Reads `.claude/settings.json` and `.cursor/hooks.json` | User must run `/hooks-trust`. Crash or timeout fails open, so keep the guard fast |
- Self-check: `python3 .agents/hooks/test_guard.py`.

| Hook blocks | Rule |
|---|---|
| Any git except status, diff, log, show, branch list. All `gh` | 2 |
| `psql`, `mongosh`, `mysql`, `redis-cli`, `prisma migrate`, `docker exec`, DB MCP tools, SQL or Mongo delete (in commands and in written code) | 3 |
| `rm`, `rmdir`, `unlink`, `find -delete`, `os.remove`, `rmtree` | 4 |
| `curl`, `wget`, `ssh`, `npm` and `yarn` installs, `pnpm dlx`, `pnpm publish`, `pip install`, web tools, all MCP tools (until `ALLOW_NET`) | 8 |
| `pnpm seed`, `pnpm run seed`, `scripts/seed` (writes to the database) | 3 |
| `python -c`, `node -e`, `eval`, heredoc interpreters (cannot be inspected) | 1 |
| Paths outside the project root (`..`, `~`, `/abs`) | 5 |
| File writes and mutating commands without `.agents/APPROVED` | 1, 6 |
