"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/", label: "Dashboard" },
  { href: "/predictions", label: "Predictions" },
  { href: "/market", label: "Market Data" },
  { href: "/watchlist", label: "Watchlist" },
  { href: "/analytics", label: "Analytics" },
  { href: "/history", label: "Prediction History" },
  { href: "/models", label: "Model Performance" },
];

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const path = usePathname();
  return (
    <aside className="flex h-full w-60 flex-col border-r border-line bg-card px-3 py-5">
      <div className="border-b border-line px-2 pb-4">
        <p className="text-sm font-bold tracking-[0.15em] text-body">NEPSE</p>
        <p className="text-xs tracking-[0.15em] text-muted">DIRECTION TRACKER</p>
      </div>
      <nav className="mt-3 flex flex-col gap-0.5">
        {NAV.map((n) => (
          <Link
            key={n.href}
            href={n.href}
            onClick={onNavigate}
            className={`rounded-lg border border-transparent px-2.5 py-2 text-[13px] transition-colors ${
              path === n.href
                ? "border-accent/30 bg-accent/10 text-body"
                : "text-muted hover:bg-surface hover:text-body"
            }`}
          >
            {n.label}
          </Link>
        ))}
        <div className="mx-1 my-2 border-t border-line" />
        <span className="cursor-default px-2.5 py-2 text-[13px] text-muted/50">Settings</span>
      </nav>
      <div className="mt-auto border-t border-line px-2 pt-3 text-xs text-muted">
        <p>
          <span className="mr-1.5 inline-block h-2 w-2 rounded-full bg-up" />
          System Status · API Connected
        </p>
        <p className="mt-1">Direction only — not investment advice.</p>
      </div>
    </aside>
  );
}
