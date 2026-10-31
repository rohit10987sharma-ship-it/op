"""
Unit tests for PrivLens CSV and SQL Scanners (PS-019 classes).
"""

import os
import unittest
from privlens.scanner.engine import ScannerEngine

class TestScanners(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.rules_path = os.path.join(base_dir, "config", "detection_rules.yaml")
        cls.data_dir = os.path.join(base_dir, "datasets", "synthetic")
        cls.engine = ScannerEngine(cls.rules_path)

    def test_csv_scanner(self):
        csv_file = os.path.join(self.data_dir, "customer_signups.csv")
        self.assertTrue(os.path.exists(csv_file), f"CSV not found: {csv_file}")
        fields = self.engine.csv_scanner.scan_file(csv_file)
        self.assertEqual(len(fields), 9)
        
        # Check specific discovered fields
        email_field = next(f for f in fields if f.column_name == "email_address")
        self.assertTrue(email_field.is_candidate_pii)
        self.assertEqual(email_field.candidate_class_id, "CNT")

        name_field = next(f for f in fields if f.column_name == "customer_name")
        self.assertTrue(name_field.is_candidate_pii)
        self.assertEqual(name_field.candidate_class_id, "PID")

        user_id_field = next(f for f in fields if f.column_name == "user_id")
        self.assertFalse(user_id_field.is_candidate_pii)

    def test_sql_scanner(self):
        db_file = os.path.join(self.data_dir, "enterprise_data.db")
        self.assertTrue(os.path.exists(db_file), f"DB not found: {db_file}")
        fields = self.engine.sql_scanner.scan_sqlite(db_file)
        self.assertGreater(len(fields), 15)

        # Check employees pan_card
        pan_field = next(f for f in fields if f.table_name == "employees" and f.column_name == "pan_card")
        self.assertTrue(pan_field.is_candidate_pii)
        self.assertEqual(pan_field.candidate_class_id, "GID")

        # Check employees age
        age_field = next(f for f in fields if f.table_name == "employees" and f.column_name == "age")
        self.assertTrue(age_field.is_candidate_pii)
        self.assertEqual(age_field.candidate_class_id, "PID")

if __name__ == "__main__":
    unittest.main()
