import { SimBanner } from "../components/SimBanner";
import { StatusRow } from "../components/StatusRow";
import { StockTable } from "../components/StockTable";
import { Card, ErrorState, SectionHead } from "../components/ui";
import { api } from "../lib/api";
import type { StockQuote } from "../lib/types";

export default async function Dashboard() {
  let stocks: StockQuote[] = [];
  try {
    const body = (await api.stocks()) as { stocks: StockQuote[] };
    stocks = body.stocks;
  } catch (e: unknown) {
    return <ErrorState message={e instanceof Error ? e.message : "Failed to load."} />;
  }
  const updated = stocks.length ? stocks[0].date : "N/A";
  return (
    <div className="space-y-4">
      <StatusRow stocks={stocks.length} updated={updated} model="Random Forest" />
      <SimBanner />
      <section>
        <SectionHead title="Stocks" sub={`${stocks.length} NEPSE symbols · click a symbol for its prediction`} />
        <StockTable stocks={stocks} />
      </section>
      <Card>
        <SectionHead title="About this demo" />
        <p className="text-[13px] text-muted">
          The model predicts next-session <b className="text-body">direction (UP/DOWN)</b>, not price.
          Live movement above is a labelled simulation; evaluation uses a chronological split, so
          backtest accuracy near 50% is the honest, expected result for noisy daily data.
        </p>
      </Card>
    </div>
  );
}
