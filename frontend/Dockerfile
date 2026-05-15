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

# Vite reads VITE_* from the environment at build time. Surfacing them
# as build ARGs keeps the values out of the image tag and lets
# docker-compose forward them from the project's .env file.
#
# Auth selection (ADR 0024):
#   VITE_AUTH_PROVIDER=mock  -> default; dev/tests; no Clerk required.
#   VITE_AUTH_PROVIDER=clerk -> production path; requires
#                               VITE_CLERK_PUBLISHABLE_KEY (pk_test_*
#                               in dev, pk_live_* in prod).
ARG VITE_AUTH_PROVIDER=mock
ARG VITE_CLERK_PUBLISHABLE_KEY=
ENV VITE_AUTH_PROVIDER=$VITE_AUTH_PROVIDER
ENV VITE_CLERK_PUBLISHABLE_KEY=$VITE_CLERK_PUBLISHABLE_KEY

RUN npm run build

# ---------- Stage 2: runtime ----------
FROM nginx:1.27-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -q -O - http://127.0.0.1/ >/dev/null 2>&1 || exit 1
