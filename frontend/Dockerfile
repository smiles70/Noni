# syntax=docker/dockerfile:1.6
# Multi-stage build for the Noni frontend.
# Stage 1: build the Vite bundle.
# Stage 2: serve the static bundle with nginx.

# ---------- Stage 1: builder ----------
FROM node:18-alpine AS builder

WORKDIR /app

# Cache deps separately from source.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---------- Stage 2: runtime ----------
FROM nginx:1.27-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -q -O - http://127.0.0.1/ >/dev/null 2>&1 || exit 1
