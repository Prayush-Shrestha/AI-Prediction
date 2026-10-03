import type { Prediction } from "../lib/types";
import { pct, rs } from "../lib/format";
import { Badge, Card } from "./ui";

export function PredictionPanel({ p }: { p: Prediction }) {
  const dir = p.action === "HOLD" ? "HOLD" : p.prediction;
  return (
    <Card>
      <p className="text-xs uppercase tracking-wider text-muted">Next session prediction</p>
      <div className="mt-1 flex items-start justify-between gap-3">
        <div>
          <p className="text-xl font-bold text-body">{p.symbol}</p>
          <p className="mt-1 text-2xl font-bold text-body">{rs(p.current_price)}</p>
          <p className={`text-[13px] font-semibold ${p.change_pct >= 0 ? "text-up" : "text-down"}`}>
            {pct(p.change_pct)} today
          </p>
        </div>
        <div className="text-right">
          <Badge value={dir} />
          <p className="mt-2 text-xl font-bold text-body">{(p.confidence * 100).toFixed(1)}%</p>
          <p className="text-xs text-muted">confidence</p>
        </div>
      </div>
      <div className="mt-3 border-t border-line pt-3 text-[13px]">
        <div className="flex justify-between py-0.5">
          <span className="text-muted">Model</span>
          <span className="text-body">{p.model_label}</span>
        </div>
        <div className="flex justify-between py-0.5">
          <span className="text-muted">P(UP)</span>
          <span className="text-body">{p.p_up.toFixed(3)}</span>
        </div>
        <div className="flex justify-between py-0.5">
          <span className="text-muted">Last updated</span>
          <span className="text-body">{p.as_of}</span>
        </div>
      </div>
    </Card>
  );
}
