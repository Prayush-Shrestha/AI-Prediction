"""
dashboard.py
------------
Builds a professional financial-analytics HTML dashboard (dashboard.html).
No server needed. Run:  python dashboard.py   then open dashboard.html.

Data sources (unchanged logic — UI redesign only):
  data/nepse_sample.csv  -> price history / day changes
  predictions_output.csv -> predictions, confidence, backtest metrics
  feature_importance.csv -> model reasoning
Charts use the existing plotly dependency. No new dependencies.
All numbers shown are computed from the above files; nothing is invented.
The model predicts next-session DIRECTION only (UP/DOWN/HOLD), not a price
target, so the UI never shows a fabricated target price.
"""
import html as htmlmod
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PRICE_CSV = Path("data/nepse_sample.csv")
PRED_CSV = Path("predictions_output.csv")
IMP_CSV = Path("feature_importance.csv")
OUT_HTML = Path("dashboard.html")

BG, CARD, SURFACE = "#0B1220", "#111827", "#172033"
ACCENT, UP, DOWN = "#3B82F6", "#22C55E", "#EF4444"
TEXT, MUTED, BORDER = "#F8FAFC", "#94A3B8", "#243044"


# ---------------------------------------------------------------- data ----
def load_inputs():
    price = pd.read_csv(PRICE_CSV, parse_dates=["Date"])
    pred = pd.read_csv(PRED_CSV) if PRED_CSV.exists() else pd.DataFrame()
    imp = pd.read_csv(IMP_CSV, index_col=0) if IMP_CSV.exists() else pd.DataFrame()
    return price, pred, imp


def pct_col(s):
    return s.astype(str).str.rstrip("%").astype(float) / 100


def num_col(s):
    return pd.to_numeric(s, errors="coerce")


def rel_time(path):
    try:
        secs = (datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)).total_seconds()
    except OSError:
        return "unknown"
    if secs < 90:
        return "just now"
    if secs < 3600:
        return f"{int(secs // 60)} mins ago"
    if secs < 86400:
        return f"{int(secs // 3600)} hrs ago"
    return f"{int(secs // 86400)} days ago"


def last_changes(price):
    """Real 1-day % change per symbol from the price file."""
    out = {}
    for sym, g in price.groupby("Symbol"):
        g = g.sort_values("Date")
        if len(g) >= 2:
            prev, last = float(g["Close"].iloc[-2]), float(g["Close"].iloc[-1])
            out[sym] = (last - prev) / prev * 100 if prev else 0.0
        else:
            out[sym] = 0.0
    return out


# --------------------------------------------------------------- figures --
def style_fig(fig, height=360):
    fig.update_layout(
        height=height,
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(family="Inter, 'Segoe UI', Arial, sans-serif", size=12, color=MUTED),
        margin=dict(l=48, r=16, t=44, b=40),
        legend=dict(orientation="h", y=1.08, x=0, font=dict(size=11)),
        hoverlabel=dict(bgcolor=SURFACE, bordercolor=BORDER, font=dict(color=TEXT)),
    )
    fig.update_xaxes(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER, tickfont=dict(size=11))
    fig.update_yaxes(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER, tickfont=dict(size=11))
    return fig


def build_focus_fig(price, symbol, direction):
    """Historical close (solid) + 20-day trend (dashed) + 1-step direction
    projection (dashed). Projection magnitude = recent median daily move and is
    labelled illustrative: the model predicts direction, not price."""
    g = price[price.Symbol == symbol].sort_values("Date").tail(60).copy()
    g["sma20"] = g.Close.rolling(20).mean()
    med = float(g.Close.diff().abs().tail(20).median() or 0.0)
    last_date, last_close = g["Date"].iloc[-1], float(g["Close"].iloc[-1])
    step = {"UP": 1, "DOWN": -1}.get(direction, 0)
    next_date = pd.Timestamp(last_date) + pd.offsets.BDay(1)
    proj = last_close + step * med
    color = UP if step > 0 else (DOWN if step < 0 else MUTED)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=g.Date, y=g.Close, name="Historical close",
                             line=dict(width=2, color=ACCENT)))
    fig.add_trace(go.Scatter(x=g.Date, y=g.sma20, name="20-day trend",
                             line=dict(width=1, color=MUTED, dash="dash")))
    fig.add_trace(go.Scatter(x=[last_date, next_date], y=[last_close, proj],
                             name="Predicted next session (direction only)",
                             line=dict(width=2, color=color, dash="dash")))
    fig.update_layout(title=dict(text=f"{symbol} — last 60 sessions", font=dict(size=13, color=TEXT)),
                      yaxis_title="Price (Rs)", xaxis_title="Date")
    return style_fig(fig, 380)


def build_price_fig(price, symbol):
    g = price[price.Symbol == symbol].sort_values("Date").copy()
    g["sma5"] = g.Close.rolling(5).mean()
    g["sma20"] = g.Close.rolling(20).mean()
    std20 = g.Close.rolling(20).std()
    g["bb_up"] = g.sma20 + 2 * std20
    g["bb_lo"] = g.sma20 - 2 * std20
    d = g.Close.diff()
    rs = d.clip(lower=0).rolling(14).mean() / (-d.clip(upper=0)).rolling(14).mean().replace(0, np.nan)
    g["rsi"] = 100 - 100 / (1 + rs)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.07,
                        row_heights=[0.55, 0.2, 0.25],
                        subplot_titles=(f"{symbol} — Close, trend and volatility",
                                        "Volume", "RSI-14"))
    fig.add_trace(go.Scatter(x=g.Date, y=g.Close, name="Close",
                             line=dict(width=2, color=ACCENT)), 1, 1)
    fig.add_trace(go.Scatter(x=g.Date, y=g.sma5, name="SMA-5",
                             line=dict(width=1, color=MUTED, dash="dot")), 1, 1)
    fig.add_trace(go.Scatter(x=g.Date, y=g.sma20, name="SMA-20",
                             line=dict(width=1, color=TEXT, dash="dash")), 1, 1)
    fig.add_trace(go.Scatter(x=g.Date, y=g.bb_up, name="BB upper",
                             line=dict(width=1, color="#475569"), showlegend=False), 1, 1)
    fig.add_trace(go.Scatter(x=g.Date, y=g.bb_lo, name="BB lower", fill="tonexty",
                             fillcolor="rgba(148,163,184,0.10)",
                             line=dict(width=1, color="#475569"), showlegend=False), 1, 1)
    fig.add_trace(go.Bar(x=g.Date, y=g.Volume, name="Volume",
                         marker_color="rgba(59,130,246,0.45)"), 2, 1)
    fig.add_trace(go.Scatter(x=g.Date, y=g.rsi, name="RSI",
                             line=dict(width=1.5, color=ACCENT)), 3, 1)
    fig.add_hline(y=70, line_dash="dash", line_color=DOWN, row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color=UP, row=3, col=1)
    for ann in fig.layout.annotations:
        ann.font.color = TEXT
        ann.font.size = 12
    return style_fig(fig, 560)


# ------------------------------------------------------------------- html --
CSS = """
:root{--bg:#0B1220;--card:#111827;--surface:#172033;--accent:#3B82F6;
--up:#22C55E;--down:#EF4444;--text:#F8FAFC;--muted:#94A3B8;--border:#243044}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
font-family:Inter,'Segoe UI',system-ui,-apple-system,Arial,sans-serif;font-size:14px;line-height:1.5}
a{color:inherit}
/* sidebar */
.sidebar{position:fixed;inset:0 auto 0 0;width:240px;background:var(--card);
border-right:1px solid var(--border);display:flex;flex-direction:column;
padding:20px 14px;z-index:40;transition:transform .2s ease}
.brand{padding:2px 10px 16px;border-bottom:1px solid var(--border);margin-bottom:12px}
.brand b{display:block;font-size:15px;letter-spacing:.12em}
.brand span{font-size:12px;color:var(--muted);letter-spacing:.12em}
.nav{display:flex;flex-direction:column;gap:2px}
.nav a{text-decoration:none;color:var(--muted);font-size:13.5px;padding:9px 10px;
border-radius:8px;border:1px solid transparent}
.nav a:hover{background:var(--surface);color:var(--text)}
.nav a.active{background:rgba(59,130,246,.14);color:var(--text);border-color:rgba(59,130,246,.35)}
.nav .sep{border-top:1px solid var(--border);margin:10px 2px}
.nav a.disabled{opacity:.45;cursor:default}
.nav a.disabled:hover{background:none;color:var(--muted)}
.side-foot{margin-top:auto;padding:12px 10px 0;color:var(--muted);font-size:12px;
border-top:1px solid var(--border)}
/* main */
.main{margin-left:240px;min-width:0}
.wrap{max-width:1180px;margin:0 auto;padding:20px 24px 48px}
/* header */
.header{display:flex;align-items:center;gap:12px;padding:14px 0 4px}
.header h1{font-size:24px;margin:0;font-weight:650}
.header .hello{color:var(--muted);font-size:13px;margin:2px 0 0}
.hspace{flex:1}
.iconbtn{position:relative;background:var(--card);border:1px solid var(--border);
color:var(--text);border-radius:10px;padding:8px 11px;cursor:pointer;font-size:14px}
.iconbtn:hover{border-color:var(--accent)}
.iconbtn .dot{position:absolute;top:7px;right:8px;width:7px;height:7px;border-radius:50%;background:var(--accent)}
.alerts{position:relative}
.alerts summary{list-style:none;cursor:pointer}
.alerts summary::-webkit-details-marker{display:none}
.alerts .panel{position:absolute;right:0;top:44px;width:290px;background:var(--surface);
border:1px solid var(--border);border-radius:12px;padding:12px 14px;z-index:50}
.alerts .panel b{font-size:13px}
.alerts .panel ul{margin:8px 0 0;padding-left:18px;color:var(--muted);font-size:12.5px}
.profile{display:flex;align-items:center;gap:10px;background:var(--card);
border:1px solid var(--border);border-radius:10px;padding:6px 12px 6px 6px}
.avatar{width:30px;height:30px;border-radius:50%;background:var(--surface);
border:1px solid var(--border);display:flex;align-items:center;justify-content:center;
font-weight:700;font-size:13px;color:var(--text)}
.profile small{display:block;color:var(--muted);font-size:11.5px}
.burger{display:none;background:var(--card);border:1px solid var(--border);color:var(--text);
border-radius:10px;padding:8px 11px;cursor:pointer;font-size:15px}
/* status row */
.status{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:14px 0 4px}
.stat{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 16px}
.stat .l{font-size:12px;color:var(--muted)}
.stat .v{font-size:16px;font-weight:650;margin-top:2px}
.stat .s{font-size:12px;color:var(--muted)}
.pilldot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px;vertical-align:1px}
/* sections */
.sec{margin-top:22px}
.sec-h{display:flex;align-items:baseline;gap:10px;margin:0 0 10px}
.sec-h h2{font-size:17px;margin:0;font-weight:650}
.sec-h p{margin:0;color:var(--muted);font-size:12.5px}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;
padding:18px;box-shadow:0 1px 2px rgba(0,0,0,.35)}
.grid-2{display:grid;grid-template-columns:1.6fr 1fr;gap:12px}
.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.hero-top{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}
.eyebrow{font-size:12px;color:var(--muted);letter-spacing:.08em;text-transform:uppercase}
.hero-sym{font-size:20px;font-weight:700;margin:2px 0}
.hero-price{font-size:26px;font-weight:700;margin:6px 0 0}
.chg-up{color:var(--up);font-size:13px;font-weight:600}
.chg-down{color:var(--down);font-size:13px;font-weight:600}
.signal{text-align:right}
.signal .dir{font-size:15px;font-weight:700;letter-spacing:.06em;padding:5px 14px;
border-radius:8px;display:inline-block;border:1px solid var(--border)}
.dir.bull{color:var(--up);border-color:rgba(34,197,94,.4);background:rgba(34,197,94,.08)}
.dir.bear{color:var(--down);border-color:rgba(239,68,68,.4);background:rgba(239,68,68,.08)}
.dir.flat{color:var(--muted)}
.confbar{height:6px;background:var(--surface);border:1px solid var(--border);
border-radius:4px;margin-top:10px;overflow:hidden}
.confbar i{display:block;height:100%;background:var(--accent)}
.mini{font-size:12.5px;color:var(--muted);margin-top:8px}
/* summary cards */
.sum .k{font-size:12.5px;color:var(--muted)}
.sum .big{font-size:20px;font-weight:700;margin:4px 0 0}
.sum .sub{font-size:12.5px;color:var(--muted)}
/* metrics */
.metric{display:flex;justify-content:space-between;align-items:baseline;
padding:10px 2px;border-bottom:1px solid var(--border);font-size:13.5px}
.metric:last-child{border-bottom:none}
.metric b{font-size:15px;font-variant-numeric:tabular-nums}
.metric span{color:var(--muted)}
.note{font-size:12.5px;color:var(--muted);background:var(--surface);
border:1px solid var(--border);border-radius:10px;padding:10px 12px;margin-top:12px}
/* tables */
.table-wrap{overflow-x:auto;border:1px solid var(--border);border-radius:12px;background:var(--card)}
table{width:100%;border-collapse:collapse;font-size:13.5px;min-width:560px}
th,td{text-align:left;padding:10px 14px;border-bottom:1px solid var(--border);
font-variant-numeric:tabular-nums;white-space:nowrap}
thead th{font-size:12px;color:var(--muted);font-weight:600;background:var(--surface)}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover{background:rgba(59,130,246,.05)}
.tag{font-size:12px;font-weight:700;letter-spacing:.04em;padding:3px 10px;border-radius:7px;border:1px solid}
.tag.up{color:var(--up);border-color:rgba(34,197,94,.4);background:rgba(34,197,94,.08)}
.tag.down{color:var(--down);border-color:rgba(239,68,68,.4);background:rgba(239,68,68,.08)}
.tag.hold{color:var(--muted);border-color:var(--border);background:var(--surface)}
.num{text-align:right}
/* chart select */
.toolbar{display:flex;gap:10px;align-items:center;margin-bottom:10px;flex-wrap:wrap}
select{background:var(--surface);color:var(--text);border:1px solid var(--border);
border-radius:8px;padding:8px 10px;font-size:13px}
.hint{font-size:12.5px;color:var(--muted)}
.plot svg{max-width:100%}
footer{color:var(--muted);font-size:12px;margin-top:26px;border-top:1px solid var(--border);padding-top:14px}
/* responsive */
.scrim{display:none}
@media(max-width:1024px){
.grid-2{grid-template-columns:1fr}
.status{grid-template-columns:repeat(3,1fr)}
}
@media(max-width:860px){
.sidebar{transform:translateX(-100%)}
body.nav-open .sidebar{transform:none}
body.nav-open .scrim{display:block;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:30}
.main{margin-left:0}
.burger{display:inline-block}
.grid-3{grid-template-columns:1fr}
.status{grid-template-columns:1fr 1fr}
.header h1{font-size:20px}
.profile div{display:none}
}
@media(max-width:560px){.status{grid-template-columns:1fr}.wrap{padding:14px 14px 40px}}
"""

JS = """
function toggleNav(){document.body.classList.toggle('nav-open')}
document.querySelectorAll('.sidebar .nav a').forEach(function(a){
a.addEventListener('click',function(){document.body.classList.remove('nav-open')})});
var scrim=document.querySelector('.scrim');
if(scrim){scrim.addEventListener('click',function(){document.body.classList.remove('nav-open')})}
function pickSymbol(sel){
var v=sel.value;
document.querySelectorAll('.sympane').forEach(function(p){
p.style.display=(p.getAttribute('data-sym')===v)?'block':'none'});
if(window.Plotly){
document.querySelectorAll('.sympane').forEach(function(p){
if(p.style.display==='block'){
(p.querySelectorAll('.plotly-graph-div')||[]).forEach(function(d){
try{Plotly.Plots.resize(d)}catch(e){}})}})}}
"""


def badge(direction):
    return {"UP": ("BULLISH", "up"), "DOWN": ("BEARISH", "down")}.get(direction, ("NEUTRAL", "hold"))


def main():
    price, pred, imp = load_inputs()
    if pred.empty:
        print("predictions_output.csv not found — run: python predict.py first")
        return

    action_col = next((c for c in pred.columns if c.startswith("Action")), "Predicted Next Session")
    conf = pct_col(pred["Model Confidence"])
    focus_idx = int(conf.idxmax())
    focus = pred.loc[focus_idx]
    fsym, fdir = focus["Symbol"], focus["Predicted Next Session"]
    factual = focus[action_col]
    fconf = float(conf.loc[focus_idx])
    flabel, fcls = badge(factual if factual in ("UP", "DOWN") else fdir)
    fclose = float(focus["Last Close"])
    changes = last_changes(price)
    fchg = changes.get(fsym, 0.0)
    chg_cls = "chg-up" if fchg >= 0 else "chg-down"

    mean_acc = float(pct_col(pred["Backtest Accuracy"]).mean() * 100)
    mean_p = float(num_col(pred["Precision"]).mean())
    mean_r = float(num_col(pred["Recall"]).mean())
    mean_f1 = float(num_col(pred["F1"]).mean())
    n_up = int((pred["Predicted Next Session"] == "UP").sum())
    n_down = int((pred["Predicted Next Session"] == "DOWN").sum())
    n_hold = int((pred[action_col] == "HOLD").sum())
    asof = str(pred["As of"].max())
    pup = float(focus["P(UP)"]) if "P(UP)" in pred else 0.5
    conf_word = "High" if fconf >= 0.65 else ("Moderate" if fconf >= 0.55 else "Low")

    # Real alerts derived from the backtest table (no invented events).
    worst = pred.loc[pct_col(pred["Backtest Accuracy"]).idxmin()]
    alerts = [
        f"{worst['Symbol']} backtest accuracy {worst['Backtest Accuracy']} — below the 50% coin-flip line.",
        f"{n_hold} symbol(s) on HOLD at the 0.55 confidence gate." if n_hold else "No HOLD calls — every symbol cleared the 0.55 confidence gate.",
        f"Mean model accuracy {mean_acc:.1f}% vs majority baseline "
        f"{float(pct_col(pred['Baseline Majority']).mean() * 100):.1f}%.",
    ]
    alerts_html = "".join(f"<li>{htmlmod.escape(a)}</li>" for a in alerts)

    # ---- figures (same data as before, restyled to the palette) ----
    conf_colors = [
        UP if a == "UP" else (DOWN if a == "DOWN" else MUTED)
        for a in (pred[action_col] if action_col in pred else pred["Predicted Next Session"])
    ]
    fig_conf = go.Figure(go.Bar(x=pred.Symbol, y=pred["P(UP)"],
                                marker_color=conf_colors, name="P(UP)"))
    fig_conf.add_hline(y=0.5, line_dash="dash", line_color=MUTED)
    fig_conf.update_layout(title=dict(text="P(UP) per symbol — 0.50 is the coin-flip line",
                                      font=dict(size=13, color=TEXT)),
                           yaxis_title="P(UP)", yaxis_range=[0, 1])
    fig_conf = style_fig(fig_conf, 340)

    fig_base = go.Figure()
    fig_base.add_trace(go.Bar(x=pred.Symbol, y=pct_col(pred["Backtest Accuracy"]) * 100,
                              name="Model", marker_color=ACCENT))
    fig_base.add_trace(go.Bar(x=pred.Symbol, y=pct_col(pred["Baseline Majority"]) * 100,
                              name="Always majority", marker_color="#475569"))
    fig_base.add_trace(go.Bar(x=pred.Symbol, y=pct_col(pred["Baseline Momentum"]) * 100,
                              name="Same as yesterday", marker_color="#334155"))
    fig_base.add_hline(y=50, line_dash="dash", line_color=MUTED)
    fig_base.update_layout(title=dict(text="Backtest accuracy vs naive baselines",
                                      font=dict(size=13, color=TEXT)),
                           yaxis_title="Accuracy (%)", barmode="group")
    fig_base = style_fig(fig_base, 360)

    if not imp.empty:
        avg_imp = imp.mean().sort_values(ascending=True)
        fig_imp = go.Figure(go.Bar(x=avg_imp.values, y=avg_imp.index, orientation="h",
                                   marker_color=ACCENT, name="Importance"))
        fig_imp.update_layout(title=dict(text="Mean feature importance",
                                         font=dict(size=13, color=TEXT)),
                              xaxis_title="Importance")
        imp_html = fig_imp.to_html(full_html=False, include_plotlyjs=False)
        top_feats = htmlmod.escape(str(focus["Top Features"]))
    else:
        imp_html = '<p class="hint">Run predict.py to generate feature_importance.csv</p>'
        top_feats = "n/a"

    focus_fig = build_focus_fig(price, fsym,
                                factual if factual in ("UP", "DOWN") else fdir)

    # ---- per-symbol panes + selector (all existing charts preserved) ----
    options, panes = [], []
    for i, s in enumerate(pred.Symbol.tolist()):
        options.append(f'<option value="{s}"{" selected" if s == fsym else ""}>{s}</option>')
        panes.append(
            f'<div class="sympane" data-sym="{s}" style="display:'
            f'{"block" if s == fsym else "none"}">'
            f"{build_price_fig(price, s).to_html(full_html=False, include_plotlyjs=False)}</div>"
        )

    # ---- watchlist (real symbols, real 1-day change, real prediction) ----
    wl_rows = []
    for _, r in pred.sort_values("Symbol").iterrows():
        c = changes.get(r["Symbol"], 0.0)
        lbl, cls = badge(r[action_col])
        wl_rows.append(
            f"<tr><td><b>{r['Symbol']}</b></td><td class=\"num\">Rs {float(r['Last Close']):,.2f}</td>"
            f"<td class=\"num\" style=\"color:{UP if c >= 0 else DOWN}\">{c:+.2f}%</td>"
            f"<td><span class=\"tag {cls}\">{lbl}</span></td></tr>"
        )

    # ---- history (the prediction run itself; result = backtest on that symbol) ----
    hist_rows = []
    for _, r in pred.sort_values("Symbol").iterrows():
        lbl, cls = badge(r[action_col])
        hist_rows.append(
            f"<tr><td><b>{r['Symbol']}</b></td><td><span class=\"tag {cls}\">{lbl}</span></td>"
            f"<td class=\"num\">{r['Model Confidence']}</td><td>{r['As of']}</td>"
            f"<td class=\"num\">backtest {r['Backtest Accuracy']}</td></tr>"
        )

    updated = rel_time(PRED_CSV)

    page = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Share Prediction — Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>""" + CSS + """</style></head><body>
<div class="scrim"></div>
<aside class="sidebar">
<div class="brand"><b>AI SHARE</b><span>PREDICTION</span></div>
<nav class="nav">
<a href="#top" class="active">Dashboard</a>
<a href="#predictions">Predictions</a>
<a href="#market">Market Data</a>
<a href="#watchlist">Watchlist</a>
<a href="#history">History</a>
<div class="sep"></div>
<a href="#" class="disabled">Settings</a>
<a href="#" class="disabled">Help</a>
</nav>
<div class="side-foot">NEPSE demo model · direction only,<br>not investment advice.</div>
</aside>
<div class="main"><div class="wrap" id="top">
<header class="header">
<button class="burger" onclick="toggleNav()" aria-label="Menu">☰</button>
<div><h1>Dashboard</h1><p class="hello">Good evening, Prayush<br>AI-powered market prediction overview</p></div>
<div class="hspace"></div>
<details class="alerts"><summary class="iconbtn">🔔<span class="dot"></span></summary>
<div class="panel"><b>Notifications</b><ul>""" + alerts_html + """</ul></div></details>
<div class="profile"><div class="avatar">P</div><div>Prayush<small>Analyst workspace</small></div></div>
</header>
<section class="status">
<div class="stat"><div class="l">Market Status</div><div class="v"><span class="pilldot" style="background:""" + MUTED + """></span>EOD sample</div><div class="s">Data as of """ + htmlmod.escape(asof) + """</div></div>
<div class="stat"><div class="l">Last Updated</div><div class="v">""" + htmlmod.escape(updated) + """</div><div class="s">predictions_output.csv</div></div>
<div class="stat"><div class="l">Model Accuracy</div><div class="v">""" + f"{mean_acc:.1f}%" + """</div><div class="s">mean backtest · """ + f"{n_up} up / {n_down} down / {n_hold} hold" + """</div></div>
</section>
<section class="sec" id="predictions">
<div class="sec-h"><h2>Share Prediction</h2><p>Highest-confidence call from the latest run</p></div>
<div class="grid-2">
<div class="card"><div class="hero-top">
<div><div class="eyebrow">Featured symbol</div>
<div class="hero-sym">""" + htmlmod.escape(str(fsym)) + """ <span class="hint">NEPSE · as of """ + htmlmod.escape(str(focus["As of"])) + """</span></div>
<div class="hero-price">Rs """ + f"{fclose:,.2f}" + """ <span class=\"""" + chg_cls + """\">""" + f"{fchg:+.2f}% today" + """</span></div>
<div class="mini\">Model output: <b>""" + htmlmod.escape(str(fdir)) + """</b> · P(UP) """ + f"{pup:.3f}" + """ · """ + htmlmod.escape(str(focus["Backtest Accuracy"])) + """ backtest on this symbol.</div>
</div>
<div class="signal\"><div class="eyebrow\">Prediction</div><br><span class="dir """ + fcls + """\">""" + flabel + """</span>
<div class="eyebrow" style="margin-top:12px">Confidence</div>
<div style="font-size:20px;font-weight:700">""" + f"{fconf * 100:.1f}%" + """</div>
<div class="confbar"><i style="width:""" + f"{fconf * 100:.0f}%" + """></i></div></div>
</div></div>
<div class="card"><div class="eyebrow\">Prediction signal</div>
<div style="font-size:16px;font-weight:700;margin:6px 0"><span class="dir """ + fcls + """\">""" + flabel + """</span></div>
<div class="mini\">Confidence <b style="color:""" + TEXT + """\">""" + f"{fconf * 100:.1f}% ({conf_word})" + """</b></div>
<div class="mini\">Supporting features: """ + top_feats + """</div>
<div class="note\">Backtest near 50% is expected for next-session direction (weak-form efficiency). Judge the model against the baselines below, not against perfection.</div>
</div>
</div>
<div class="grid-3" style="margin-top:12px">
<div class="card sum\"><div class="k\">Current Price</div><div class="big\">Rs """ + f"{fclose:,.2f}" + """</div><div class="sub\">""" + f"{fchg:+.2f}% vs previous session" + """</div></div>
<div class="card sum\"><div class="k\">Prediction</div><div class="big\">""" + flabel.title() + """</div><div class="sub\">Next session · P(UP) """ + f"{pup:.3f}" + """ · direction only, no price target</div></div>
<div class="card sum\"><div class="k\">Confidence</div><div class="big\">""" + f"{fconf * 100:.1f}%" + """</div><div class="sub\">""" + conf_word + """ · gate 55% (below = HOLD)</div></div>
</div>
</section>
<section class="sec" id="market">
<div class="sec-h\"><h2>Price &amp; Prediction Chart</h2><p>Solid = historical close · dashed grey = 20-day trend · dashed colour = predicted direction (illustrative step)</p></div>
<div class="card">""" + focus_fig.to_html(full_html=False, include_plotlyjs=False) + """</div>
<div class="sec-h\" style="margin-top:18px"><h2>Market Data</h2><p>Per-symbol technicals: trend, Bollinger envelope, volume, RSI-14</p></div>
<div class="card"><div class="toolbar\"><label for="symsel\" class="hint\">Symbol</label>
<select id="symsel\" onchange="pickSymbol(this)">""" + "".join(options) + """</select>
<span class="hint\">Close with SMA-5/20 and Bollinger bands · volume · RSI with 70/30 levels.</span></div>
""" + "".join(panes) + """</div>
<div class="grid-2\" style="margin-top:12px">
<div class="card\"><div class="sec-h\"><h2>Confidence by Symbol</h2></div>""" + fig_conf.to_html(full_html=False, include_plotlyjs=False) + """</div>
<div class="card\"><div class="sec-h\"><h2>Model vs Baselines</h2></div>""" + fig_base.to_html(full_html=False, include_plotlyjs=False) + """<div class="note\">Lift over “always majority” and “same as yesterday” is the result to report.</div></div>
</div>
</section>
<section class="sec\" id="performance">
<div class="sec-h\"><h2>Model Performance</h2><p>Mean backtest metrics across """ + f"{len(pred)} symbols" + """</p></div>
<div class="grid-2\">
<div class="card\">
<div class="metric\"><span>Accuracy</span><b>""" + f"{mean_acc:.1f}%" + """</b></div>
<div class="metric\"><span>Precision</span><b>""" + f"{mean_p:.3f}" + """</b></div>
<div class="metric\"><span>Recall</span><b>""" + f"{mean_r:.3f}" + """</b></div>
<div class="metric\"><span>F1 Score</span><b>""" + f"{mean_f1:.3f}" + """</b></div>
<div class="note\">Time-based train/test split per symbol (no shuffling, no lookahead). Class-weighted Random Forest, 300 trees.</div>
</div>
<div class="card\"><div class="sec-h\"><h2>What Drives the Model</h2></div>""" + imp_html + """</div>
</div>
</section>
<section class="sec\" id="watchlist">
<div class="sec-h\"><h2>Watchlist</h2><p>All """ + f"{len(pred)}" + """ modelled NEPSE symbols</p></div>
<div class="table-wrap\"><table><thead><tr><th>Company</th><th style="text-align:right">Price</th><th style="text-align:right">Change</th><th>Prediction</th></tr></thead>
<tbody>""" + "".join(wl_rows) + """</tbody></table></div>
</section>
<section class="sec\" id="history">
<div class="sec-h\"><h2>Recent Predictions</h2><p>Latest run per symbol</p></div>
<div class="table-wrap\"><table><thead><tr><th>Stock</th><th>Prediction</th><th style="text-align:right">Confidence</th><th>Date</th><th style="text-align:right">Result</th></tr></thead>
<tbody>""" + "".join(hist_rows) + """</tbody></table></div>
</section>
<footer>Generated by dashboard.py from data/nepse_sample.csv, predictions_output.csv and feature_importance.csv. Demo methodology — direction prediction is noisy; treat output as probability, never as financial advice.</footer>
</div></div>
<script>""" + JS + """</script>
</body></html>"""

    OUT_HTML.write_text(page, encoding="utf-8")
    print(f"Saved -> {OUT_HTML.resolve()}  ({OUT_HTML.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
