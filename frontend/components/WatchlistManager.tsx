"use client";
import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import type { WatchlistItem } from "../lib/types";
import { pct, rs } from "../lib/format";
import { Badge, ErrorState } from "./ui";

export function WatchlistManager({ symbols }: { symbols: string[] }) {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [pick, setPick] = useState(symbols[0] ?? "");

  const load = () => {
    api
      .watchlist()
      .then((b: unknown) => setItems((b as { items: WatchlistItem[] }).items))
      .catch((e: unknown) => setError(e instanceof ApiError ? e.message : "Failed to load watchlist."));
  };
  useEffect(load, []);

  const add = async () => {
    if (!pick) return;
    try {
      await api.watchAdd(pick);
      setError(null);
      load();
    } catch (e: unknown) {
      setError(e instanceof ApiError ? e.message : "Failed to add symbol.");
    }
  };
  const remove = async (s: string) => {
    await api.watchRemove(s);
    load();
  };

  if (error && items.length === 0) return <ErrorState message={error} onRetry={load} />;
  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <select
          value={pick}
          onChange={(e) => setPick(e.target.value)}
          className="rounded-lg border border-line bg-surface px-2.5 py-2 text-[13px] text-body"
        >
          {symbols.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <button
          onClick={add}
          className="rounded-lg border border-line bg-surface px-3 py-2 text-[13px] text-body transition-colors hover:border-accent"
        >
          Add to watchlist
        </button>
      </div>
      {items.length === 0 ? (
        <p className="rounded-xl border border-line bg-card p-6 text-sm text-muted">
          Watchlist is empty. Add a symbol to track its price, direction and confidence.
        </p>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-line bg-card">
          <table className="w-full min-w-[560px] border-collapse text-[13px]">
            <thead>
              <tr className="bg-surface text-left text-xs text-muted">
                <th className="px-3.5 py-2.5 font-semibold">Symbol</th>
                <th className="px-3.5 py-2.5 text-right font-semibold">Price</th>
                <th className="px-3.5 py-2.5 text-right font-semibold">Change</th>
                <th className="px-3.5 py-2.5 font-semibold">Direction</th>
                <th className="px-3.5 py-2.5 text-right font-semibold">Confidence</th>
                <th className="px-3.5 py-2.5 font-semibold"> </th>
              </tr>
            </thead>
            <tbody>
              {items.map((i) => (
                <tr key={i.symbol} className="border-t border-line tabular-nums">
                  <td className="px-3.5 py-2.5 font-bold text-body">{i.symbol}</td>
                  <td className="px-3.5 py-2.5 text-right text-body">{rs(i.current_price)}</td>
                  <td className={`px-3.5 py-2.5 text-right ${(i.change_pct ?? 0) >= 0 ? "text-up" : "text-down"}`}>
                    {i.change_pct === null ? "N/A" : pct(i.change_pct)}
                  </td>
                  <td className="px-3.5 py-2.5">{i.prediction ? <Badge value={i.prediction} /> : "N/A"}</td>
                  <td className="px-3.5 py-2.5 text-right text-muted">
                    {i.confidence === null ? "N/A" : `${(i.confidence * 100).toFixed(1)}%`}
                  </td>
                  <td className="px-3.5 py-2.5">
                    <button onClick={() => remove(i.symbol)} className="text-muted hover:text-down">
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
