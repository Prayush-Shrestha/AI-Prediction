"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();
  const linkClass = (href) =>
    `px-3 py-1.5 rounded-full text-sm transition-colors ${
      pathname === href
        ? "bg-indigo text-white"
        : "text-ink/70 hover:text-ink hover:bg-black/5"
    }`;

  return (
    <header className="border-b border-black/5 bg-paper/95 backdrop-blur sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-5 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-crimson inline-block" />
          <span className="font-serif text-lg tracking-tight">NEPSE Direction Tracker</span>
        </div>
        <nav className="flex gap-1">
          <Link href="/" className={linkClass("/")}>Dashboard</Link>
          <Link href="/analytics" className={linkClass("/analytics")}>Analytics</Link>
        </nav>
      </div>
    </header>
  );
}
