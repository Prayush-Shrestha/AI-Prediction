export function pct(x: number | null | undefined, digits = 2): string {
  if (x === null || x === undefined || Number.isNaN(x)) return "N/A";
  return `${x >= 0 ? "+" : ""}${x.toFixed(digits)}%`;
}

export function num(x: number | null | undefined, digits = 2): string {
  if (x === null || x === undefined || Number.isNaN(x)) return "N/A";
  return x.toFixed(digits);
}

export function rs(x: number | null | undefined): string {
  if (x === null || x === undefined || Number.isNaN(x)) return "N/A";
  return `Rs ${x.toLocaleString("en-NP", { maximumFractionDigits: 2, minimumFractionDigits: 2 })}`;
}

export function timeAgo(iso: string): string {
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60) return `${Math.floor(s)}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  return `${Math.floor(s / 3600)}h ago`;
}
