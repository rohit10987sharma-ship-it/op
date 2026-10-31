"""
Unit tests for PDF Technical Report Generator.
"""

import os
import unittest
from web.app import app
from privlens.scanner.engine import ScannerEngine
from privlens.governance.mapper import GovernanceMapper
from privlens.evaluation.metrics import BenchmarkEvaluator
from privlens.reporters.pdf_reporter import PDFReporter

class TestPDFReporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        rules_path = os.path.join(base_dir, "config", "detection_rules.yaml")
        gov_path = os.path.join(base_dir, "config", "governance_registry.yaml")
        gt_path = os.path.join(base_dir, "datasets", "ground_truth.json")
        data_dir = os.path.join(base_dir, "datasets", "synthetic")

        engine = ScannerEngine(rules_path)
        mapper = GovernanceMapper(gov_path)
        evaluator = BenchmarkEvaluator(gt_path)

        fields = engine.scan_path(data_dir)
        cls.inventory = mapper.map_all(fields)
        cls.evaluation = evaluator.evaluate(fields)
        cls.test_pdf_path = os.path.join(base_dir, "reports", "test_report.pdf")

    def tearDown(self):
        if os.path.exists(self.test_pdf_path):
            try:
                os.remove(self.test_pdf_path)
            except Exception:
                pass

    def test_generate_pdf_report(self):
        path = PDFReporter.generate_report(self.inventory, self.evaluation, self.test_pdf_path)
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 5000)

        # Check PDF header magic bytes (%PDF)
        with open(path, "rb") as f:
            header = f.read(4)
        self.assertEqual(header, b"%PDF")

    def test_pdf_endpoint(self):
        import web.app
        web.app.cached_inventory = self.inventory
        web.app.cached_evaluation = self.evaluation
        client = app.test_client()
        res = client.get("/api/export/pdf")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, "application/pdf")
        self.assertGreater(len(res.data), 5000)
        self.assertTrue(res.data.startswith(b"%PDF"))

if __name__ == "__main__":
    unittest.main()
