"""
JSON Reporter for PrivLens.
Serializes scan inventories, evidence gaps, and evaluation metrics.
"""

import json
from typing import List, Dict, Any, Optional
from privlens.models import InventoryItem, EvaluationSummary

class JSONReporter:
    @staticmethod
    def generate_report(
        inventory: List[InventoryItem], 
        evaluation: Optional[EvaluationSummary] = None,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generates structured JSON data and optionally writes to file."""
        report = {
            "metadata": {
                "tool": "PrivLens PII Discovery & Privacy Evidence Inventory Engine",
                "version": "1.0.0",
                "disclaimer": (
                    "Technical evidence observation only. Not an automated lawful-basis decision, "
                    "nor an inference of universal cross-border data transfer. Requires human privacy review."
                ),
                "total_fields_scanned": len(inventory),
                "total_candidate_pii_fields": sum(1 for item in inventory if item.discovery.is_candidate_pii),
                "total_evidence_gaps": sum(len(item.gaps) for item in inventory)
            },
            "inventory": [item.to_dict() for item in inventory],
            "evaluation": evaluation.to_dict() if evaluation else None
        }

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)

        return report
