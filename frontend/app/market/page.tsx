import { Suspense } from "react";
import { IndicatorsCard } from "../../components/IndicatorsCard";
import { PriceChart } from "../../components/PriceChart";
import { SymbolSelect } from "../../components/SymbolSelect";
import { Card, ErrorState, SectionHead } from "../../components/ui";
import { api } from "../../lib/api";
import type { StockDetail } from "../../lib/types";

export default async function MarketPage({ searchParams }: { searchParams: { symbol?: string } }) {
  let symbols: string[] = [];
  try {
    const s = (await api.stocks()) as { stocks: { symbol: string }[] };
    symbols = s.stocks.map((x) => x.symbol);
  } catch (e: unknown) {
    return <ErrorState message={e instanceof Error ? e.message : "Failed to load."} />;
  }
  const symbol = symbols.includes(searchParams.symbol ?? "") ? searchParams.symbol! : symbols[0];
  let detail: StockDetail;
  try {
    detail = (await api.stock(symbol)) as StockDetail;
  } catch (e: unknown) {
    return <ErrorState message={e instanceof Error ? e.message : "Failed to load."} />;
  }
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Suspense>
          <SymbolSelect symbols={symbols} value={symbol} />
        </Suspense>
        <span className="text-xs text-muted">{detail.sector} · OHLCV from dataset</span>
      </div>
      <Card>
        <SectionHead title={`${symbol} — Price History`} sub="close with 20-day trend" />
        <PriceChart history={detail.history} height={360} />
      </Card>
      <IndicatorsCard indicators={detail.indicators} />
    </div>
  );
}
