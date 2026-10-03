"use client";
import { useState } from "react";

export function Header({ onMenu }: { onMenu: () => void }) {
  const [open, setOpen] = useState(false);
  return (
    <header className="flex items-center gap-3 py-3">
      <button
        onClick={onMenu}
        aria-label="Menu"
        className="rounded-lg border border-line bg-card px-2.5 py-1.5 text-body lg:hidden"
      >
        ☰
      </button>
      <div>
        <h1 className="text-2xl font-semibold text-body">Dashboard</h1>
        <p className="text-[13px] text-muted">Market prediction overview</p>
      </div>
      <div className="flex-1" />
      <div className="relative">
        <button
          onClick={() => setOpen((v) => !v)}
          aria-label="Notifications"
          className="relative rounded-lg border border-line bg-card px-2.5 py-1.5 text-body transition-colors hover:border-accent"
        >
          🔔<span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-accent" />
        </button>
        {open ? (
          <div className="absolute right-0 top-11 z-50 w-72 rounded-xl border border-line bg-surface p-3 text-xs text-muted">
            <p className="font-semibold text-body">Notifications</p>
            <ul className="mt-1 list-disc space-y-1 pl-4">
              <li>Backtest accuracy near 50% is expected for next-day direction.</li>
              <li>Simulation feed refreshes every 60 seconds.</li>
            </ul>
          </div>
        ) : null}
      </div>
      <div className="flex items-center gap-2 rounded-lg border border-line bg-card py-1 pl-1 pr-3">
        <div className="flex h-7 w-7 items-center justify-center rounded-full border border-line bg-surface text-xs font-bold text-body">
          P
        </div>
        <div className="hidden sm:block">
          <p className="text-[13px] leading-tight text-body">Prayush</p>
          <p className="text-[11px] leading-tight text-muted">Analyst workspace</p>
        </div>
      </div>
    </header>
  );
}
