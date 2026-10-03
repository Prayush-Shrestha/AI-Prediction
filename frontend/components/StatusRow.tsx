import { Card } from "./ui";

export function StatusRow({
  stocks,
  updated,
  model,
}: {
  stocks: number;
  updated: string;
  model: string;
}) {
  const items = [
    { label: "Market Status", value: "Demo Simulation", sub: "not a real-time NEPSE feed" },
    { label: "Last Updated", value: updated, sub: "dataset as-of date" },
    { label: "Stocks Tracked", value: String(stocks), sub: "NEPSE symbols" },
    { label: "Model", value: model, sub: "primary model" },
  ];
  return (
    <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
      {items.map((i) => (
        <Card key={i.label} className="!p-3">
          <p className="text-xs text-muted">{i.label}</p>
          <p className="mt-0.5 text-base font-semibold text-body">{i.value}</p>
          <p className="text-xs text-muted">{i.sub}</p>
        </Card>
      ))}
    </div>
  );
}
