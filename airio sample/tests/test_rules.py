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
        # 1. Name
        names = ["Aarav Sharma", "Priya Patel", "Rohan Singh", "Sneha Gupta"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("customer_name", names)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "PID")

        # 2. Date of Birth
        dobs = ["1992-05-14", "1988-11-20", "2001-02-28", "1975-09-12"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("date_of_birth", dobs)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "PID")

        # 3. Gender
        genders = ["Male", "Female", "Non-Binary", "Female", "Male"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("gender", genders)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "PID")

        # 4. Age
        ages = ["25", "42", "31", "19", "58"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("age", ages)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "PID")

    def test_contact_information_matching(self):
        # 1. Email address
        emails = ["aarav@example.com", "priya.patel@corp.org", "rohan12@domain.net"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("email_address", emails)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "CNT")

        # 2. Phone number
        phones = ["+91-9876543210", "+91-8765432109", "9123456780", "+1-555-234-5678"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("phone_number", phones)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "CNT")

    def test_government_identifiers_matching(self):
        # 1. Aadhaar
        aadhaars = ["4532 1488 2947", "4916 0128 4912", "8024 0071 8931"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("aadhaar_number", aadhaars)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "GID")

        # 2. PAN
        pans = ["ABCDE1234F", "BKRPK9821Z", "DELPR8102Q"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("pan_number", pans)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "GID")

        # 3. Passport
        passports = ["A1234567", "Z9876543", "P2345678", "M8765432"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("passport_number", passports)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "GID")

        # 4. Voter ID
        voter_ids = ["ABC1234567", "XYZ9876543", "KLM2345678", "PQR8765432"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("voter_id", voter_ids)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "GID")

        # 5. Driving Licence
        dls = ["DL-0420180012345", "MH-1220150098765", "KA-0120200054321", "TN-0720190087654"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("driving_licence", dls)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "GID")

    def test_financial_information_matching(self):
        # 1. Bank account number
        accounts = ["123456789012", "987654321098", "567890123456", "432109876543"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("bank_account_number", accounts)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "FIN")

        # 2. IFSC
        ifscs = ["HDFC0001234", "SBIN0000456", "ICIC0009876", "UTIB0002345"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("ifsc_code", ifscs)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "FIN")

        # 3. Card number
        cards = ["4532-0151-1283-0366", "4532 0151 1283 0366", "4532015112830366", "4532-0151-1283-0366"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("card_number", cards)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "FIN")

        # 4. UPI ID
        upis = ["aarav@okhdfcbank", "priya22@okaxis", "rohan@paytm"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("upi_id", upis)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "FIN")

    def test_location_address_matching(self):
        # 1. Postal address
        addresses = ["123 MG Road, Sector 5", "45 Park Street, Indiranagar", "789 Brigade Road, Colony"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("residential_address", addresses)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "LOC")

        # 2. PIN code
        pins = ["560001", "110001", "400001", "600001"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("pin_code", pins)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "LOC")

        # 3. Geo coordinates
        coords = ["12.971599, 77.594566", "28.613939, 77.209023", "19.076090, 72.877426"]
        is_pi, cid, cname, conf, ev, prev = self.matcher.evaluate_column("geo_coordinates", coords)
        self.assertTrue(is_pi)
        self.assertEqual(cid, "LOC")

    def test_masking(self):
        self.assertEqual(mask_sample_value("aarav@example.com"), "a***v@example.com")
        self.assertEqual(mask_sample_value("4532 1488 2947"), "XXXX-XXXX-2947")
        self.assertEqual(mask_sample_value("ABCDE1234F"), "AB***4F")

if __name__ == "__main__":
    unittest.main()
