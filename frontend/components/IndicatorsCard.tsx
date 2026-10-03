import type { Indicators } from "../lib/types";
import { num } from "../lib/format";
import { Card, SectionHead } from "./ui";

const ROWS: { key: keyof Indicators; label: string; money?: boolean }[] = [
  { key: "rsi_14", label: "RSI (14)" },
  { key: "sma_20", label: "SMA 20", money: true },
  { key: "sma_10", label: "SMA 10", money: true },
  { key: "ema_12", label: "EMA 12", money: true },
  { key: "ema_26", label: "EMA 26", money: true },
  { key: "macd_hist", label: "MACD histogram" },
  { key: "macd_signal", label: "MACD signal" },
  { key: "bb_upper", label: "Bollinger upper", money: true },
  { key: "bb_lower", label: "Bollinger lower", money: true },
  { key: "volatility_10", label: "Volatility (10d)" },
  { key: "Volume", label: "Volume" },
];

export function IndicatorsCard({ indicators }: { indicators: Indicators }) {
  return (
    <Card>
      <SectionHead title="Technical Indicators" sub="latest session, from backend" />
      <div>
        {ROWS.map((r) => {
          const v = indicators[r.key];
          return (
            <div key={r.key} className="flex items-baseline justify-between border-b border-line py-2 text-[13px] last:border-0">
              <span className="text-muted">{r.label}</span>
              <b className="tabular-nums text-body">
                {r.key === "Volume" ? (v === null ? "N/A" : Math.round(v).toLocaleString()) : r.money && v !== null ? `Rs ${num(v)}` : num(v)}
              </b>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
