"use client";
import { useEffect, useState, useCallback } from "react";
import StockCard from "../components/StockCard";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const POLL_MS = 60_000; // update once every minute

export default function DashboardPage() {
  const [stocks, setStocks] = useState([]);
  const [updatedAt, setUpdatedAt] = useState(null);
  const [secondsLeft, setSecondsLeft] = useState(POLL_MS / 1000);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStocks = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/stocks`, { cache: "no-store" });
      if (!res.ok) throw new Error(`Backend returned ${res.status}`);
      const data = await res.json();
      setStocks(data.stocks.sort((a, b) => a.symbol.localeCompare(b.symbol)));
      setUpdatedAt(data.updated_at);
      setError(null);
    } catch (e) {
      setError(
        "Can't reach the backend. Is it running? (uvicorn main:app --port 8000)"
      );
    } finally {
      setLoading(false);
      setSecondsLeft(POLL_MS / 1000);
    }
  }, []);

  useEffect(() => {
    fetchStocks();
    const poll = setInterval(fetchStocks, POLL_MS);
    const countdown = setInterval(
      () => setSecondsLeft((s) => (s > 0 ? s - 1 : 0)),
      1000
    );
    return () => {
      clearInterval(poll);
      clearInterval(countdown);
    };
  }, [fetchStocks]);

  const upCount = stocks.filter((s) => s.direction === "UP").length;
  const downCount = stocks.length - upCount;

  return (
    <div>
      <div className="flex flex-wrap items-end justify-between gap-3 mb-6">
        <div>
          <h1 className="text-2xl font-serif">Today&apos;s NEPSE Outlook</h1>
          <p className="text-sm text-ink/50 mt-1">
            {updatedAt
              ? `Last tick: ${new Date(updatedAt).toLocaleTimeString()}`
              : "Loading first tick…"}
            {" · "}next update in {secondsLeft}s
          </p>
        </div>
        <div className="flex gap-2 text-sm">
          <span className="px-3 py-1.5 rounded-full bg-rise/10 text-rise font-medium">
            {upCount} predicted up
          </span>
          <span className="px-3 py-1.5 rounded-full bg-fall/10 text-fall font-medium">
            {downCount} predicted down
          </span>
        </div>
      </div>

      {error && (
        <div className="mb-6 rounded-xl border border-fall/20 bg-fall/5 text-fall text-sm px-4 py-3">
          {error}
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-28 rounded-2xl bg-black/5 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {stocks.map((s) => (
            <StockCard key={s.symbol} stock={s} />
          ))}
        </div>
      )}
    </div>
  );
}
