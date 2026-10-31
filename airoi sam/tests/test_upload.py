"""
Unit tests for File Upload and Scanning API.
"""

import os
import io
import sqlite3
import unittest
from web.app import app
import datasets.generate_datasets as g

class TestUploadAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_upload_csv(self):
        csv_content = (
            "user_id,full_name,contact_email\n"
            "1,Alice Green,alice@example.com\n"
            "2,Bob White,bob@example.com\n"
            "3,Charlie Black,charlie@example.com\n"
            "4,Diana Blue,diana@example.com\n"
        )
        data = {
            "files": (io.BytesIO(csv_content.encode("utf-8")), "unit_test_leads.csv"),
            "mode": "append"
        }
        res = self.client.post("/api/upload-and-scan", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["new_pii_detected"], 2) # full_name and contact_email

    def test_upload_sqlite_db(self):
        # Create in-memory SQLite DB
        db_path = "temp_unit_test.db"
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("CREATE TABLE accounts (acc_id INT, card_num TEXT, upi_vpa TEXT)")
        for i in range(1, 6):
            cur.execute("INSERT INTO accounts VALUES (?, ?, ?)", (i, g.random_luhn_credit_card(), f"user{i}@okhdfcbank"))
        conn.commit()
        conn.close()

        with open(db_path, "rb") as f:
            db_bytes = f.read()
        os.remove(db_path)

        data = {
            "files": (io.BytesIO(db_bytes), "unit_test_accounts.db"),
            "mode": "append"
        }
        res = self.client.post("/api/upload-and-scan", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["new_pii_detected"], 2) # card_num and upi_vpa

    def test_upload_invalid_extension(self):
        data = {
            "files": (io.BytesIO(b"malicious content"), "executable.exe"),
            "mode": "append"
        }
        res = self.client.post("/api/upload-and-scan", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 400)
        self.assertIn("Unsupported file type", res.get_json()["error"])

if __name__ == "__main__":
    unittest.main()
