"""
Evaluation and Performance Benchmarking Engine for PrivLens.
Calculates per-class Precision, Recall, F1-score, and Macro/Micro averages
against manually labeled ground truth.
"""

import json
from typing import List, Dict, Any, Optional
from privlens.models import DiscoveredField, ClassMetric, EvaluationSummary

DATA_CLASSES = {
    "PID": "Personal identity",
    "CNT": "Contact information",
    "GID": "Government identifiers",
    "FIN": "Financial information",
    "LOC": "Location / address"
}

class BenchmarkEvaluator:
    def __init__(self, ground_truth_path: str):
        self.ground_truth_path = ground_truth_path
        self.ground_truth = self._load_ground_truth(ground_truth_path)
        self.lookup = self._build_lookup()

    def _load_ground_truth(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _make_key(self, source: str, table: Optional[str], col: str) -> str:
        tbl_str = table.strip() if table else ""
        return f"{source.strip().lower()}::{tbl_str.lower()}::{col.strip().lower()}"

    def _build_lookup(self) -> Dict[str, Dict[str, Any]]:
        lookup = {}
        for item in self.ground_truth.get("fields", []):
            k = self._make_key(item["source"], item.get("table"), item["column"])
            lookup[k] = item
        return lookup

    def evaluate(self, discovered_fields: List[DiscoveredField]) -> EvaluationSummary:
        """
        Compares discovered fields against ground truth and generates
        per-class precision, recall, F1, and aggregate metrics.
        """
        # Initialize counts per class
        stats = {
            cid: {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "support": 0}
            for cid in DATA_CLASSES
        }

        matched_keys = set()
        confusion_details = []

        total_evaluated = 0
        total_true_pii = 0
        total_pred_pii = 0

        for field in discovered_fields:
            key = self._make_key(field.source_name, field.table_name, field.column_name)
            gt_item = self.lookup.get(key)
            if not gt_item:
                continue

            matched_keys.add(key)
            total_evaluated += 1

            true_is_pii = gt_item.get("is_pii", False)
            true_class = gt_item.get("true_class", "not personal data")
            if true_class == "NONE":
                true_class = "not personal data"
            if true_is_pii:
                total_true_pii += 1

            pred_is_pii = field.is_candidate_pii
            pred_class = field.candidate_class_id if pred_is_pii else "not personal data"
            if pred_is_pii:
                total_pred_pii += 1

            is_match = (true_class == pred_class)
            confusion_details.append({
                "source": field.source_name,
                "table": field.table_name,
                "column": field.column_name,
                "true_class": true_class,
                "predicted_class": pred_class,
                "confidence": field.confidence_score,
                "match": is_match
            })

            # Update per-class statistics
            for cid in DATA_CLASSES:
                if true_class == cid and pred_class == cid:
                    stats[cid]["tp"] += 1
                elif true_class != cid and pred_class == cid:
                    stats[cid]["fp"] += 1
                elif true_class == cid and pred_class != cid:
                    stats[cid]["fn"] += 1
                else:
                    stats[cid]["tn"] += 1

                if true_class == cid:
                    stats[cid]["support"] += 1

        # Check for any ground truth fields completely missed by scanner
        for k, gt_item in self.lookup.items():
            if k not in matched_keys:
                true_class = gt_item.get("true_class", "NONE")
                if true_class in DATA_CLASSES:
                    stats[true_class]["fn"] += 1
                    stats[true_class]["support"] += 1
                    total_evaluated += 1
                    total_true_pii += 1
                    confusion_details.append({
                        "source": gt_item["source"],
                        "table": gt_item.get("table"),
                        "column": gt_item["column"],
                        "true_class": true_class,
                        "predicted_class": "MISSED (NOT SCANNED)",
                        "confidence": 0.0,
                        "match": False
                    })

        # Calculate metrics per class
        class_metrics: Dict[str, ClassMetric] = {}
        precisions = []
        recalls = []
        f1s = []

        total_tp = sum(s["tp"] for s in stats.values())
        total_fp = sum(s["fp"] for s in stats.values())
        total_fn = sum(s["fn"] for s in stats.values())

        for cid, s in stats.items():
            tp = s["tp"]
            fp = s["fp"]
            fn = s["fn"]
            tn = s["tn"]
            sup = s["support"]

            precision = (tp / (tp + fp)) if (tp + fp) > 0 else (1.0 if sup == 0 and fp == 0 else 0.0)
            recall = (tp / (tp + fn)) if (tp + fn) > 0 else (1.0 if sup == 0 else 0.0)
            f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

            precisions.append(precision)
            recalls.append(recall)
            f1s.append(f1)

            class_metrics[cid] = ClassMetric(
                class_id=cid,
                class_name=DATA_CLASSES[cid],
                true_positives=tp,
                false_positives=fp,
                false_negatives=fn,
                true_negatives=tn,
                precision=round(precision, 4),
                recall=round(recall, 4),
                f1_score=round(f1, 4),
                support=sup
            )

        macro_p = sum(precisions) / len(precisions) if precisions else 0.0
        macro_r = sum(recalls) / len(recalls) if recalls else 0.0
        macro_f1 = sum(f1s) / len(f1s) if f1s else 0.0

        micro_p = (total_tp / (total_tp + total_fp)) if (total_tp + total_fp) > 0 else 0.0
        micro_r = (total_tp / (total_tp + total_fn)) if (total_tp + total_fn) > 0 else 0.0
        micro_f1 = (2 * micro_p * micro_r / (micro_p + micro_r)) if (micro_p + micro_r) > 0 else 0.0

        return EvaluationSummary(
            macro_precision=round(macro_p, 4),
            macro_recall=round(macro_r, 4),
            macro_f1=round(macro_f1, 4),
            micro_precision=round(micro_p, 4),
            micro_recall=round(micro_r, 4),
            micro_f1=round(micro_f1, 4),
            total_evaluated_fields=total_evaluated,
            total_true_pii=total_true_pii,
            total_predicted_pii=total_pred_pii,
            class_metrics=class_metrics,
            confusion_details=confusion_details
        )
