"use client";
import { useRouter, useSearchParams } from "next/navigation";

export function SymbolSelect({ symbols, value }: { symbols: string[]; value: string }) {
  const router = useRouter();
  const params = useSearchParams();
  return (
    <select
      value={value}
      onChange={(e) => {
        const q = new URLSearchParams(params.toString());
        q.set("symbol", e.target.value);
        router.push(`?${q.toString()}`);
      }}
      className="rounded-lg border border-line bg-surface px-2.5 py-2 text-[13px] text-body"
      aria-label="Select symbol"
    >
      {symbols.map((s) => (
        <option key={s} value={s}>
          {s}
        </option>
      ))}
    </select>
  );
}
