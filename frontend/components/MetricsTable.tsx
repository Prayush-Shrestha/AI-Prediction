import type { ModelResult } from "../lib/types";
import { Card } from "./ui";

export function MetricsTable({ models }: { models: ModelResult[] }) {
  return (
    <Card className="!p-0">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[560px] border-collapse text-[13px]">
          <thead>
            <tr className="bg-surface text-left text-xs text-muted">
              <th className="px-3.5 py-2.5 font-semibold">Model</th>
              <th className="px-3.5 py-2.5 text-right font-semibold">Accuracy</th>
              <th className="px-3.5 py-2.5 text-right font-semibold">Precision</th>
              <th className="px-3.5 py-2.5 text-right font-semibold">Recall</th>
              <th className="px-3.5 py-2.5 text-right font-semibold">F1</th>
              <th className="px-3.5 py-2.5 text-right font-semibold">ROC-AUC</th>
            </tr>
          </thead>
          <tbody>
            {models.map((m) => (
              <tr key={m.key} className="border-t border-line tabular-nums">
                <td className="px-3.5 py-2.5 font-semibold text-body">{m.name}</td>
                <td className="px-3.5 py-2.5 text-right text-body">{(m.accuracy * 100).toFixed(1)}%</td>
                <td className="px-3.5 py-2.5 text-right text-body">{m.precision.toFixed(3)}</td>
                <td className="px-3.5 py-2.5 text-right text-body">{m.recall.toFixed(3)}</td>
                <td className="px-3.5 py-2.5 text-right text-body">{m.f1.toFixed(3)}</td>
                <td className="px-3.5 py-2.5 text-right text-muted">
                  {m.roc_auc === null ? "N/A" : m.roc_auc.toFixed(3)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
