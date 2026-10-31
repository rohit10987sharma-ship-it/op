"""
Governance Metadata Mapper & Evidence Gap Analyzer.
Links discovered technical fields to declared purposes and retention policies.
Flags governance gaps for human privacy steward review.
"""

import yaml
from typing import List, Dict, Any, Optional
from privlens.models import (
    DiscoveredField, 
    GovernanceMetadata, 
    EvidenceGap, 
    InventoryItem
)

class GovernanceMapper:
    def __init__(self, registry_config_path: str):
        self.registry_config_path = registry_config_path
        self.config = self._load_config(registry_config_path)
        self.purposes = {p["purpose_id"]: p for p in self.config.get("purposes", [])}
        self.registered_fields = self.config.get("registered_fields", {})

    def _load_config(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _get_target_key(self, field: DiscoveredField) -> str:
        """Constructs registry key e.g. 'customer_signups.csv' or 'enterprise_data.db:employees'"""
        if field.table_name:
            return f"{field.source_name}:{field.table_name}"
        return field.source_name

    def map_field(self, field: DiscoveredField) -> InventoryItem:
        """Links a discovered field with governance metadata and evaluates compliance evidence gaps."""
        target_key = self._get_target_key(field)
        field_id = f"{target_key}::{field.column_name}"
        
        target_registry = self.registered_fields.get(target_key, {})
        col_reg = target_registry.get(field.column_name)

        gaps: List[EvidenceGap] = []

        if col_reg is None:
            # Not in registry
            gov = GovernanceMetadata(
                registered=False,
                purpose_id=None,
                purpose_name=None,
                retention_period_months=None,
                retention_trigger=None,
                data_owner=None,
                governance_status="UNREGISTERED"
            )
            
            # If technical scanner discovered candidate PII, this is an Unregistered Shadow Data gap!
            if field.is_candidate_pii:
                gaps.append(
                    EvidenceGap(
                        gap_type="UNREGISTERED_SHADOW_DATA",
                        severity="CRITICAL",
                        field_identifier=field_id,
                        title=f"Unregistered Candidate PII in {target_key}",
                        description=(
                            f"Field '{field.column_name}' was identified as candidate personal data "
                            f"({field.candidate_class_name}, confidence: {field.confidence_score:.0%}) "
                            f"across {field.non_null_records} records, but has NO entry in the governance registry."
                        ),
                        human_action_recommendation=(
                            "Human Review Required: Consult data owner to verify business necessity. "
                            "If legitimate, register processing purpose and retention policy in RoPA. "
                            "If obsolete, initiate data minimization or decommissioning."
                        )
                    )
                )
        else:
            # Field exists in registry
            purpose_id = col_reg.get("purpose_id")
            purpose_info = self.purposes.get(purpose_id) if purpose_id else None
            purpose_name = purpose_info.get("name") if purpose_info else None
            retention_months = col_reg.get("retention_period_months")
            retention_trigger = col_reg.get("retention_trigger")
            data_owner = col_reg.get("data_owner")
            status = col_reg.get("status", "ACTIVE")

            gov = GovernanceMetadata(
                registered=True,
                purpose_id=purpose_id,
                purpose_name=purpose_name,
                retention_period_months=retention_months,
                retention_trigger=retention_trigger,
                data_owner=data_owner,
                governance_status=status
            )

            # Check gaps for candidate PII
            if field.is_candidate_pii:
                # 1. Check Missing Purpose
                if not purpose_id:
                    gaps.append(
                        EvidenceGap(
                            gap_type="MISSING_PURPOSE",
                            severity="HIGH",
                            field_identifier=field_id,
                            title=f"Missing Declared Purpose for {field.column_name}",
                            description=(
                                f"Field '{field.column_name}' is registered under {target_key} "
                                f"but has no declared business processing purpose."
                            ),
                            human_action_recommendation=(
                                "Privacy Steward Action: Assign and validate a declared business purpose "
                                "prior to lawful processing verification."
                            )
                        )
                    )

                # 2. Check Missing Retention Schedule
                if retention_months is None or retention_months <= 0:
                    gaps.append(
                        EvidenceGap(
                            gap_type="MISSING_RETENTION",
                            severity="HIGH",
                            field_identifier=field_id,
                            title=f"Missing Retention Schedule for {field.column_name}",
                            description=(
                                f"Field '{field.column_name}' contains candidate personal data "
                                f"without a defined retention limit or deletion trigger."
                            ),
                            human_action_recommendation=(
                                "Data Governance Action: Formulate data retention schedule and disposal "
                                "trigger in accordance with corporate data retention policy."
                            )
                        )
                    )

        return InventoryItem(
            field_id=field_id,
            discovery=field,
            governance=gov,
            gaps=gaps
        )

    def map_all(self, fields: List[DiscoveredField]) -> List[InventoryItem]:
        """Maps an entire list of discovered fields into a full governance inventory."""
        return [self.map_field(f) for f in fields]
