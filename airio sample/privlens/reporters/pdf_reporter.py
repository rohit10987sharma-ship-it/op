"""
PDF Technical Report Generator for PrivLens.
Produces high-quality executive and technical audit reports using ReportLab.
"""

import os
from datetime import datetime
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from reportlab.pdfgen import canvas

from privlens.models import InventoryItem, EvaluationSummary


def xml_escape(text: str) -> str:
    """Escapes XML entities for ReportLab Paragraph markup."""
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b")) # Slate 500

        # Running header on pages 2+
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "PrivLens • Technical Privacy Evidence & Metadata Inventory Report")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Footer on all pages
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 45, letter[0] - 54, 45)

        footer_text = "CONFIDENTIAL PRIVACY AUDIT • TECHNICAL DISCOVERY EVIDENCE (NON-LEGAL DETERMINATION)"
        self.drawString(54, 32, footer_text)
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(letter[0] - 54, 32, page_str)
        self.restoreState()


class PDFReporter:
    @staticmethod
    def generate_report(
        inventory: List[InventoryItem],
        evaluation: Optional[EvaluationSummary] = None,
        output_path: str = "reports/inventory_report.pdf"
    ) -> str:
        """Builds a formatted PDF report and writes to output_path."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()

        # Custom Palette
        c_primary = colors.HexColor("#0f172a")    # Slate 900
        c_brand = colors.HexColor("#0284c7")      # Sky 600
        c_dark = colors.HexColor("#1e293b")       # Slate 800
        c_border = colors.HexColor("#cbd5e1")     # Slate 300
        c_bg_light = colors.HexColor("#f8fafc")   # Slate 50
        c_text = colors.HexColor("#334155")       # Slate 700

        # Custom Typography
        style_title = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=c_primary,
            spaceAfter=4
        )

        style_subtitle = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=c_brand,
            spaceAfter=12
        )

        style_h1 = ParagraphStyle(
            "Heading1_Custom",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=c_dark,
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=True
        )

        style_h2 = ParagraphStyle(
            "Heading2_Custom",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=c_primary,
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True
        )

        style_body = ParagraphStyle(
            "Body_Custom",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11.5,
            textColor=c_text
        )

        style_meta = ParagraphStyle(
            "Meta_Custom",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#64748b")
        )

        style_table_header = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.white
        )

        style_table_cell = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=9.5,
            textColor=c_dark
        )

        style_table_cell_bold = ParagraphStyle(
            "TableCellBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9.5,
            textColor=c_primary
        )

        style_table_cell_code = ParagraphStyle(
            "TableCellCode",
            parent=styles["Normal"],
            fontName="Courier",
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#0369a1")
        )

        elements = []

        # Header Title
        elements.append(Paragraph("PrivLens: Privacy Evidence & Metadata Inventory", style_title))
        now_str = datetime.now().strftime("%B %d, %Y • %H:%M UTC")
        elements.append(Paragraph(f"Empirical PII Discovery, RoPA Governance Audit & Benchmark Report | Generated: {now_str}", style_subtitle))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=c_brand, spaceBefore=0, spaceAfter=10))

        # Legal Disclaimer Callout Box
        disclaimer_text = (
            "<b>LEGAL BOUNDARY & AUDIT NOTICE:</b> This technical report was compiled through automated "
            "syntactic discovery and column profiling. It represents factual technical evidence intended for "
            "privacy steward and DPO review. It <b>does NOT</b> constitute an automated lawful-basis decision "
            "under GDPR/CCPA, nor does it deduce universal cross-border transfer topologies."
        )
        p_disc = Paragraph(disclaimer_text, style_body)
        t_disc = Table([[p_disc]], colWidths=[letter[0] - 108])
        t_disc.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff6ff")), # Blue 50
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#93c5fd")),     # Blue 300
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(t_disc)
        elements.append(Spacer(1, 10))

        # 1. Executive Summary KPIs
        elements.append(Paragraph("1. Executive Technical Summary", style_h1))

        total_fields = len(inventory)
        pii_fields = [it for it in inventory if it.discovery.is_candidate_pii]
        non_pii_fields = [it for it in inventory if not it.discovery.is_candidate_pii]
        all_gaps = [gap for it in inventory for gap in it.gaps]

        kpi_data = [
            [
                Paragraph("<b>Metric Name</b>", style_table_header),
                Paragraph("<b>Count / Value</b>", style_table_header),
                Paragraph("<b>Context & Classification Scope</b>", style_table_header)
            ],
            [
                Paragraph("Total Fields Scanned", style_table_cell_bold),
                Paragraph(str(total_fields), style_table_cell_bold),
                Paragraph("Structured CSV spreadsheets and SQLite database tables", style_table_cell)
            ],
            [
                Paragraph("Candidate PII Discovered", style_table_cell_bold),
                Paragraph(str(len(pii_fields)), style_table_cell_bold),
                Paragraph("Personal data fields across 5 predefined data classes", style_table_cell)
            ],
            [
                Paragraph("Non-PII Columns", style_table_cell),
                Paragraph(str(len(non_pii_fields)), style_table_cell),
                Paragraph("Technical keys, surrogate IDs, timestamps, status flags", style_table_cell)
            ],
            [
                Paragraph("Governance & Evidence Gaps", style_table_cell_bold),
                Paragraph(f"<font color='#dc2626'><b>{len(all_gaps)}</b></font>", style_table_cell_bold),
                Paragraph("Unregistered shadow data, missing purposes, or missing retention", style_table_cell)
            ]
        ]
        t_kpi = Table(kpi_data, colWidths=[150, 80, letter[0] - 108 - 230])
        t_kpi.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), c_dark),
            ("GRID", (0, 0), (-1, -1), 0.5, c_border),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_bg_light]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_kpi)
        elements.append(Spacer(1, 10))

        # 5 Predefined Data Classes Breakdown
        elements.append(Paragraph("Distribution Across 5 Predefined Data Classes", style_h2))
        class_counts = {}
        for it in pii_fields:
            cname = it.discovery.candidate_class_name or "Unknown"
            class_counts[cname] = class_counts.get(cname, 0) + 1

        dist_data = [
            [
                Paragraph("<b>Data Class Name</b>", style_table_header),
                Paragraph("<b>Candidate Fields</b>", style_table_header),
                Paragraph("<b>Scope & Subtypes Observed</b>", style_table_header)
            ],
            [
                Paragraph("Personal identity (PID)", style_table_cell_bold),
                Paragraph(str(class_counts.get("Personal identity", 0)), style_table_cell),
                Paragraph("Name, date of birth, gender, age", style_table_cell)
            ],
            [
                Paragraph("Contact information (CNT)", style_table_cell_bold),
                Paragraph(str(class_counts.get("Contact information", 0)), style_table_cell),
                Paragraph("Email address, phone number", style_table_cell)
            ],
            [
                Paragraph("Government identifiers (GID)", style_table_cell_bold),
                Paragraph(str(class_counts.get("Government identifiers", 0)), style_table_cell),
                Paragraph("Aadhaar, PAN, passport, voter ID, driving licence", style_table_cell)
            ],
            [
                Paragraph("Financial information (FIN)", style_table_cell_bold),
                Paragraph(str(class_counts.get("Financial information", 0)), style_table_cell),
                Paragraph("Bank account number, IFSC, card number, UPI ID", style_table_cell)
            ],
            [
                Paragraph("Location / address (LOC)", style_table_cell_bold),
                Paragraph(str(class_counts.get("Location / address", 0)), style_table_cell),
                Paragraph("Postal address, PIN code, geo-coordinates", style_table_cell)
            ]
        ]
        t_dist = Table(dist_data, colWidths=[180, 90, letter[0] - 108 - 270])
        t_dist.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0369a1")), # Sky 700
            ("GRID", (0, 0), (-1, -1), 0.5, c_border),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_bg_light]),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        elements.append(t_dist)
        elements.append(Spacer(1, 14))

        # 2. Structured Technical Evidence Inventory Table
        elements.append(Paragraph("2. Structured Technical Evidence Inventory", style_h1))
        inv_headers = [
            Paragraph("<b>Target Asset / Column</b>", style_table_header),
            Paragraph("<b>Discovered Class</b>", style_table_header),
            Paragraph("<b>Conf.</b>", style_table_header),
            Paragraph("<b>Declared RoPA Purpose</b>", style_table_header),
            Paragraph("<b>Retention</b>", style_table_header),
            Paragraph("<b>Status</b>", style_table_header)
        ]

        inv_rows = [inv_headers]
        for it in pii_fields:
            d = it.discovery
            g = it.governance
            src_lbl = xml_escape(d.source_name)
            tbl_lbl = f" ({xml_escape(d.table_name)})" if d.table_name else ""
            col_lbl = xml_escape(d.column_name)
            target = f"{src_lbl}{tbl_lbl}<br/><b>{col_lbl}</b>"
            cname = xml_escape(d.candidate_class_name or "Unknown")
            conf = f"{d.confidence_score:.0%}"
            purp = xml_escape(g.purpose_name) if g.purpose_name else "<font color='#dc2626'><i>Missing Purpose</i></font>"
            ret = f"{g.retention_period_months}m ({xml_escape(g.retention_trigger)})" if g.retention_period_months else "<font color='#b45309'><i>Missing</i></font>"
            
            status_color = "#16a34a" if g.governance_status == "ACTIVE" else "#dc2626"
            status_text = f"<font color='{status_color}'><b>{xml_escape(g.governance_status)}</b></font>"

            inv_rows.append([
                Paragraph(target, style_table_cell),
                Paragraph(cname, style_table_cell),
                Paragraph(conf, style_table_cell_bold),
                Paragraph(purp, style_table_cell),
                Paragraph(ret, style_table_cell),
                Paragraph(status_text, style_table_cell)
            ])

        t_inv = Table(inv_rows, colWidths=[120, 100, 36, 120, 68, 60], repeatRows=1)
        t_inv.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), c_dark),
            ("GRID", (0, 0), (-1, -1), 0.5, c_border),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_bg_light]),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("ALIGN", (2, 1), (2, -1), "CENTER"),
        ]))
        elements.append(t_inv)
        elements.append(Spacer(1, 14))

        # 3. Evidence Gaps & Action Checklist
        elements.append(Paragraph("3. Evidence Gaps & Missing Metadata Action Checklist", style_h1))
        if not all_gaps:
            elements.append(Paragraph("No governance compliance evidence gaps detected.", style_body))
        else:
            gap_headers = [
                Paragraph("<b>Sev.</b>", style_table_header),
                Paragraph("<b>Target Field Identifier</b>", style_table_header),
                Paragraph("<b>Gap Type</b>", style_table_header),
                Paragraph("<b>Evidence Findings & Recommended Human Action</b>", style_table_header)
            ]
            gap_rows = [gap_headers]
            for gap in sorted(all_gaps, key=lambda x: (x.severity != "CRITICAL", x.severity != "HIGH")):
                sev_color = "#dc2626" if gap.severity == "CRITICAL" else "#d97706"
                sev_html = f"<font color='{sev_color}'><b>{xml_escape(gap.severity)}</b></font>"
                g_title = xml_escape(gap.title)
                g_desc = xml_escape(gap.description)
                g_action = xml_escape(gap.human_action_recommendation)
                desc_html = f"<b>{g_title}</b>: {g_desc}<br/><font color='#0369a1'>↳ <b>Action:</b> {g_action}</font>"

                gap_rows.append([
                    Paragraph(sev_html, style_table_cell_bold),
                    Paragraph(xml_escape(gap.field_identifier), style_table_cell_code),
                    Paragraph(xml_escape(gap.gap_type), style_table_cell),
                    Paragraph(desc_html, style_table_cell)
                ])

            t_gaps = Table(gap_rows, colWidths=[45, 125, 95, letter[0] - 108 - 265], repeatRows=1)
            t_gaps.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#991b1b")), # Red 800
                ("GRID", (0, 0), (-1, -1), 0.5, c_border),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_bg_light]),
                ("TOPPADDING", (0, 0), (-1, -1), 3.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ]))
            elements.append(t_gaps)

        elements.append(Spacer(1, 14))

        # 4. Benchmark Precision & Recall Evaluation
        if evaluation:
            elements.append(Paragraph("4. Benchmark Precision & Recall Performance", style_h1))
            summary_eval_text = (
                f"Evaluated across <b>{evaluation.total_evaluated_fields} fields</b> against ground truth. "
                f"Macro Precision: <b>{evaluation.macro_precision:.1%}</b> | "
                f"Macro Recall: <b>{evaluation.macro_recall:.1%}</b> | "
                f"Macro F1-Score: <b>{evaluation.macro_f1:.1%}</b>"
            )
            elements.append(Paragraph(summary_eval_text, style_body))
            elements.append(Spacer(1, 5))

            eval_headers = [
                Paragraph("<b>Code</b>", style_table_header),
                Paragraph("<b>Predefined Data Class</b>", style_table_header),
                Paragraph("<b>Support</b>", style_table_header),
                Paragraph("<b>TP</b>", style_table_header),
                Paragraph("<b>FP</b>", style_table_header),
                Paragraph("<b>FN</b>", style_table_header),
                Paragraph("<b>Precision</b>", style_table_header),
                Paragraph("<b>Recall</b>", style_table_header),
                Paragraph("<b>F1-Score</b>", style_table_header)
            ]
            eval_rows = [eval_headers]
            for cid, m in evaluation.class_metrics.items():
                eval_rows.append([
                    Paragraph(m.class_id, style_table_cell_bold),
                    Paragraph(m.class_name, style_table_cell),
                    Paragraph(str(m.support), style_table_cell),
                    Paragraph(str(m.true_positives), style_table_cell),
                    Paragraph(str(m.false_positives), style_table_cell),
                    Paragraph(str(m.false_negatives), style_table_cell),
                    Paragraph(f"{m.precision:.1%}", style_table_cell),
                    Paragraph(f"{m.recall:.1%}", style_table_cell),
                    Paragraph(f"<b>{m.f1_score:.1%}</b>", style_table_cell_bold)
                ])

            t_eval = Table(eval_rows, colWidths=[36, 134, 42, 28, 28, 28, 54, 54, 100], repeatRows=1)
            t_eval.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#581c87")), # Purple 900
                ("GRID", (0, 0), (-1, -1), 0.5, c_border),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_bg_light]),
                ("TOPPADDING", (0, 0), (-1, -1), 3.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
                ("ALIGN", (2, 1), (-1, -1), "CENTER"),
            ]))
            elements.append(t_eval)

        # Build Document
        doc.build(elements, canvasmaker=NumberedCanvas)
        return output_path
