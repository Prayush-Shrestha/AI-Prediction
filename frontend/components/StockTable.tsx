"use client";
import Link from "next/link";
import type { StockQuote } from "../lib/types";
import { pct, rs } from "../lib/format";
import { Badge } from "./ui";

export interface StockRow extends StockQuote {
  prediction: "UP" | "DOWN";
  action: "UP" | "DOWN" | "HOLD";
  confidence: number;
  p_up: number;
}

export function StockTable({ stocks, selected }: { stocks: StockRow[]; selected?: string }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-line bg-card">
      <table className="w-full min-w-[640px] border-collapse text-[13px]">
        <thead>
          <tr className="bg-surface text-left text-xs text-muted">
            <th className="px-3.5 py-2.5 font-semibold">Symbol</th>
            <th className="px-3.5 py-2.5 font-semibold">Sector</th>
            <th className="px-3.5 py-2.5 text-right font-semibold">Price</th>
            <th className="px-3.5 py-2.5 text-right font-semibold">Change</th>
            <th className="px-3.5 py-2.5 font-semibold">Prediction</th>
            <th className="px-3.5 py-2.5 text-right font-semibold">Confidence</th>
            <th className="px-3.5 py-2.5 text-right font-semibold">Updated</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((s) => (
            <tr
              key={s.symbol}
              className={`border-t border-line tabular-nums hover:bg-accent/5 ${
                s.symbol === selected ? "bg-accent/5" : ""
              }`}
            >
              <td className="px-3.5 py-2.5 font-bold">
                <Link href={`/predictions?symbol=${s.symbol}`} className="text-body hover:text-accent">
                  {s.symbol}
                </Link>
              </td>
              <td className="px-3.5 py-2.5 text-muted">{s.sector}</td>
              <td className="px-3.5 py-2.5 text-right text-body">{rs(s.current_price)}</td>
              <td className={`px-3.5 py-2.5 text-right ${s.change_pct >= 0 ? "text-up" : "text-down"}`}>
                {pct(s.change_pct)}
              </td>
              <td className="px-3.5 py-2.5">
                {s.action ? <Badge value={s.action === "HOLD" ? "HOLD" : s.prediction} /> : "N/A"}
              </td>
              <td className="px-3.5 py-2.5 text-right text-muted">{typeof s.confidence === "number" ? `${(s.confidence * 100).toFixed(1)}%` : "N/A"}</td>
              <td className="px-3.5 py-2.5 text-right text-muted">{s.date}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
