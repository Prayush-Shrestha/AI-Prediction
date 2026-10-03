"use client";
import { useState, type ReactNode } from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

export function Shell({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="min-h-screen bg-ink text-body">
      <div
        className={`fixed inset-y-0 left-0 z-40 transition-transform lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <Sidebar onNavigate={() => setOpen(false)} />
      </div>
      {open ? (
        <div className="fixed inset-0 z-30 bg-black/50 lg:hidden" onClick={() => setOpen(false)} />
      ) : null}
      <div className="lg:ml-60">
        <div className="mx-auto max-w-6xl px-4 pb-12 lg:px-6">
          <Header onMenu={() => setOpen((v) => !v)} />
          {children}
          <footer className="mt-8 border-t border-line pt-4 text-xs text-muted">
            NEPSE Direction Tracker · demo methodology — direction prediction is noisy; treat output
            as probability, never as financial advice.
          </footer>
        </div>
      </div>
    </div>
  );
}
