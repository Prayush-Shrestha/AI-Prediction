"use client";
import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import type { HistoryRecord } from "../lib/types";
import { Badge, ErrorState } from "./ui";

export function HistoryTable({ symbol }: { symbol?: string }) {
  const [rows, setRows] = useState<HistoryRecord[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    api
      .history(symbol)
      .then((b: unknown) => setRows((b as { records: HistoryRecord[] }).records))
      .catch((e: unknown) => setError(e instanceof ApiError ? e.message : "Failed to load history."));
  };
  useEffect(load, [symbol]);

  const reconcile = async () => {
    await api.reconcile();
    load();
  };

  if (error) return <ErrorState message={error} onRetry={load} />;
  return (
    <div>
      <div className="mb-3">
        <button
          onClick={reconcile}
          className="rounded-lg border border-line bg-surface px-3 py-2 text-[13px] text-body transition-colors hover:border-accent"
        >
          Score pending predictions
        </button>
      </div>
      {rows.length === 0 ? (
        <p className="rounded-xl border border-line bg-card p-6 text-sm text-muted">
          No predictions recorded yet. Open a prediction to record it.
        </p>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-line bg-card">
          <table className="w-full min-w-[680px] border-collapse text-[13px]">
            <thead>
              <tr className="bg-surface text-left text-xs text-muted">
                <th className="px-3.5 py-2.5 font-semibold">Date</th>
                <th className="px-3.5 py-2.5 font-semibold">Symbol</th>
                <th className="px-3.5 py-2.5 font-semibold">Prediction</th>
                <th className="px-3.5 py-2.5 text-right font-semibold">Confidence</th>
                <th className="px-3.5 py-2.5 font-semibold">Model</th>
                <th className="px-3.5 py-2.5 font-semibold">Actual</th>
                <th className="px-3.5 py-2.5 font-semibold">Result</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="border-t border-line tabular-nums">
                  <td className="px-3.5 py-2.5 text-muted">{r.as_of}</td>
                  <td className="px-3.5 py-2.5 font-bold text-body">{r.symbol}</td>
                  <td className="px-3.5 py-2.5">
                    <Badge value={r.action} />
                  </td>
                  <td className="px-3.5 py-2.5 text-right text-muted">{(r.confidence * 100).toFixed(1)}%</td>
                  <td className="px-3.5 py-2.5 text-muted">{r.model}</td>
                  <td className="px-3.5 py-2.5 text-muted">{r.actual ?? "pending"}</td>
                  <td className="px-3.5 py-2.5">
                    {r.correct === null ? (
                      <span className="text-muted">—</span>
                    ) : r.correct ? (
                      <span className="font-semibold text-up">Correct</span>
                    ) : (
                      <span className="font-semibold text-down">Incorrect</span>
                    )}
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
