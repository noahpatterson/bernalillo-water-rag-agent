FROM node:24-bookworm-slim AS base

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1 \
    PNPM_HOME=/pnpm \
    PATH=/pnpm:$PATH

RUN corepack enable && corepack prepare pnpm@10 --activate

FROM base AS deps

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

FROM base AS builder

# eve build inlines connection URLs and auth flags. Set the compose-network
# FastAPI origin and public-demo auth here, not only at container runtime.
ENV KNOWLEDGE_API_BASE_URL=http://api.localhost:8000 \
    EVE_ALLOW_ANONYMOUS=1

COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm exec eve build && pnpm build

FROM base AS runner

ENV NODE_ENV=production \
    PORT=3000

COPY --from=builder /app /app
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 3000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
