# ========================
# 1. Dependency Stage
# ========================
FROM node:20-alpine AS deps
WORKDIR /app
RUN npm install -g pnpm
COPY frontend/package.json frontend/pnpm-lock.yaml ./
COPY frontend/package-lock.json ./
RUN pnpm install --frozen-lockfile

# ========================
# 2. Builder Stage
# ========================
FROM node:20-alpine AS builder
WORKDIR /app
RUN npm install -g pnpm
COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ .
RUN pnpm run build

# ========================
# 3. Runner Stage
# ========================
FROM node:20-slim AS runner
EXPOSE 3000
ENV NODE_ENV production
RUN adduser --system --uid 1001 nextjs

WORKDIR /app

# 로그 디렉토리를 생성하고 nextjs 사용자에게 소유권 부여
RUN mkdir -p /app/logs && chown -R 1001 /app/logs
USER nextjs

# 빌드된 Next.js 파일 복사
# .next, public, node_modules 복사
COPY --from=builder --chown=nextjs:nextjs /app/.next /app/.next
COPY --from=builder --chown=nextjs:nextjs /app/node_modules /app/node_modules
COPY --from=builder --chown=nextjs:nextjs /app/public /app/public
COPY frontend/package.json /app/package.json
COPY frontend/pnpm-lock.yaml /app/pnpm-lock.yaml

# Next.js 애플리케이션 시작
CMD ["node", "node_modules/.bin/next", "start"]