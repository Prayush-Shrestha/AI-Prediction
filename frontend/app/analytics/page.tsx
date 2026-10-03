import { AccuracyChart } from "../../components/AccuracyChart";
import { ImportanceChart } from "../../components/ImportanceChart";
import { Methodology } from "../../components/Methodology";
import { PriceChart } from "../../components/PriceChart";
import { Card, ErrorState, SectionHead } from "../../components/ui";
import { api } from "../../lib/api";
import type { AnalyticsOverview, StockDetail } from "../../lib/types";

export default async function AnalyticsPage() {
  let ov: AnalyticsOverview;
  try {
    ov = (await api.analyticsOverview()) as AnalyticsOverview;
  } catch (e: unknown) {
    return <ErrorState message={e instanceof Error ? e.message : "Failed to load."} />;
  }
  const d = ov.dataset;
  let first: StockDetail | null = null;
  try {
    first = (await api.stock("NABIL")) as StockDetail;
  } catch {
    first = null;
  }
  return (
    <div className="space-y-4">
      <section className="grid grid-cols-2 gap-3 xl:grid-cols-4">
        {[
          { l: "Records", v: String(d.records) },
          { l: "Symbols", v: String(d.symbols) },
          { l: "Date range", v: `${d.start} → ${d.end}` },
          { l: "Train / Test", v: `${d.train_n} / ${d.test_n}` },
        ].map((i) => (
          <Card key={i.l} className="!p-3">
            <p className="text-xs text-muted">{i.l}</p>
            <p className="mt-0.5 text-base font-semibold tabular-nums text-body">{i.v}</p>
          </Card>
        ))}
      </section>
      <Card>
        <SectionHead title="Accuracy by Symbol" sub="same data, features, split and target for every model" />
        <AccuracyChart rows={ov.accuracy_by_symbol} />
      </Card>
      <div className="grid gap-3 lg:grid-cols-2">
        <Card>
          <SectionHead title="Average Feature Importance" sub="Random Forest, mean over symbols" />
          <ImportanceChart data={ov.avg_feature_importance} />
        </Card>
        <Card>
          <SectionHead title="Samples per Symbol" sub="chronological 80/20 split" />
          <table className="w-full border-collapse text-[13px]">
            <thead>
              <tr className="text-left text-xs text-muted">
                <th className="py-1.5 font-semibold">Symbol</th>
                <th className="py-1.5 text-right font-semibold">Rows</th>
                <th className="py-1.5 text-right font-semibold">Train</th>
                <th className="py-1.5 text-right font-semibold">Test</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(ov.per_symbol_samples).map(([s, r]) => (
                <tr key={s} className="border-t border-line tabular-nums">
                  <td className="py-1.5 font-semibold text-body">{s}</td>
                  <td className="py-1.5 text-right text-muted">{r.rows}</td>
                  <td className="py-1.5 text-right text-muted">{r.train_n}</td>
                  <td className="py-1.5 text-right text-muted">{r.test_n}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>
      {first ? (
        <Card>
          <SectionHead title="Price History — NABIL" sub="interactive sample" />
          <PriceChart history={first.history} />
        </Card>
      ) : null}
      <Methodology />
    </div>
  );
}
