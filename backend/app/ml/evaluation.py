"""Model evaluation. All metrics are computed on the chronological tail of the
data (see registry); scores around 45-65% accuracy are normal for next-day
direction and are reported honestly, alongside two naive baselines."""
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate(y_true, y_pred, y_proba, train_majority: int, y_momentum) -> dict:
    y_true = np.asarray(y_true)
    roc_auc = None
    if len(np.unique(y_true)) == 2:
        try:
            roc_auc = float(roc_auc_score(y_true, np.asarray(y_proba)))
        except ValueError:
            roc_auc = None
    tn, fp, fn, tp = confusion_matrix(y_true, np.asarray(y_pred), labels=[0, 1]).ravel().tolist()
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": roc_auc,
        "confusion": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
        "baseline_majority_acc": float(accuracy_score(y_true, np.full_like(y_true, train_majority))),
        "baseline_momentum_acc": float(accuracy_score(y_true, np.asarray(y_momentum))),
    }
