"""Module-level precision and recall against the seeded labels, using pandas.

Usage: python evaluate.py   (writes results/evaluation.json)
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from solid_check.analyzer import analyse_tree, module_flags  # noqa: E402

ROOT = Path(__file__).resolve().parent
PRINCIPLES = ["SRP", "OCP", "ISP"]


def evaluate():
    classes, functions, seconds = analyse_tree(ROOT / "corpus")
    flags = module_flags(classes, functions)
    labels = json.loads((ROOT / "corpus" / "labels.json").read_text())
    rows = []
    for m in sorted(labels):
        row = {"module": m}
        for p in PRINCIPLES:
            row[f"truth_{p}"] = p in labels[m]
            row[f"pred_{p}"] = p in flags.get(m, set())
        rows.append(row)
    df = pd.DataFrame(rows)
    out = {"modules": len(df), "analysis_seconds": round(seconds, 4), "per_principle": {}}
    for p in PRINCIPLES:
        tp = int((df[f"truth_{p}"] & df[f"pred_{p}"]).sum())
        fp = int((~df[f"truth_{p}"] & df[f"pred_{p}"]).sum())
        fn = int((df[f"truth_{p}"] & ~df[f"pred_{p}"]).sum())
        out["per_principle"][p] = {
            "tp": tp, "fp": fp, "fn": fn,
            "precision": round(tp / (tp + fp), 3) if tp + fp else None,
            "recall": round(tp / (tp + fn), 3) if tp + fn else None,
        }
    any_truth = df[[f"truth_{p}" for p in PRINCIPLES]].any(axis=1)
    any_pred = df[[f"pred_{p}" for p in PRINCIPLES]].any(axis=1)
    tp = int((any_truth & any_pred).sum())
    fp = int((~any_truth & any_pred).sum())
    fn = int((any_truth & ~any_pred).sum())
    out["module_level"] = {"tp": tp, "fp": fp, "fn": fn,
                           "precision": round(tp / (tp + fp), 3) if tp + fp else None,
                           "recall": round(tp / (tp + fn), 3) if tp + fn else None}
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "evaluation.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return df


if __name__ == "__main__":
    evaluate()
