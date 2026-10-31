"""
Unit tests for PrivLens Rule Matcher & Validators (PS-019 classes).
"""

import os
import unittest
import yaml
from privlens.scanner.rule_matcher import (
    RuleMatcher, 
    luhn_checksum, 
    valid_ipv4, 
    valid_aadhaar, 
    valid_geo_coords, 
    mask_sample_value
)

class TestRuleMatcher(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rules_path = os.path.join(os.path.dirname(__file__), "..", "config", "detection_rules.yaml")
        with open(rules_path, "r", encoding="utf-8") as f:
            cls.config = yaml.safe_load(f)
        cls.matcher = RuleMatcher(cls.config)

    def test_luhn_algorithm(self):
        valid_cc = "4532015112830366"
        self.assertTrue(luhn_checksum(valid_cc))
        invalid_cc = "4532015112830367"
        self.assertFalse(luhn_checksum(invalid_cc))

    def test_aadhaar_validation(self):
        self.assertTrue(valid_aadhaar("4532 1488 2947"))
        self.assertTrue(valid_aadhaar("802400718931"))
        self.assertFalse(valid_aadhaar("1234 5678 9012")) # starts with 1
        self.assertFalse(valid_aadhaar("12345"))           # short

    def test_geo_coords_validation(self):
        self.assertTrue(valid_geo_coords("12.971599, 77.594566"))
        self.assertTrue(valid_geo_coords("-33.8688, 151.2093"))
        self.assertFalse(valid_geo_coords("95.0, 77.0")) # lat > 90
        self.assertFalse(valid_geo_coords("invalid"))

    def test_personal_identity_matching(self):
        # Name
        names = ["Aarav Sharma", "Priya Patel", "Rohan Singh"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("customer_name", names)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "PID")

        # DOB
        dobs = ["1992-05-14", "1988-11-20", "2001-02-28"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("date_of_birth", dobs)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "PID")

    def test_contact_information_matching(self):
        emails = ["aarav@example.com", "priya.patel@corp.org", "rohan12@domain.net"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("email_address", emails)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "CNT")

    def test_government_identifiers_matching(self):
        # PAN
        pans = ["ABCDE1234F", "BKRPK9821Z", "DELPR8102Q"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("pan_number", pans)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "GID")

        # Aadhaar
        aadhaars = ["4532 1488 2947", "4916 0128 4912", "8024 0071 8931"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("aadhaar_number", aadhaars)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "GID")

    def test_financial_information_matching(self):
        upis = ["aarav@okhdfcbank", "priya22@okaxis", "rohan@paytm"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("upi_id", upis)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "FIN")

    def test_location_address_matching(self):
        pins = ["560001", "110001", "400001", "600001"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("pin_code", pins)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "LOC")

    def test_masking(self):
        self.assertEqual(mask_sample_value("aarav@example.com"), "a***v@example.com")
        self.assertEqual(mask_sample_value("4532 1488 2947"), "XXXX-XXXX-2947")
        self.assertEqual(mask_sample_value("ABCDE1234F"), "AB***4F")

if __name__ == "__main__":
    unittest.main()
