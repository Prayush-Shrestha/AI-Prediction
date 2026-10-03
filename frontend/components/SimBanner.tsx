"use client";
import { useCallback, useEffect, useState } from "react";
import { api } from "../lib/api";
import type { SimQuote } from "../lib/types";
import { useCountdown } from "../hooks/useCountdown";

export function SimBanner() {
  const [quotes, setQuotes] = useState<SimQuote[]>([]);
  const [error, setError] = useState(false);
  const load = useCallback(() => {
    api
      .tick()
      .then((b: unknown) => {
        const body = b as { quotes: SimQuote[] };
        setQuotes(body.quotes);
        setError(false);
      })
      .catch(() => setError(true));
  }, []);
  useEffect(() => {
    load();
  }, [load]);
  const left = useCountdown(60, load);
  const up = quotes.filter((q) => q.prediction === "UP").length;
  return (
    <div className="rounded-xl border border-line bg-card px-4 py-2.5 text-[13px]">
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
        <span className="font-semibold text-body">
          <span className="mr-1.5 inline-block h-2 w-2 rounded-full bg-accent" />
          Demo Simulation
        </span>
        <span className="text-muted">not a real-time NEPSE feed · next update in {left}s</span>
        {!error && quotes.length > 0 ? (
          <span className="text-muted">
            {up} up / {quotes.length - up} down-or-hold across {quotes.length} symbols
          </span>
        ) : null}
        {error ? <span className="text-down">simulation unavailable</span> : null}
      </div>
    </div>
  );
}
