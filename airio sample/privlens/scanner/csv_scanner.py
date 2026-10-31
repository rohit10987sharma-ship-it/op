"""
CSV Scanner for PrivLens.
Discovers and profiles columns in CSV files.
"""

import os
import pandas as pd
from typing import List
from privlens.models import DiscoveredField
from privlens.scanner.rule_matcher import RuleMatcher

class CSVScanner:
    def __init__(self, rule_matcher: RuleMatcher, sample_limit: int = 100):
        self.rule_matcher = rule_matcher
        self.sample_limit = sample_limit

    def scan_file(self, file_path: str) -> List[DiscoveredField]:
        """Scans a single CSV file and profiles each column."""
        file_name = os.path.basename(file_path)
        try:
            df = pd.read_csv(file_path, low_memory=False)
        except Exception as e:
            print(f"[CSVScanner] Error reading {file_path}: {e}")
            return []

        total_rows = len(df)
        discovered_fields: List[DiscoveredField] = []

        for col in df.columns:
            series = df[col]
            non_null = int(series.count())
            data_type = str(series.dtype)
            
            # Sample non-null values
            sample_series = series.dropna().head(self.sample_limit)
            samples = sample_series.tolist()

            is_pii, class_id, class_name, confidence, evidence, previews = (
                self.rule_matcher.evaluate_column(str(col), samples)
            )

            discovered_fields.append(
                DiscoveredField(
                    source_name=file_name,
                    table_name=None,
                    column_name=str(col),
                    data_type=data_type,
                    total_records=total_rows,
                    non_null_records=non_null,
                    is_candidate_pii=is_pii,
                    candidate_class_id=class_id if is_pii else None,
                    candidate_class_name=class_name if is_pii else None,
                    confidence_score=confidence,
                    evidence_checklist=evidence,
                    sample_preview_masked=previews
                )
            )

        return discovered_fields

    def scan_directory(self, dir_path: str) -> List[DiscoveredField]:
        """Scans all CSV files in a given directory."""
        results: List[DiscoveredField] = []
        if not os.path.exists(dir_path):
            return results
        for root, _, files in os.walk(dir_path):
            for file in sorted(files):
                if file.lower().endswith(".csv"):
                    full_path = os.path.join(root, file)
                    results.extend(self.scan_file(full_path))
        return results
