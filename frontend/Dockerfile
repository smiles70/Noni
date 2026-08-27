# syntax=docker/dockerfile:1.6
# Multi-stage build for the Mynaani frontend.
# Stage 1: build the Vite bundle.
# Stage 2: serve the static bundle with nginx.

# ---------- Stage 1: builder ----------
FROM node:18-alpine AS builder

WORKDIR /app

# Cache deps separately from source.
# package-lock.json is managed at the monorepo root; install from
# package.json in the standalone frontend image.
COPY package.json ./
RUN npm install

COPY . .

# Vite reads VITE_* from the environment at build time. Surfacing them
# as build ARGs keeps the values out of the image tag and lets
# docker-compose forward them from the project's .env file.
#
# Auth selection (mock default; magic for production):
#   VITE_AUTH_PROVIDER=mock  -> default; dev/tests.
#   VITE_AUTH_PROVIDER=magic -> requires VITE_MAGIC_PUBLISHABLE_KEY.
ARG VITE_AUTH_PROVIDER=mock
ARG VITE_MAGIC_PUBLISHABLE_KEY=
ENV VITE_AUTH_PROVIDER=$VITE_AUTH_PROVIDER
ENV VITE_MAGIC_PUBLISHABLE_KEY=$VITE_MAGIC_PUBLISHABLE_KEY

RUN npm run build

# ---------- Stage 2: runtime ----------
FROM nginx:1.27-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -q -O - http://127.0.0.1/ >/dev/null 2>&1 || exit 1
