"""
SQL Database Scanner for PrivLens.
Connects to SQLite databases, inspects schema, and profiles column data.
"""

import os
import sqlite3
from typing import List, Optional
from privlens.models import DiscoveredField
from privlens.scanner.rule_matcher import RuleMatcher

class SQLScanner:
    def __init__(self, rule_matcher: RuleMatcher, sample_limit: int = 100):
        self.rule_matcher = rule_matcher
        self.sample_limit = sample_limit

    def scan_sqlite(self, db_path: str) -> List[DiscoveredField]:
        """Scans all user tables in a SQLite database file."""
        if not os.path.exists(db_path):
            print(f"[SQLScanner] Database file not found: {db_path}")
            return []

        db_name = os.path.basename(db_path)
        discovered_fields: List[DiscoveredField] = []

        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # Retrieve user tables
            cur.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%';
            """)
            tables = [row["name"] for row in cur.fetchall()]

            for tbl in tables:
                # Column info
                cur.execute(f"PRAGMA table_info(`{tbl}`);")
                cols_info = cur.fetchall()

                # Total count
                cur.execute(f"SELECT COUNT(*) as cnt FROM `{tbl}`;")
                total_rows = cur.fetchone()["cnt"]

                # Sample data
                cur.execute(f"SELECT * FROM `{tbl}` LIMIT {self.sample_limit};")
                sample_rows = cur.fetchall()

                for cinfo in cols_info:
                    col_name = cinfo["name"]
                    data_type = cinfo["type"] or "TEXT"

                    # Extract samples for this column
                    samples = [r[col_name] for r in sample_rows if r[col_name] is not None]
                    
                    # Count non-nulls in table for this column
                    cur.execute(f"SELECT COUNT(`{col_name}`) as non_null FROM `{tbl}`;")
                    non_null_count = cur.fetchone()["non_null"]

                    is_pii, class_id, class_name, confidence, evidence, previews = (
                        self.rule_matcher.evaluate_column(col_name, samples)
                    )

                    discovered_fields.append(
                        DiscoveredField(
                            source_name=db_name,
                            table_name=tbl,
                            column_name=col_name,
                            data_type=data_type,
                            total_records=total_rows,
                            non_null_records=non_null_count,
                            is_candidate_pii=is_pii,
                            candidate_class_id=class_id if is_pii else None,
                            candidate_class_name=class_name if is_pii else None,
                            confidence_score=confidence,
                            evidence_checklist=evidence,
                            sample_preview_masked=previews
                        )
                    )

            conn.close()
        except Exception as e:
            print(f"[SQLScanner] Error scanning SQLite database {db_path}: {e}")

        return discovered_fields
