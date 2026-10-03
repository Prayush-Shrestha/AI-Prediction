import { SectionHead } from "../../components/ui";
import { WatchlistManager } from "../../components/WatchlistManager";
import { ErrorState } from "../../components/ui";
import { api } from "../../lib/api";

export default async function WatchlistPage() {
  let symbols: string[] = [];
  try {
    const s = (await api.stocks()) as { stocks: { symbol: string }[] };
    symbols = s.stocks.map((x) => x.symbol);
  } catch (e: unknown) {
    return <ErrorState message={e instanceof Error ? e.message : "Failed to load."} />;
  }
  return (
    <div className="space-y-3">
      <SectionHead title="Watchlist" sub="stored in the database via the backend API" />
      <WatchlistManager symbols={symbols} />
    </div>
  );
}
