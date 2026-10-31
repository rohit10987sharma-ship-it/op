"""
Data models and schemas for PrivLens PII Discovery & Privacy Governance Engine.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any

@dataclass
class EvidenceItem:
    rule_id: str
    rule_name: str
    matched_by_header: bool
    matched_by_value: bool
    sample_match_count: int
    sample_total_count: int
    match_ratio: float
    confidence_contribution: float
    details: str

@dataclass
class DiscoveredField:
    source_name: str
    table_name: Optional[str]
    column_name: str
    data_type: str
    total_records: int
    non_null_records: int
    is_candidate_pii: bool
    candidate_class_id: Optional[str]   # "IDN", "CNT", "FIN", "SEN", "NET" or None
    candidate_class_name: Optional[str] # e.g. "Direct Identifiers"
    confidence_score: float             # 0.0 to 1.0
    evidence_checklist: List[EvidenceItem] = field(default_factory=list)
    sample_preview_masked: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class GovernanceMetadata:
    registered: bool
    purpose_id: Optional[str]
    purpose_name: Optional[str]
    retention_period_months: Optional[int]
    retention_trigger: Optional[str]
    data_owner: Optional[str]
    governance_status: str  # "ACTIVE", "INCOMPLETE", "UNREGISTERED", "UNLINKED_PURPOSE"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class EvidenceGap:
    gap_type: str        # "UNREGISTERED_SHADOW_DATA", "MISSING_PURPOSE", "MISSING_RETENTION", "UNCONFIRMED_PII"
    severity: str        # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    field_identifier: str
    title: str
    description: str
    human_action_recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class InventoryItem:
    field_id: str                  # "customer_signups.csv::full_name" or "enterprise_data.db:employees::ssn"
    discovery: DiscoveredField
    governance: GovernanceMetadata
    gaps: List[EvidenceGap] = field(default_factory=list)
    
    # Explicit legal disclaimer tag (as required by prompt)
    disclaimer: str = (
        "Technical evidence observation only. Not an automated lawful-basis decision, "
        "nor an inference of universal cross-border data transfer. Requires human privacy review."
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field_id": self.field_id,
            "discovery": self.discovery.to_dict(),
            "governance": self.governance.to_dict(),
            "gaps": [g.to_dict() for g in self.gaps],
            "disclaimer": self.disclaimer
        }

@dataclass
class ClassMetric:
    class_id: str
    class_name: str
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    precision: float
    recall: float
    f1_score: float
    support: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class EvaluationSummary:
    macro_precision: float
    macro_recall: float
    macro_f1: float
    micro_precision: float
    micro_recall: float
    micro_f1: float
    total_evaluated_fields: int
    total_true_pii: int
    total_predicted_pii: int
    class_metrics: Dict[str, ClassMetric] = field(default_factory=dict)
    confusion_details: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "macro_precision": self.macro_precision,
            "macro_recall": self.macro_recall,
            "macro_f1": self.macro_f1,
            "micro_precision": self.micro_precision,
            "micro_recall": self.micro_recall,
            "micro_f1": self.micro_f1,
            "total_evaluated_fields": self.total_evaluated_fields,
            "total_true_pii": self.total_true_pii,
            "total_predicted_pii": self.total_predicted_pii,
            "class_metrics": {k: v.to_dict() for k, v in self.class_metrics.items()},
            "confusion_details": self.confusion_details
        }
