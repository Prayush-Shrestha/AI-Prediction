"use client";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PricePoint } from "../lib/types";

function sma(values: number[], n: number): (number | null)[] {
  return values.map((_, i) => {
    if (i + 1 < n) return null;
    return values.slice(i + 1 - n, i + 1).reduce((a, b) => a + b, 0) / n;
  });
}

export function PriceChart({ history, height = 320 }: { history: PricePoint[]; height?: number }) {
  const closes = history.map((h) => h.close);
  const data = history.map((h, i) => ({
    date: h.date.slice(5),
    close: h.close,
    sma20: sma(closes, 20)[i],
  }));
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ left: 8, right: 8, top: 8, bottom: 0 }}>
        <CartesianGrid stroke="#243044" strokeDasharray="3 3" />
        <XAxis dataKey="date" tick={{ fill: "#94A3B8", fontSize: 11 }} minTickGap={28} />
        <YAxis
          tick={{ fill: "#94A3B8", fontSize: 11 }}
          domain={["auto", "auto"]}
          tickFormatter={(v: number) => `${v}`}
        />
        <Tooltip
          contentStyle={{ background: "#172033", border: "1px solid #243044", borderRadius: 8, color: "#F8FAFC" }}
        />
        <Legend />
        <Line type="monotone" dataKey="close" name="Close (Rs)" stroke="#3B82F6" strokeWidth={2} dot={false} />
        <Line
          type="monotone"
          dataKey="sma20"
          name="SMA-20"
          stroke="#94A3B8"
          strokeWidth={1}
          strokeDasharray="5 4"
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
