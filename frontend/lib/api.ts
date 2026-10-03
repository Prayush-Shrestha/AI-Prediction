const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function get<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, { cache: "no-store", ...init });
  } catch {
    throw new ApiError(0, "Unable to load market data. Please check the backend connection.");
  }
  if (!res.ok) {
    if (res.status === 404) throw new ApiError(404, "Symbol not found.");
    if (res.status === 422) throw new ApiError(422, "Model unavailable for this symbol.");
    throw new ApiError(res.status, `Request failed (${res.status}).`);
  }
  return (await res.json()) as T;
}

async function send<T>(path: string, method: string, body?: unknown): Promise<T> {
  return get<T>(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

export const api = {
  health: () => get("/api/health"),
  stocks: () => get<{ stocks: unknown[]; count: number }>("/api/stocks"),
  stock: (s: string) => get(`/api/stocks/${s}`),
  prediction: (s: string, model?: string) =>
    get(`/api/predictions/${s}${model ? `?model=${model}` : ""}`),
  models: (s: string) => get(`/api/models/${s}`),
  analyticsOverview: () => get("/api/analytics/overview"),
  analyticsSymbol: (s: string) => get(`/api/analytics/${s}`),
  history: (symbol?: string) => get(`/api/history${symbol ? `?symbol=${symbol}` : ""}`),
  reconcile: () => send<{ scored: number; pending: number }>("/api/history/reconcile", "POST"),
  watchlist: () => get("/api/watchlist"),
  watchAdd: (symbol: string, note = "") =>
    send("/api/watchlist", "POST", { symbol, note }),
  watchRemove: (symbol: string) => send(`/api/watchlist/${symbol}`, "DELETE"),
  tick: () => get("/api/simulation/tick"),
};
