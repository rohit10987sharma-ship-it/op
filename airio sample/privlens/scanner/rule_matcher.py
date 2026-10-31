"""
Rule Matcher and Evidence Profiler for PrivLens.
Applies regex heuristics, checksum validators (Luhn), and sample profiling
to build technical evidence for candidate PII fields.
"""

import re
import ipaddress
from typing import List, Dict, Tuple, Optional, Any
from privlens.models import EvidenceItem

def luhn_checksum(val: str) -> bool:
    """Validates credit card number with Luhn algorithm."""
    clean = re.sub(r"[\s-]", "", str(val))
    if not clean.isdigit() or len(clean) < 13 or len(clean) > 19:
        return False
    digits = [int(d) for d in clean]
    total = 0
    for idx, d in enumerate(reversed(digits)):
        if idx % 2 == 1:
            doubled = d * 2
            total += (doubled - 9) if doubled > 9 else doubled
        else:
            total += d
    return total % 10 == 0

def valid_ipv4(val: str) -> bool:
    """Validates IPv4 address string."""
    clean = str(val).strip()
    try:
        ip = ipaddress.IPv4Address(clean)
        return not (ip.is_multicast or ip.is_loopback)
    except Exception:
        return False

def valid_aadhaar(val: str) -> bool:
    """Validates 12-digit Aadhaar number (first digit cannot be 0 or 1)."""
    clean = re.sub(r"[\s-]", "", str(val))
    if not clean.isdigit() or len(clean) != 12:
        return False
    if clean[0] in ("0", "1"):
        return False
    return True

def valid_geo_coords(val: str) -> bool:
    """Validates Lat, Long coordinates within -90..90 and -180..180."""
    clean = str(val).strip()
    parts = clean.split(",")
    if len(parts) != 2:
        return False
    try:
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0
    except Exception:
        return False

def mask_sample_value(val: Any) -> str:
    """Masks personal data for safe presentation in evidence review."""
    s = str(val).strip()
    if not s:
        return ""
    if "@" in s:
        parts = s.split("@", 1)
        prefix = parts[0]
        masked_prefix = prefix[0] + "***" + (prefix[-1] if len(prefix) > 1 else "")
        return f"{masked_prefix}@{parts[1]}"
    if re.match(r"^[2-9]\d{3}\s?\d{4}\s?\d{4}$", s): # Aadhaar
        clean = re.sub(r"[\s-]", "", s)
        return f"XXXX-XXXX-{clean[-4:]}"
    if re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", s): # PAN
        return f"{s[:2]}***{s[-2:]}"
    if re.match(r"^\d{3}-\d{2}-\d{4}$", s): # SSN
        return f"***-**-{s[-4:]}"
    if len(s) >= 12 and any(c.isdigit() for c in s): # Card or IBAN
        return f"{s[:4]}-****-****-{s[-4:]}"
    if len(s) > 4:
        return f"{s[:2]}***{s[-2:]}"
    return "***"


class RuleMatcher:
    def __init__(self, rules_config: Dict[str, Any]):
        self.config = rules_config
        self.rules = rules_config.get("rules", [])
        self.thresholds = rules_config.get("thresholds", {})
        self.data_classes = {dc["id"]: dc for dc in rules_config.get("data_classes", [])}
        
        # Precompile regexes for performance
        self.compiled_rules = []
        for r in self.rules:
            header_regs = [re.compile(p, re.IGNORECASE) for p in r.get("header_patterns", [])]
            value_regs = [re.compile(p) for p in r.get("value_patterns", [])]
            self.compiled_rules.append({
                "def": r,
                "header_regs": header_regs,
                "value_regs": value_regs,
                "validator": r.get("validator")
            })

    def evaluate_column(
        self, 
        column_name: str, 
        samples: List[Any]
    ) -> Tuple[bool, Optional[str], Optional[str], float, List[EvidenceItem], List[str]]:
        """
        Evaluates a column against all configured detection rules.
        Returns:
            (is_pii, class_id, class_name, confidence_score, evidence_checklist, sample_previews)
        """
        non_empty_samples = [str(s).strip() for s in samples if s is not None and str(s).strip() != ""]
        sample_count = len(non_empty_samples)
        
        min_non_empty = self.thresholds.get("min_non_empty_values", 3)
        if sample_count < min_non_empty:
            # Insufficient samples to profile reliably
            return False, None, None, 0.0, [], []

        evidence_list: List[EvidenceItem] = []
        candidate_classes: Dict[str, float] = {}

        for cr in self.compiled_rules:
            rdef = cr["def"]
            rule_id = rdef["rule_id"]
            class_id = rdef["class_id"]
            rule_name = rdef["name"]
            
            # 1. Header match check
            header_matched = any(reg.search(column_name) for reg in cr["header_regs"])
            
            # 2. Value pattern matches
            value_matches = 0
            for val in non_empty_samples:
                # Check regex
                reg_match = any(vreg.search(val) for vreg in cr["value_regs"])
                if reg_match:
                    # Check custom validator if specified
                    validator_ok = True
                    if cr["validator"] == "luhn_checksum":
                        validator_ok = luhn_checksum(val)
                    elif cr["validator"] == "valid_ipv4":
                        validator_ok = valid_ipv4(val)
                    elif cr["validator"] == "valid_aadhaar":
                        validator_ok = valid_aadhaar(val)
                    elif cr["validator"] == "valid_geo_coords":
                        validator_ok = valid_geo_coords(val)
                    
                    if validator_ok:
                        value_matches += 1

            match_ratio = value_matches / sample_count if sample_count > 0 else 0.0
            min_ratio = rdef.get("min_sample_match_ratio", 0.35)
            value_matched = match_ratio >= min_ratio

            # Calculate rule score
            header_weight = rdef.get("header_weight", 0.40)
            value_weight = rdef.get("value_weight", 0.60)

            score = 0.0
            if header_matched and value_matched:
                score = header_weight + (value_weight * match_ratio)
            elif header_matched and match_ratio >= 0.10:
                score = (header_weight * 0.90) + (value_weight * match_ratio)
            elif header_matched:
                score = header_weight * 0.70
            elif value_matched:
                score = value_weight * match_ratio

            score = min(1.0, round(score, 3))

            if score >= 0.35: # Sufficient technical evidence trigger
                details = (
                    f"Rule: {rule_name} | Header Pattern Match: {header_matched} | "
                    f"Sample Match: {value_matches}/{sample_count} ({match_ratio:.1%})"
                )
                if cr["validator"]:
                    details += f" | Checksum Validator ({cr['validator']}): Verified"

                evidence = EvidenceItem(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    matched_by_header=header_matched,
                    matched_by_value=value_matched,
                    sample_match_count=value_matches,
                    sample_total_count=sample_count,
                    match_ratio=round(match_ratio, 3),
                    confidence_contribution=score,
                    details=details
                )
                evidence_list.append(evidence)
                candidate_classes[class_id] = max(candidate_classes.get(class_id, 0.0), score)

        cutoff = self.thresholds.get("classification_confidence_cutoff", 0.50)
        
        # Pick best class if multiple rules matched
        if candidate_classes:
            best_class_id = max(candidate_classes.items(), key=lambda x: x[1])[0]
            best_score = candidate_classes[best_class_id]
            
            if best_score >= cutoff:
                best_class_name = self.data_classes.get(best_class_id, {}).get("name", best_class_id)
                # Generate masked preview of first few samples
                preview = [mask_sample_value(s) for s in non_empty_samples[:4]]
                return True, best_class_id, best_class_name, best_score, evidence_list, preview

        # If low confidence or no rule triggered
        if evidence_list:
            # Low confidence finding
            best_class_id = max(candidate_classes.items(), key=lambda x: x[1])[0]
            best_score = candidate_classes[best_class_id]
            best_class_name = self.data_classes.get(best_class_id, {}).get("name", best_class_id)
            preview = [mask_sample_value(s) for s in non_empty_samples[:3]]
            return False, best_class_id, best_class_name, best_score, evidence_list, preview

        return False, None, None, 0.0, [], []
