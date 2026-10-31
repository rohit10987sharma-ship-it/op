"""
Unit tests for Precision, Recall, and F1 Evaluation Metrics.
"""

import os
import unittest
from privlens.scanner.engine import ScannerEngine
from privlens.evaluation.metrics import BenchmarkEvaluator

class TestEvaluation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.rules_path = os.path.join(base_dir, "config", "detection_rules.yaml")
        cls.gt_path = os.path.join(base_dir, "datasets", "ground_truth.json")
        cls.data_dir = os.path.join(base_dir, "datasets", "synthetic")
        
        cls.engine = ScannerEngine(cls.rules_path)
        cls.evaluator = BenchmarkEvaluator(cls.gt_path)

    def test_benchmark_metrics(self):
        fields = self.engine.scan_path(self.data_dir)
        summary = self.evaluator.evaluate(fields)

        self.assertGreaterEqual(summary.total_evaluated_fields, 40)
        self.assertGreaterEqual(summary.macro_precision, 0.90)
        self.assertGreaterEqual(summary.macro_recall, 0.90)
        self.assertGreaterEqual(summary.macro_f1, 0.90)

        # Check that all 5 PS-019 classes are present
        for code in ["PID", "CNT", "GID", "FIN", "LOC"]:
            self.assertIn(code, summary.class_metrics)
            m = summary.class_metrics[code]
            self.assertGreater(m.support, 0)
            self.assertGreaterEqual(m.f1_score, 0.90)

if __name__ == "__main__":
    unittest.main()
