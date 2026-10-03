import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Shell } from "../components/Shell";
import "./globals.css";

export const metadata: Metadata = {
  title: "NEPSE Direction Tracker",
  description: "AI/ML-based next-session direction analytics for NEPSE stocks.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <Shell>{children}</Shell>
      </body>
    </html>
  );
}
