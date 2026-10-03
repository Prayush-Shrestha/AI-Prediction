import { Card, SectionHead } from "./ui";

const STEPS = [
  "Historical OHLCV",
  "Data Cleaning",
  "Feature Engineering",
  "Time-Based Split",
  "Model Training",
  "Prediction",
  "Evaluation",
  "Dashboard",
];

export function Methodology() {
  return (
    <Card>
      <SectionHead title="Methodology" sub="how a prediction is produced" />
      <ol className="flex flex-wrap items-center gap-1.5 text-xs">
        {STEPS.map((s, i) => (
          <li key={s} className="flex items-center gap-1.5">
            <span className="rounded-md border border-line bg-surface px-2 py-1 text-body">{s}</span>
            {i < STEPS.length - 1 ? <span className="text-muted">↓</span> : null}
          </li>
        ))}
      </ol>
      <p className="mt-3 text-xs text-muted">
        The split is chronological (no shuffling): the model never sees future data during training.
        Backtest accuracy near 50% is expected for next-day direction — the honest result to report.
      </p>
    </Card>
  );
}
