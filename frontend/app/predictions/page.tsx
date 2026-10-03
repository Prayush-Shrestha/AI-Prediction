import { Suspense } from "react";
import { IndicatorsCard } from "../../components/IndicatorsCard";
import { ImportanceChart } from "../../components/ImportanceChart";
import { ModelSelect } from "../../components/ModelSelect";
import { PredictionPanel } from "../../components/PredictionPanel";
import { PriceChart } from "../../components/PriceChart";
import { SymbolSelect } from "../../components/SymbolSelect";
import { Card, ErrorState, SectionHead } from "../../components/ui";
import { api } from "../../lib/api";
import { num } from "../../lib/format";
import type { Prediction, StockDetail } from "../../lib/types";

const MODELS = [
  { key: "random_forest", label: "Random Forest" },
  { key: "logistic_regression", label: "Logistic Regression" },
  { key: "gradient_boosting", label: "Gradient Boosting" },
];

export default async function PredictionsPage({
  searchParams,
}: {
  searchParams: { symbol?: string; model?: string };
}) {
  let symbols: string[] = [];
  try {
    const s = (await api.stocks()) as { stocks: { symbol: string }[] };
    symbols = s.stocks.map((x) => x.symbol);
  } catch (e: unknown) {
    return <ErrorState message={e instanceof Error ? e.message : "Failed to load."} />;
  }
  const symbol = symbols.includes(searchParams.symbol ?? "") ? searchParams.symbol! : symbols[0];
  const model = MODELS.some((m) => m.key === searchParams.model) ? searchParams.model! : MODELS[0].key;

  let pred: Prediction;
  let detail: StockDetail;
  try {
    [pred, detail] = (await Promise.all([
      api.prediction(symbol, model),
      api.stock(symbol),
    ])) as [Prediction, StockDetail];
  } catch (e: unknown) {
    return <ErrorState message={e instanceof Error ? e.message : "Failed to load prediction."} />;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <Suspense>
          <SymbolSelect symbols={symbols} value={symbol} />
        </Suspense>
        <Suspense>
          <ModelSelect value={model} />
        </Suspense>
        <span className="text-xs text-muted">
          {detail.sector} · prediction recorded to history
        </span>
      </div>
      <div className="grid gap-3 lg:grid-cols-5">
        <div className="lg:col-span-2">
          <PredictionPanel p={pred} />
        </div>
        <div className="lg:col-span-3">
          <Card>
            <SectionHead title={`${symbol} — Price History`} sub="close with 20-day trend" />
            <PriceChart history={detail.history} />
          </Card>
        </div>
      </div>
      <div className="grid gap-3 lg:grid-cols-2">
        <Card>
          <SectionHead
            title="Important Model Features"
            sub="actual values at prediction time · importance, not causation"
          />
          <table className="w-full border-collapse text-[13px]">
            <thead>
              <tr className="text-left text-xs text-muted">
                <th className="py-1.5 font-semibold">Feature</th>
                <th className="py-1.5 text-right font-semibold">Value</th>
                <th className="py-1.5 text-right font-semibold">Importance</th>
              </tr>
            </thead>
            <tbody>
              {pred.factors.map((f) => (
                <tr key={f.feature} className="border-t border-line tabular-nums">
                  <td className="py-1.5 text-body">{f.feature}</td>
                  <td className="py-1.5 text-right text-muted">{f.value === null ? "N/A" : num(f.value, 4)}</td>
                  <td className="py-1.5 text-right text-body">{f.importance.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
        <div>
          <IndicatorsCard indicators={detail.indicators} />
        </div>
      </div>
      <Card>
        <SectionHead title="All Features — Model View" />
        <FullImportance symbol={symbol} />
      </Card>
    </div>
  );
}

async function FullImportance({ symbol }: { symbol: string }) {
  try {
    const m = (await api.models(symbol)) as { feature_importance: { feature: string; importance: number }[] };
    return <ImportanceChart data={m.feature_importance} height={360} />;
  } catch {
    return <p className="text-sm text-muted">Feature importance unavailable.</p>;
  }
}
