"""
dashboard.py
------------
Builds an interactive HTML dashboard (dashboard.html) — no server needed.
Just run:  python dashboard.py   then open dashboard.html in a browser.

Shows: KPIs, predictions table, P(UP) confidence, backtest vs baselines,
feature importance, and per-symbol price + SMA + Bollinger + volume + RSI.
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path

PRICE_CSV = Path("data/nepse_sample.csv")
PRED_CSV = Path("predictions_output.csv")
IMP_CSV = Path("feature_importance.csv")
OUT_HTML = Path("dashboard.html")


def load_inputs():
    price = pd.read_csv(PRICE_CSV, parse_dates=["Date"])
    pred = pd.read_csv(PRED_CSV) if PRED_CSV.exists() else pd.DataFrame()
    imp = pd.read_csv(IMP_CSV, index_col=0) if IMP_CSV.exists() else pd.DataFrame()
    return price, pred, imp


def pct_col(s):
    return s.astype(str).str.rstrip("%").astype(float) / 100


def build_price_fig(price, symbol):
    g = price[price.Symbol == symbol].sort_values("Date").copy()
    g["sma5"] = g.Close.rolling(5).mean()
    g["sma20"] = g.Close.rolling(20).mean()
    std20 = g.Close.rolling(20).std()
    g["bb_up"] = g.sma20 + 2 * std20
    g["bb_lo"] = g.sma20 - 2 * std20
    # RSI-14
    d = g.Close.diff()
    gain, loss = d.clip(lower=0), -d.clip(upper=0)
    rs = gain.rolling(14).mean() / loss.rolling(14).mean().replace(0, np.nan)
    g["rsi"] = 100 - 100 / (1 + rs)

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06,
        row_heights=[0.55, 0.2, 0.25],
        subplot_titles=(f"{symbol} — Close + SMA5/20 + Bollinger", "Volume", "RSI-14"),
    )
    fig.add_trace(go.Scatter(x=g.Date, y=g.Close, name="Close", line=dict(width=2)), 1, 1)
    fig.add_trace(go.Scatter(x=g.Date, y=g.sma5, name="SMA-5", line=dict(dash="dot")), 1, 1)
    fig.add_trace(go.Scatter(x=g.Date, y=g.sma20, name="SMA-20", line=dict(dash="dash")), 1, 1)
    fig.add_trace(go.Scatter(x=g.Date, y=g.bb_up, name="BB upper",
                             line=dict(width=1, color="gray"), showlegend=False), 1, 1)
    fig.add_trace(go.Scatter(x=g.Date, y=g.bb_lo, name="BB lower",
                             line=dict(width=1, color="gray"),
                             fill="tonexty", fillcolor="rgba(150,150,150,0.15)",
                             showlegend=False), 1, 1)
    fig.add_trace(go.Bar(x=g.Date, y=g.Volume, name="Volume", marker_opacity=0.6), 2, 1)
    fig.add_trace(go.Scatter(x=g.Date, y=g.rsi, name="RSI", line=dict(color="purple")), 3, 1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    fig.update_layout(height=650, margin=dict(t=50, b=20),
                      legend=dict(orientation="h", y=1.05))
    return fig


def main():
    price, pred, imp = load_inputs()
    if pred.empty:
        print("predictions_output.csv not found — run: python predict.py first")
        return
    symbols = pred.Symbol.tolist()

    # ---- KPIs ----
    accs = pct_col(pred["Backtest Accuracy"]) if "Backtest Accuracy" in pred else pd.Series([np.nan])
    action_col = next((c for c in pred.columns if c.startswith("Action")), None)
    n_up = (pred["Predicted Next Session"] == "UP").sum()
    n_down = (pred["Predicted Next Session"] == "DOWN").sum()
    n_hold = (pred[action_col] == "HOLD").sum() if action_col else 0
    mean_acc = accs.mean() * 100
    mean_pup = pred["P(UP)"].mean() if "P(UP)" in pred else float("nan")

    # ---- Fig 1: P(UP) confidence ----
    color = pred.apply(
        lambda r: "#22c55e" if (action_col and r[action_col] == "UP")
        else ("#ef4444" if (action_col and r[action_col] == "DOWN")
              else ("#22c55e" if r["Predicted Next Session"] == "UP" else "#ef4444")), axis=1)
    fig_conf = go.Figure(go.Bar(
        x=pred.Symbol, y=pred["P(UP)"] if "P(UP)" in pred else [],
        marker_color=color.tolist(), text=pred["P(UP)"] if "P(UP)" in pred else None,
        textposition="outside"))
    fig_conf.add_hline(y=0.5, line_dash="dash", line_color="black")
    fig_conf.update_layout(title="Model confidence P(UP) per symbol (line = 50% coin-flip)",
                           yaxis_title="P(UP)", height=380)

    # ---- Fig 2: backtest vs baselines ----
    fig_base = go.Figure()
    if "Backtest Accuracy" in pred:
        a = pct_col(pred["Backtest Accuracy"]) * 100
        m1 = pct_col(pred["Baseline Majority"]) * 100 if "Baseline Majority" in pred else None
        m2 = pct_col(pred["Baseline Momentum"]) * 100 if "Baseline Momentum" in pred else None
        fig_base.add_trace(go.Bar(x=pred.Symbol, y=a, name="Model accuracy"))
        if m1 is not None:
            fig_base.add_trace(go.Bar(x=pred.Symbol, y=m1, name="Baseline: always majority"))
        if m2 is not None:
            fig_base.add_trace(go.Bar(x=pred.Symbol, y=m2, name="Baseline: same as yesterday"))
        fig_base.add_hline(y=50, line_dash="dash", line_color="black")
        fig_base.update_layout(title="Backtest: model vs naive baselines (above 50% = real edge)",
                               yaxis_title="Accuracy %", barmode="group", height=400)

    # ---- Fig 3: avg feature importance ----
    if not imp.empty:
        avg_imp = imp.mean().sort_values(ascending=True)
        fig_imp = go.Figure(go.Bar(x=avg_imp.values, y=avg_imp.index, orientation="h",
                                   marker_color="#6366f1"))
        fig_imp.update_layout(title="Avg feature importance (what drives the model?)",
                              xaxis_title="Mean importance", height=420)
        imp_html = fig_imp.to_html(full_html=False, include_plotlyjs=False)
    else:
        imp_html = "<p>Run predict.py to generate feature_importance.csv</p>"

    # ---- Price figs (one per symbol, tabbed with <details>) ----
    price_sections = ""
    for i, s in enumerate(symbols):
        fig = build_price_fig(price, s)
        open_attr = " open" if i == 0 else ""
        price_sections += (
            f"<details{open_attr} class='card'><summary><b>{s}</b> — price, volume & RSI "
            f"(click to expand)</summary>"
            f"{fig.to_html(full_html=False, include_plotlyjs=False)}</details>\n"
        )

    # ---- Predictions table ----
    def action_badge(v):
        cls = {"UP": "up", "DOWN": "down", "HOLD": "hold"}.get(str(v), "")
        return f"<span class='badge {cls}'>{v}</span>"

    tbl = pred.copy()
    if action_col:
        tbl[action_col] = tbl[action_col].apply(action_badge)
    tbl["Predicted Next Session"] = tbl["Predicted Next Session"].apply(action_badge)
    table_html = tbl.to_html(index=False, escape=False, classes="ptable")

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>NEPSE Prediction Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:24px}}
h1{{margin:0 0 4px}} .sub{{color:#94a3b8;margin-bottom:18px}}
.kpis{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:18px}}
.kpi{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:14px 18px;min-width:150px}}
.kpi .v{{font-size:24px;font-weight:700}} .kpi .l{{color:#94a3b8;font-size:13px}}
.card{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:16px;margin:14px 0}}
summary{{cursor:pointer;padding:6px;font-size:16px}}
.badge{{padding:3px 12px;border-radius:20px;font-weight:700;font-size:13px}}
.up{{background:#14532d;color:#86efac}} .down{{background:#450a0a;color:#fca5a5}} .hold{{background:#422006;color:#fcd34d}}
table.ptable{{width:100%;border-collapse:collapse;font-size:14px}}
.ptable th,.ptable td{{border-bottom:1px solid #334155;padding:8px 10px;text-align:left}}
.ptable th{{color:#94a3b8}} .warn{{background:#422006;border:1px solid #b45309;border-radius:10px;padding:12px 16px}}
</style></head><body>
<h1>📈 NEPSE Next-Session Dashboard</h1>
<div class="sub">Demo ML pipeline — direction prediction is noisy; treat as probability, not advice.</div>
<div class="kpis">
<div class="kpi"><div class="v">{len(pred)}</div><div class="l">Symbols</div></div>
<div class="kpi"><div class="v">{mean_acc:.1f}%</div><div class="l">Mean backtest accuracy</div></div>
<div class="kpi"><div class="v">{mean_pup:.2f}</div><div class="l">Mean P(UP)</div></div>
<div class="kpi"><div class="v">🟢 {n_up} / 🔴 {n_down} / 🟡 {n_hold}</div><div class="l">UP / DOWN / HOLD</div></div>
</div>
<div class="warn">⚠️ Backtest near 50% is <b>expected</b> (weak-form efficiency). Your edge = model F1/accuracy <b>minus baselines</b>, not accuracy alone.</div>
<div class="card"><h2>Predictions</h2>{table_html}</div>
<div class="card"><h2>Confidence</h2>{fig_conf.to_html(full_html=False, include_plotlyjs=False)}</div>
<div class="card"><h2>Model vs baselines</h2>{fig_base.to_html(full_html=False, include_plotlyjs=False) if fig_base.data else "<p>n/a</p>"}</div>
<div class="card"><h2>Feature importance</h2>{imp_html}</div>
<h2>Per-symbol technicals</h2>
{price_sections}
<p class="sub">Generated by dashboard.py · data: {PRICE_CSV} · predictions: {PRED_CSV}</p>
</body></html>"""
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Saved -> {OUT_HTML.resolve()}  ({OUT_HTML.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
