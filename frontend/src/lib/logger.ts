/**
 * Sprint 28-B.7: structured frontend logger with levels.
 *
 * Replaces ad-hoc console.* calls. Respects VITE_LOG_LEVEL to gate
 * verbosity (default: warn in production, debug in development).
 *
 * Levels: debug < info < warn < error. Each output goes to the
 * matching console method so browser devtools filtering still works.
 *
 * NEVER log tokens, headers, raw JWTs, or PII (B10 guardrail).
 */

type Level = "debug" | "info" | "warn" | "error";

const ORDER: Record<Level, number> = {
  debug: 10,
  info: 20,
  warn: 30,
  error: 40,
};

interface ImportMetaEnvShape {
  VITE_LOG_LEVEL?: string;
  MODE?: string;
}

const _env: ImportMetaEnvShape =
  (import.meta as unknown as { env?: ImportMetaEnvShape }).env ?? {};

function _resolveMinLevel(): number {
  const raw = (_env.VITE_LOG_LEVEL ?? "").toLowerCase();
  if (raw in ORDER) return ORDER[raw as Level];
  // Default: noisier in dev, quieter in prod.
  return _env.MODE === "production" ? ORDER.warn : ORDER.debug;
}

const MIN_LEVEL = _resolveMinLevel();

function _emit(level: Level, msg: string, ctx?: unknown): void {
  if (ORDER[level] < MIN_LEVEL) return;
  const payload = ctx === undefined ? msg : { msg, ctx };
  // Map to the matching console method.
  switch (level) {
    case "debug":
      // eslint-disable-next-line no-console
      console.debug(payload);
      break;
    case "info":
      // eslint-disable-next-line no-console
      console.info(payload);
      break;
    case "warn":
      // eslint-disable-next-line no-console
      console.warn(payload);
      break;
    case "error":
      // eslint-disable-next-line no-console
      console.error(payload);
      break;
  }
}

export const logger = {
  debug: (msg: string, ctx?: unknown) => _emit("debug", msg, ctx),
  info: (msg: string, ctx?: unknown) => _emit("info", msg, ctx),
  warn: (msg: string, ctx?: unknown) => _emit("warn", msg, ctx),
  error: (msg: string, ctx?: unknown) => _emit("error", msg, ctx),
};
