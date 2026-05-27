/**
 * Authenticated API client (ADR 0024 — Bearer model).
 *
 * Sprint 28-B.2: native fetch replacement for axios. Maintains the same
 * API surface so consuming files require zero changes.
 *
 * Post-AuthProvider cutover (2026-05-17) this module hosts:
 *   - The shared `apiClient` instance every authenticated call goes
 *     through (B2 single credential pipeline).
 *   - Mock-mode token write/clear helpers (re-exported by `./auth`).
 *
 * The Clerk-mode Bearer is attached by AuthProvider's single
 * interceptor inside the React tree, NOT by this module.
 */

import { API_BASE_URL } from "../lib/env";

// Sprint 28: env variables now centralized in lib/env.ts.

export const MOCK_TOKEN_KEY = "noni.mock_token";
export { API_BASE_URL };

function _generateRequestId(): string {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
}

// ---------------------------------------------------------------------------
// Lightweight fetch wrapper that mimics the axios response shape.
// ---------------------------------------------------------------------------

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

interface RequestConfig {
  headers?: Record<string, string>;
  validateStatus?: (status: number) => boolean;
  retry?: boolean;
  timeout?: number;
}

interface ApiResponse<T = unknown> {
  data: T;
  status: number;
  statusText: string;
  headers: Headers;
}

type InterceptorHandler = (config: RequestConfig) => RequestConfig | Promise<RequestConfig>;

const API_V1_PREFIX = "/api/v1";
const RETRYABLE_STATUSES = new Set([408, 429, 500, 502, 503, 504]);
const GET_RETRY_DELAYS_MS = [250, 750];

function _normalizePath(url: string): string {
  if (url.startsWith("http") || url.startsWith(API_V1_PREFIX)) {
    return url;
  }
  if (url.startsWith("/api/")) {
    return `${API_V1_PREFIX}${url.slice(4)}`;
  }
  if (url.startsWith("/auth/")) {
    return `${API_V1_PREFIX}${url}`;
  }
  if (url === "/auth") {
    return `${API_V1_PREFIX}/auth`;
  }
  if (url.startsWith("/me/")) {
    return `${API_V1_PREFIX}${url}`;
  }
  if (url === "/me") {
    return `${API_V1_PREFIX}/me`;
  }
  return url;
}

function _sleep(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

class FetchClient {
  private _baseURL: string;
  private _requestInterceptors: InterceptorHandler[] = [];
  private _defaultTimeout: number;

  constructor(baseURL: string, defaultTimeout: number = 15000) {
    this._baseURL = baseURL;
    this._defaultTimeout = defaultTimeout;
  }

  get interceptors() {
    return {
      request: {
        use: (handler: InterceptorHandler) => {
          this._requestInterceptors.push(handler);
          return this._requestInterceptors.length - 1;
        },
        eject: (id: number) => {
          this._requestInterceptors.splice(id, 1);
        },
      },
    };
  }

  private async _request<T>(
    method: HttpMethod,
    url: string,
    data?: unknown,
    config: RequestConfig = {},
  ): Promise<ApiResponse<T>> {
    let merged = { ...config };
    for (const handler of this._requestInterceptors) {
      merged = await handler(merged);
    }

    const normalizedUrl = _normalizePath(url);
    const fullURL = normalizedUrl.startsWith("http")
      ? normalizedUrl
      : `${this._baseURL}${normalizedUrl}`;

    const controller = new AbortController();
    const timeoutMs = merged.timeout ?? this._defaultTimeout;
    const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

    const init: RequestInit = {
      method,
      headers: {
        "Content-Type": "application/json",
        "X-Request-ID": _generateRequestId(),
        ...merged.headers,
      },
      signal: controller.signal,
    };
    if (data !== undefined) {
      init.body = JSON.stringify(data);
    }

    let response: Response;
    try {
      response = await fetch(fullURL, init);
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") {
        const timeoutErr = new Error(`Request timeout after ${timeoutMs}ms`);
        (timeoutErr as unknown as { response?: ApiResponse<unknown> }).response = {
          data: null,
          status: 0,
          statusText: "timeout",
          headers: new Headers(),
        };
        throw timeoutErr;
      }
      throw err;
    } finally {
      window.clearTimeout(timeoutId);
    }
    const isOk = merged.validateStatus ? merged.validateStatus(response.status) : response.ok;

    let parsed: unknown;
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      parsed = await response.json();
    } else {
      parsed = await response.text();
    }

    if (!isOk) {
      const err = new Error(`Request failed with status ${response.status}`);
      (err as unknown as { response?: ApiResponse<unknown> }).response = {
        data: parsed,
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
      };
      throw err;
    }

    return {
      data: parsed as T,
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    };
  }

  get<T = unknown>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this._requestWithRetry<T>("GET", url, undefined, config);
  }

  post<T = unknown>(url: string, data?: unknown, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this._request<T>("POST", url, data, config);
  }

  put<T = unknown>(url: string, data?: unknown, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this._request<T>("PUT", url, data, config);
  }

  patch<T = unknown>(url: string, data?: unknown, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this._request<T>("PATCH", url, data, config);
  }

  delete<T = unknown>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this._request<T>("DELETE", url, undefined, config);
  }

  private async _requestWithRetry<T>(
    method: HttpMethod,
    url: string,
    data?: unknown,
    config: RequestConfig = {},
  ): Promise<ApiResponse<T>> {
    const shouldRetry = method === "GET" && config.retry !== false;
    if (!shouldRetry) {
      return this._request<T>(method, url, data, config);
    }

    let lastError: unknown;
    for (let attempt = 0; attempt <= GET_RETRY_DELAYS_MS.length; attempt += 1) {
      try {
        return await this._request<T>(method, url, data, config);
      } catch (err) {
        lastError = err;
        const status = (err as { response?: ApiResponse<unknown> }).response?.status;
        if (!status || !RETRYABLE_STATUSES.has(status) || attempt >= GET_RETRY_DELAYS_MS.length) {
          throw err;
        }
        await _sleep(GET_RETRY_DELAYS_MS[attempt]);
      }
    }
    throw lastError;
  }
}

export const apiClient = new FetchClient(API_BASE_URL);

/** Mock-mode helpers. */
export function setMockToken(email: string): void {
  localStorage.setItem(MOCK_TOKEN_KEY, `mock:${email}`);
}

export function clearMockToken(): void {
  localStorage.removeItem(MOCK_TOKEN_KEY);
}
