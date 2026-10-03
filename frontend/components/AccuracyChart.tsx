"use client";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function AccuracyChart({ rows }: { rows: Record<string, number | string>[] }) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={rows} margin={{ left: 0, right: 8, top: 8 }}>
        <CartesianGrid stroke="#243044" strokeDasharray="3 3" />
        <XAxis dataKey="symbol" tick={{ fill: "#94A3B8", fontSize: 11 }} />
        <YAxis tick={{ fill: "#94A3B8", fontSize: 11 }} domain={[0, 1]} tickFormatter={(v: number) => `${Math.round(v * 100)}%`} />
        <Tooltip
          contentStyle={{ background: "#172033", border: "1px solid #243044", borderRadius: 8, color: "#F8FAFC" }}
        />
        <Legend />
        <Bar dataKey="random_forest" name="Random Forest" fill="#3B82F6" />
        <Bar dataKey="logistic_regression" name="Log. Regression" fill="#94A3B8" />
        <Bar dataKey="gradient_boosting" name="Grad. Boosting" fill="#22C55E" />
      </BarChart>
    </ResponsiveContainer>
  );
}
