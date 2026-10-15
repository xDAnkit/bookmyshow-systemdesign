# The pnpm version comes from the "packageManager" field in package.json (set it with: corepack use pnpm@latest).
FROM node:24-alpine AS build
RUN corepack enable
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY tsconfig*.json ./
COPY src ./src
RUN pnpm run build

FROM node:24-alpine
RUN corepack enable
WORKDIR /app
ENV NODE_ENV=production
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile --prod
COPY --from=build /app/dist ./dist
USER node
EXPOSE 3000
CMD ["node", "dist/server.js"]
