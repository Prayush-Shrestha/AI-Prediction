"use client";
import { useEffect, useState, useCallback } from "react";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  LineChart, Line, Legend,
} from "recharts";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [symbol, setSymbol] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/api/analytics`, { cache: "no-store" })
      .then((r) => r.json())
      .then((data) => {
        setAnalytics(data);
        if (data.symbols?.length) setSymbol(data.symbols[0].symbol);
      })
      .catch(() => setError("Can't reach the backend."));
  }, []);

  const loadHistory = useCallback((sym) => {
    fetch(`${API_URL}/api/history/${sym}?n=40`, { cache: "no-store" })
      .then((r) => r.json())
      .then((data) =>
        setHistory(
          data.series.map((p) => ({
            date: new Date(p.date).toLocaleDateString(undefined, { month: "short", day: "numeric" }),
            close: p.close,
          }))
        )
      )
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (symbol) loadHistory(symbol);
  }, [symbol, loadHistory]);

  if (error) {
    return <div className="text-fall text-sm">{error}</div>;
  }
  if (!analytics) {
    return <div className="h-64 rounded-2xl bg-black/5 animate-pulse" />;
  }

  const barData = analytics.symbols.map((s) => ({
    symbol: s.symbol,
    accuracy: s.backtest_accuracy ?? 0,
  }));

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-2xl font-serif">Model Analytics</h1>
        <p className="text-sm text-ink/50 mt-1">
          Backtest accuracy is measured on a held-out, time-ordered slice of
          each symbol&apos;s history — never seen during training. Average across
          all symbols: <span className="font-medium text-ink">{analytics.average_backtest_accuracy}%</span>.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-black/5 shadow-soft p-5">
        <h2 className="font-medium mb-4">Backtest accuracy by symbol</h2>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={barData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
            <XAxis dataKey="symbol" tick={{ fontSize: 12 }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} unit="%" />
            <Tooltip formatter={(v) => `${v}%`} />
            <Bar dataKey="accuracy" fill="#0F3D68" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
        <p className="text-xs text-ink/40 mt-3">
          A dashed reference at 50% would represent a coin-flip baseline —
          most bars sitting close to it is the expected, honest result for
          short-term direction prediction.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-black/5 shadow-soft p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-medium">Recent price history</h2>
          <select
            value={symbol || ""}
            onChange={(e) => setSymbol(e.target.value)}
            className="text-sm border border-black/10 rounded-lg px-3 py-1.5 bg-paper"
          >
            {analytics.symbols.map((s) => (
              <option key={s.symbol} value={s.symbol}>{s.symbol}</option>
            ))}
          </select>
        </div>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} />
            <YAxis domain={["auto", "auto"]} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="close" stroke="#B03052" strokeWidth={2} dot={false} name="Close (Rs)" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-2xl border border-black/5 shadow-soft p-5">
        <h2 className="font-medium mb-4">What drives each model most</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {analytics.symbols.map((s) => (
            <div key={s.symbol} className="border border-black/5 rounded-xl p-3">
              <div className="text-sm font-medium">{s.symbol}</div>
              <div className="text-xs text-ink/50 mt-1">
                top feature: <span className="text-ink/80">{s.top_feature}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
