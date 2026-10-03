import { Suspense } from "react";
import { ImportanceChart } from "../../components/ImportanceChart";
import { MetricsTable } from "../../components/MetricsTable";
import { SymbolSelect } from "../../components/SymbolSelect";
import { Card, ErrorState, SectionHead } from "../../components/ui";
import { api } from "../../lib/api";
import type { ModelsResponse } from "../../lib/types";

export default async function ModelsPage({ searchParams }: { searchParams: { symbol?: string } }) {
  let symbols: string[] = [];
  try {
    const s = (await api.stocks()) as { stocks: { symbol: string }[] };
    symbols = s.stocks.map((x) => x.symbol);
  } catch (e: unknown) {
    return <ErrorState message={e instanceof Error ? e.message : "Failed to load."} />;
  }
  const symbol = symbols.includes(searchParams.symbol ?? "") ? searchParams.symbol! : symbols[0];
  let m: ModelsResponse;
  try {
    m = (await api.models(symbol)) as ModelsResponse;
  } catch (e: unknown) {
    return <ErrorState message={e instanceof Error ? e.message : "Failed to load."} />;
  }
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Suspense>
          <SymbolSelect symbols={symbols} value={symbol} />
        </Suspense>
        <span className="text-xs text-muted">{m.target_definition} {m.split}</span>
      </div>
      <div>
        <SectionHead title="Model Comparison" sub="measured on the same test period — no ranking, just numbers" />
        <MetricsTable models={m.models} />
      </div>
      <div className="grid gap-3 lg:grid-cols-2">
        <Card>
          <SectionHead title="Confusion Matrices" sub="test set" />
          {m.models.map((r) => (
            <div key={r.key} className="mb-3 last:mb-0">
              <p className="text-[13px] font-semibold text-body">{r.name}</p>
              <div className="mt-1 grid max-w-xs grid-cols-2 gap-1 text-center text-xs tabular-nums">
                <div className="rounded-md border border-line bg-surface p-2">TN {r.confusion.tn}</div>
                <div className="rounded-md border border-line bg-surface p-2">FP {r.confusion.fp}</div>
                <div className="rounded-md border border-line bg-surface p-2">FN {r.confusion.fn}</div>
                <div className="rounded-md border border-line bg-surface p-2">TP {r.confusion.tp}</div>
              </div>
            </div>
          ))}
        </Card>
        <Card>
          <SectionHead title="Model Feature Importance" sub={m.importance_note} />
          <ImportanceChart data={m.feature_importance} />
        </Card>
      </div>
    </div>
  );
}
