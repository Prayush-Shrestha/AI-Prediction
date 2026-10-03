"use client";
import { useEffect, useRef, useState } from "react";

export default function StockCard({ stock }) {
  const { symbol, price, change_pct, direction, confidence } = stock;
  const prevPrice = useRef(price);
  const [flash, setFlash] = useState(null);

  useEffect(() => {
    if (prevPrice.current !== price) {
      setFlash(price > prevPrice.current ? "flash-up" : "flash-down");
      prevPrice.current = price;
      const t = setTimeout(() => setFlash(null), 1100);
      return () => clearTimeout(t);
    }
  }, [price]);

  const isUp = direction === "UP";
  const tickUp = change_pct >= 0;

  return (
    <div
      className={`rounded-2xl border border-black/5 bg-white shadow-soft p-4 transition-colors ${flash || ""}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="font-semibold tracking-tight">{symbol}</div>
          <div className="text-2xl font-serif tabular mt-1">Rs {price.toFixed(2)}</div>
        </div>
        <span
          className={`text-xs font-medium px-2 py-1 rounded-full tabular ${
            tickUp ? "bg-rise/10 text-rise" : "bg-fall/10 text-fall"
          }`}
        >
          {tickUp ? "▲" : "▼"} {Math.abs(change_pct).toFixed(2)}%
        </span>
      </div>

      <div className="mt-4 pt-3 border-t border-black/5 flex items-center justify-between">
        <div className="text-xs text-ink/50">Predicted next session</div>
        <div
          className={`flex items-center gap-1.5 text-sm font-semibold ${
            isUp ? "text-rise" : "text-fall"
          }`}
        >
          {isUp ? "▲ UP" : "▼ DOWN"}
          <span className="text-ink/40 font-normal">· {confidence.toFixed(0)}%</span>
        </div>
      </div>
    </div>
  );
}
