"""
PrivLens Core Scanner Engine.
Orchestrates CSV and SQL scanning using configured detection rules.
"""

import os
import yaml
from typing import List, Dict, Any, Optional
from privlens.models import DiscoveredField
from privlens.scanner.rule_matcher import RuleMatcher
from privlens.scanner.csv_scanner import CSVScanner
from privlens.scanner.sql_scanner import SQLScanner

class ScannerEngine:
    def __init__(self, rules_config_path: str):
        self.rules_config_path = rules_config_path
        self.config = self._load_config(rules_config_path)
        self.rule_matcher = RuleMatcher(self.config)
        sample_limit = self.config.get("thresholds", {}).get("sample_size_per_column", 100)
        self.csv_scanner = CSVScanner(self.rule_matcher, sample_limit=sample_limit)
        self.sql_scanner = SQLScanner(self.rule_matcher, sample_limit=sample_limit)

    def _load_config(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_data_classes(self) -> List[Dict[str, Any]]:
        return self.config.get("data_classes", [])

    def get_rules(self) -> List[Dict[str, Any]]:
        return self.config.get("rules", [])

    def scan_path(self, target_path: str) -> List[DiscoveredField]:
        """Scans a file or directory based on its type."""
        results: List[DiscoveredField] = []
        if os.path.isfile(target_path):
            if target_path.lower().endswith(".csv"):
                results.extend(self.csv_scanner.scan_file(target_path))
            elif target_path.lower().endswith((".db", ".sqlite", ".sqlite3")):
                results.extend(self.sql_scanner.scan_sqlite(target_path))
        elif os.path.isdir(target_path):
            # Scan CSVs
            results.extend(self.csv_scanner.scan_directory(target_path))
            # Scan any sqlite databases inside
            for root, _, files in os.walk(target_path):
                for f in files:
                    if f.lower().endswith((".db", ".sqlite", ".sqlite3")):
                        db_p = os.path.join(root, f)
                        results.extend(self.sql_scanner.scan_sqlite(db_p))
        return results

    def scan_targets(self, targets: List[str]) -> List[DiscoveredField]:
        """Scans multiple specified targets."""
        all_results: List[DiscoveredField] = []
        for target in targets:
            all_results.extend(self.scan_path(target))
        return all_results
