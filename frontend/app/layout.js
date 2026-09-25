import "./globals.css";
import Navbar from "../components/Navbar";

export const metadata = {
  title: "NEPSE Direction Tracker",
  description: "A next-session price direction dashboard for NEPSE-listed stocks.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col font-sans">
        <Navbar />
        <main className="flex-1 max-w-6xl w-full mx-auto px-5 py-8">{children}</main>
        <footer className="border-t border-black/5 py-6 text-center text-xs text-ink/50">
          Built as an academic project — technical-indicator model on historical
          price/volume data. Not investment advice.
        </footer>
      </body>
    </html>
  );
}
