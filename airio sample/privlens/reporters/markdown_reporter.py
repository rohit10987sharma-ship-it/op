"""
Markdown Technical Report Generator for PrivLens.
Produces formatted technical evidence inventories, evidence gap analyses,
and evaluation benchmark tables.
"""

from typing import List, Optional
from privlens.models import InventoryItem, EvaluationSummary

class MarkdownReporter:
    @staticmethod
    def generate_report(
        inventory: List[InventoryItem],
        evaluation: Optional[EvaluationSummary] = None,
        output_path: Optional[str] = None
    ) -> str:
        lines = []

        lines.append("# PrivLens: Technical Privacy Evidence & Metadata Inventory Report")
        lines.append("")
        lines.append("> **IMPORTANT LEGAL BOUNDARY & EVIDENCE DISCLAIMER**  ")
        lines.append("> This report contains *technical evidence* discovered by automated heuristic profiling. ")
        lines.append("> It **does NOT** constitute a legal compliance determination, **does NOT** infer GDPR/CCPA lawful basis, ")
        lines.append("> and **does NOT** deduce universal data transfer flows. Findings are strictly formulated ")
        lines.append("> as an evidence checklist for human privacy officer review.")
        lines.append("")

        total_fields = len(inventory)
        pii_fields = [it for it in inventory if it.discovery.is_candidate_pii]
        non_pii_fields = [it for it in inventory if not it.discovery.is_candidate_pii]
        all_gaps = [gap for it in inventory for gap in it.gaps]

        # Summary KPIs
        lines.append("## 1. Executive Technical Summary")
        lines.append("")
        lines.append("| Metric | Count |")
        lines.append("| :--- | :--- |")
        lines.append(f"| **Total Fields Scanned** | `{total_fields}` |")
        lines.append(f"| **Candidate PII Fields Discovered** | `{len(pii_fields)}` |")
        lines.append(f"| **Non-PII Technical Columns** | `{len(non_pii_fields)}` |")
        lines.append(f"| **Identified Governance & Evidence Gaps** | `{len(all_gaps)}` |")
        lines.append("")

        # 5 Data Classes Summary
        lines.append("### Distribution Across 5 Predefined Data Classes")
        lines.append("")
        class_counts = {}
        for it in pii_fields:
            cname = it.discovery.candidate_class_name or "Unknown"
            class_counts[cname] = class_counts.get(cname, 0) + 1

        lines.append("| Predefined Data Class | Candidate Fields Discovered |")
        lines.append("| :--- | :--- |")
        for cname, count in sorted(class_counts.items()):
            lines.append(f"| **{cname}** | {count} |")
        lines.append("")

        # Technical Evidence Inventory Table
        lines.append("## 2. Structured Technical Evidence Inventory")
        lines.append("")
        lines.append("| Target Field | Discovered Class | Confidence | Declared Purpose | Retention Period | Governance Status |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for it in pii_fields:
            d = it.discovery
            g = it.governance
            target = f"`{d.source_name}`" + (f" (`{d.table_name}`)" if d.table_name else "") + f" : **{d.column_name}**"
            cname = d.candidate_class_name or "N/A"
            conf = f"{d.confidence_score:.0%}"
            purp = g.purpose_name if g.purpose_name else "*(Missing Purpose)*"
            ret = f"{g.retention_period_months} months ({g.retention_trigger})" if g.retention_period_months else "*(Missing Retention)*"
            status = g.governance_status
            lines.append(f"| {target} | {cname} | `{conf}` | {purp} | {ret} | `{status}` |")
        lines.append("")

        # Evidence Gaps & Missing Metadata
        lines.append("## 3. Evidence Gaps & Missing Metadata Action Checklist")
        lines.append("")
        if not all_gaps:
            lines.append("No governance evidence gaps detected across scanned assets.")
        else:
            lines.append("| Severity | Target Field | Gap Type | Description & Human Recommendation |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for gap in sorted(all_gaps, key=lambda x: (x.severity != "CRITICAL", x.severity != "HIGH")):
                sev_badge = f"**{gap.severity}**"
                lines.append(
                    f"| {sev_badge} | `{gap.field_identifier}` | `{gap.gap_type}` | "
                    f"**{gap.title}**: {gap.description}<br>↳ *Action:* {gap.human_action_recommendation} |"
                )
        lines.append("")

        # Benchmark Precision & Recall Evaluation
        if evaluation:
            lines.append("## 4. Benchmark Precision & Recall Evaluation")
            lines.append("")
            lines.append(f"- **Evaluated Fields against Ground Truth**: `{evaluation.total_evaluated_fields}`")
            lines.append(f"- **Macro Precision**: `{evaluation.macro_precision:.2%}` | **Macro Recall**: `{evaluation.macro_recall:.2%}` | **Macro F1**: `{evaluation.macro_f1:.2%}`")
            lines.append(f"- **Micro Precision**: `{evaluation.micro_precision:.2%}` | **Micro Recall**: `{evaluation.micro_recall:.2%}` | **Micro F1**: `{evaluation.micro_f1:.2%}`")
            lines.append("")
            lines.append("### Per-Class Evaluation Metrics")
            lines.append("")
            lines.append("| Class Code | Data Class Name | Support (True) | TP | FP | FN | Precision | Recall | F1-Score |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            for cid, m in evaluation.class_metrics.items():
                lines.append(
                    f"| `{m.class_id}` | {m.class_name} | {m.support} | {m.true_positives} | "
                    f"{m.false_positives} | {m.false_negatives} | `{m.precision:.2%}` | `{m.recall:.2%}` | `**{m.f1_score:.2%}**` |"
                )
            lines.append("")

        content = "\n".join(lines)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

        return content
