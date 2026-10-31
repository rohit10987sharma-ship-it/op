"""
Unit tests for Governance Mapping and Evidence Gap flagging.
"""

import os
import unittest
from privlens.scanner.engine import ScannerEngine
from privlens.governance.mapper import GovernanceMapper

class TestGovernance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.rules_path = os.path.join(base_dir, "config", "detection_rules.yaml")
        cls.gov_path = os.path.join(base_dir, "config", "governance_registry.yaml")
        cls.data_dir = os.path.join(base_dir, "datasets", "synthetic")
        
        cls.engine = ScannerEngine(cls.rules_path)
        cls.mapper = GovernanceMapper(cls.gov_path)

    def test_governance_mapping_and_gaps(self):
        csv_file = os.path.join(self.data_dir, "customer_signups.csv")
        fields = self.engine.csv_scanner.scan_file(csv_file)
        inventory = self.mapper.map_all(fields)

        # Check customer_name (should be ACTIVE)
        name_item = next(it for it in inventory if it.discovery.column_name == "customer_name")
        self.assertEqual(name_item.governance.governance_status, "ACTIVE")
        self.assertEqual(len(name_item.gaps), 0)

        # Check residential_address (should have MISSING_RETENTION gap)
        addr_item = next(it for it in inventory if it.discovery.column_name == "residential_address")
        self.assertEqual(addr_item.governance.governance_status, "INCOMPLETE")
        self.assertTrue(any(g.gap_type == "MISSING_RETENTION" for g in addr_item.gaps))

        # Check date_of_birth (unregistered shadow data)
        dob_item = next(it for it in inventory if it.discovery.column_name == "date_of_birth")
        self.assertEqual(dob_item.governance.governance_status, "UNREGISTERED")
        self.assertTrue(any(g.gap_type == "UNREGISTERED_SHADOW_DATA" for g in dob_item.gaps))

if __name__ == "__main__":
    unittest.main()
