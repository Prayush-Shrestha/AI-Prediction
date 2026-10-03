"use client";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ImportanceEntry } from "../lib/types";

export function ImportanceChart({ data, height = 300 }: { data: ImportanceEntry[]; height?: number }) {
  const rows = [...data].sort((a, b) => a.importance - b.importance).slice(-12);
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={rows} layout="vertical" margin={{ left: 24, right: 12 }}>
        <CartesianGrid stroke="#243044" strokeDasharray="3 3" />
        <XAxis type="number" tick={{ fill: "#94A3B8", fontSize: 11 }} />
        <YAxis type="category" dataKey="feature" tick={{ fill: "#94A3B8", fontSize: 11 }} width={110} />
        <Tooltip
          contentStyle={{ background: "#172033", border: "1px solid #243044", borderRadius: 8, color: "#F8FAFC" }}
        />
        <Legend />
        <Bar dataKey="importance" name="Importance" fill="#3B82F6" />
      </BarChart>
    </ResponsiveContainer>
  );
}
