export type Direction = "UP" | "DOWN";
export type Action = "UP" | "DOWN" | "HOLD";

export interface StockQuote {
  symbol: string;
  sector: string;
  current_price: number;
  change_pct: number;
  volume: number;
  date: string;
  prediction: Direction;
  action: Action;
  confidence: number;
  p_up: number;
}

export interface PricePoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Indicators {
  Close: number | null;
  Volume: number | null;
  rsi_14: number | null;
  sma_5: number | null;
  sma_10: number | null;
  sma_20: number | null;
  ema_10: number | null;
  ema_12: number | null;
  ema_26: number | null;
  macd_hist: number | null;
  macd_signal: number | null;
  bb_upper: number | null;
  bb_lower: number | null;
  bb_width: number | null;
  volatility_10: number | null;
  atr_14_norm: number | null;
}

export interface StockDetail {
  symbol: string;
  sector: string;
  indicators: Indicators;
  history: PricePoint[];
}

export interface ModelFactor {
  feature: string;
  importance: number;
  value: number | null;
}

export interface Prediction {
  symbol: string;
  model: string;
  model_label: string;
  current_price: number;
  change_pct: number;
  prediction: Direction;
  action: Action;
  p_up: number;
  confidence: number;
  threshold: number;
  as_of: string;
  factors: ModelFactor[];
}

export interface Confusion {
  tn: number;
  fp: number;
  fn: number;
  tp: number;
}

export interface ModelResult {
  name: string;
  key: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  roc_auc: number | null;
  confusion: Confusion;
  baseline_majority_acc: number;
  baseline_momentum_acc: number;
  train_n: number;
  test_n: number;
}

export interface ImportanceEntry {
  feature: string;
  importance: number;
}

export interface ModelsResponse {
  symbol: string;
  target_definition: string;
  split: string;
  models: ModelResult[];
  feature_importance: ImportanceEntry[];
  importance_note: string;
}

export interface DatasetInfo {
  records: number;
  symbols: number;
  start: string;
  end: string;
  train_n: number;
  test_n: number;
  target_definition: string;
  split: string;
}

export interface AnalyticsOverview {
  dataset: DatasetInfo;
  per_symbol_samples: Record<string, { rows: number; train_n: number; test_n: number }>;
  accuracy_by_symbol: Record<string, number | string>[];
  avg_feature_importance: ImportanceEntry[];
}

export interface HistoryRecord {
  id: number;
  symbol: string;
  as_of: string;
  prediction: Direction;
  action: Action;
  confidence: number;
  model: string;
  actual: Direction | null;
  correct: boolean | null;
}

export interface WatchlistItem {
  symbol: string;
  note: string;
  current_price: number | null;
  change_pct: number | null;
  prediction: Action | null;
  confidence: number | null;
}

export interface SimQuote {
  symbol: string;
  price: number;
  change_pct: number;
  prediction: Action;
  confidence: number;
}

export interface Health {
  status: string;
  version: string;
  symbols: number;
  data_csv: string;
  model_status: string;
}
