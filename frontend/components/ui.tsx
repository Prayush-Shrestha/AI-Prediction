import type { ReactNode } from "react";

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`rounded-xl border border-line bg-card p-4 shadow-sm ${className}`}>{children}</div>
  );
}

export function SectionHead({ title, sub }: { title: string; sub?: string }) {
  return (
    <div className="mb-2 flex items-baseline gap-2">
      <h2 className="text-base font-semibold text-body">{title}</h2>
      {sub ? <p className="text-xs text-muted">{sub}</p> : null}
    </div>
  );
}

export function Badge({ value }: { value: string }) {
  const cls =
    value === "UP" || value === "BULLISH"
      ? "border-up/40 bg-up/10 text-up"
      : value === "DOWN" || value === "BEARISH"
        ? "border-down/40 bg-down/10 text-down"
        : "border-line bg-surface text-muted";
  return (
    <span className={`inline-block rounded-md border px-2 py-0.5 text-xs font-bold tracking-wide ${cls}`}>
      {value}
    </span>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="rounded-xl border border-line bg-card p-6 text-sm text-muted">
      <p>{message}</p>
      {onRetry ? (
        <button
          onClick={onRetry}
          className="mt-3 rounded-lg border border-line bg-surface px-3 py-1.5 text-body transition-colors hover:border-accent"
        >
          Retry
        </button>
      ) : null}
    </div>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-xl border border-line bg-card ${className}`} />;
}
