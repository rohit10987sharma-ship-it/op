"""
Command Line Interface (CLI) for PrivLens.
Privacy Evidence Discovery & Governance Gap Inspection Tool.
"""

import os
import sys
import argparse

# Force UTF-8 encoding on Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from privlens.scanner.engine import ScannerEngine
from privlens.governance.mapper import GovernanceMapper
from privlens.evaluation.metrics import BenchmarkEvaluator
from privlens.reporters.json_reporter import JSONReporter
from privlens.reporters.markdown_reporter import MarkdownReporter
from privlens.reporters.pdf_reporter import PDFReporter

console = Console(force_terminal=True, legacy_windows=False)

DEFAULT_RULES_PATH = os.path.join(os.path.dirname(__file__), "config", "detection_rules.yaml")
DEFAULT_GOV_PATH = os.path.join(os.path.dirname(__file__), "config", "governance_registry.yaml")
DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), "datasets", "synthetic")
DEFAULT_GROUND_TRUTH = os.path.join(os.path.dirname(__file__), "datasets", "ground_truth.json")
DEFAULT_REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")

def print_banner():
    banner = Text("🛡️ PrivLens: PII Discovery & Privacy Evidence Inventory Engine", style="bold cyan")
    console.print(Panel(banner, subtitle="Technical Evidence & Governance Gap Profiler (Non-Legal Interpretation)", style="blue"))

def cmd_scan(args):
    print_banner()
    data_path = args.path or DEFAULT_DATA_DIR
    rules_path = args.rules or DEFAULT_RULES_PATH
    gov_path = args.gov or DEFAULT_GOV_PATH
    
    console.print(f"[bold green]Initializing Scanner...[/bold green]")
    console.print(f"Target path: [cyan]{data_path}[/cyan]")
    console.print(f"Rules config: [cyan]{rules_path}[/cyan]")
    console.print(f"Governance registry: [cyan]{gov_path}[/cyan]\n")
    
    engine = ScannerEngine(rules_path)
    mapper = GovernanceMapper(gov_path)
    
    discovered_fields = engine.scan_path(data_path)
    inventory = mapper.map_all(discovered_fields)
    
    # Render Technical Evidence Table
    table = Table(title="🔍 Discovered Candidate Personal Data Fields", show_header=True, header_style="bold magenta")
    table.add_column("Data Source", style="cyan")
    table.add_column("Column", style="bold")
    table.add_column("Data Class", style="yellow")
    table.add_column("Confidence", justify="right")
    table.add_column("Declared Purpose", style="green")
    table.add_column("Retention", justify="center")
    table.add_column("Gov Status", style="bold")

    pii_count = 0
    for item in inventory:
        d = item.discovery
        g = item.governance
        if d.is_candidate_pii:
            pii_count += 1
            src = d.source_name + (f" ({d.table_name})" if d.table_name else "")
            conf_str = f"{d.confidence_score:.0%}"
            purp_str = g.purpose_name or "[red]Missing[/red]"
            ret_str = f"{g.retention_period_months}m" if g.retention_period_months else "[red]Missing[/red]"
            
            status_style = "green" if g.governance_status == "ACTIVE" else "bold red"
            table.add_row(
                src, 
                d.column_name, 
                d.candidate_class_name or "N/A", 
                conf_str, 
                purp_str, 
                ret_str, 
                f"[{status_style}]{g.governance_status}[/{status_style}]"
            )

    console.print(table)
    console.print(f"\n[bold]Total Fields Scanned:[/bold] {len(inventory)} | [bold]Candidate PII Fields:[/bold] [yellow]{pii_count}[/yellow]")

    # Render Evidence Gaps Table
    gaps = [gap for item in inventory for gap in item.gaps]
    if gaps:
        console.print("\n")
        gap_table = Table(title="⚠️ Identified Evidence Gaps & Missing Metadata", show_header=True, header_style="bold red")
        gap_table.add_column("Severity", justify="center")
        gap_table.add_column("Target Field", style="cyan")
        gap_table.add_column("Gap Type", style="yellow")
        gap_table.add_column("Description & Action Required", style="white")

        for g in sorted(gaps, key=lambda x: (x.severity != "CRITICAL", x.severity != "HIGH")):
            sev_color = "red" if g.severity == "CRITICAL" else ("yellow" if g.severity == "HIGH" else "blue")
            gap_table.add_row(
                f"[{sev_color}]{g.severity}[/{sev_color}]",
                g.field_identifier,
                g.gap_type,
                f"{g.description}\n[dim]Action: {g.human_action_recommendation}[/dim]"
            )
        console.print(gap_table)

    # Export report if requested
    if args.export:
        os.makedirs(DEFAULT_REPORT_DIR, exist_ok=True)
        md_path = os.path.join(DEFAULT_REPORT_DIR, "inventory_report.md")
        json_path = os.path.join(DEFAULT_REPORT_DIR, "inventory_report.json")
        pdf_path = os.path.join(DEFAULT_REPORT_DIR, "inventory_report.pdf")
        MarkdownReporter.generate_report(inventory, output_path=md_path)
        JSONReporter.generate_report(inventory, output_path=json_path)
        PDFReporter.generate_report(inventory, output_path=pdf_path)
        console.print(f"\n[bold green]✓ Reports generated successfully:[/bold green]")
        console.print(f"  Markdown: [cyan]{md_path}[/cyan]")
        console.print(f"  PDF:      [cyan]{pdf_path}[/cyan]")
        console.print(f"  JSON:     [cyan]{json_path}[/cyan]")

def cmd_evaluate(args):
    print_banner()
    data_path = args.path or DEFAULT_DATA_DIR
    rules_path = args.rules or DEFAULT_RULES_PATH
    gt_path = args.ground_truth or DEFAULT_GROUND_TRUTH

    console.print(f"[bold green]Running Benchmark Evaluation against Ground Truth...[/bold green]")
    console.print(f"Ground Truth benchmark: [cyan]{gt_path}[/cyan]\n")

    engine = ScannerEngine(rules_path)
    discovered_fields = engine.scan_path(data_path)

    evaluator = BenchmarkEvaluator(gt_path)
    summary = evaluator.evaluate(discovered_fields)

    # Render Per-Class Evaluation Table
    table = Table(title="📊 Per-Class Precision & Recall Evaluation Benchmark", show_header=True, header_style="bold cyan")
    table.add_column("Code", justify="center", style="bold")
    table.add_column("Data Class Name", style="white")
    table.add_column("True (Support)", justify="right")
    table.add_column("TP", justify="right", style="green")
    table.add_column("FP", justify="right", style="red")
    table.add_column("FN", justify="right", style="magenta")
    table.add_column("Precision", justify="right", style="bold")
    table.add_column("Recall", justify="right", style="bold")
    table.add_column("F1-Score", justify="right", style="bold yellow")

    for cid, m in summary.class_metrics.items():
        table.add_row(
            m.class_id,
            m.class_name,
            str(m.support),
            str(m.true_positives),
            str(m.false_positives),
            str(m.false_negatives),
            f"{m.precision:.1%}",
            f"{m.recall:.1%}",
            f"{m.f1_score:.1%}"
        )

    console.print(table)

    summary_panel = Text()
    summary_panel.append(f"Evaluated Fields: {summary.total_evaluated_fields}\n", style="bold")
    summary_panel.append(f"Macro Precision: {summary.macro_precision:.1%}  |  Macro Recall: {summary.macro_recall:.1%}  |  Macro F1: {summary.macro_f1:.1%}\n", style="cyan")
    summary_panel.append(f"Micro Precision: {summary.micro_precision:.1%}  |  Micro Recall: {summary.micro_recall:.1%}  |  Micro F1: {summary.micro_f1:.1%}", style="green")
    console.print(Panel(summary_panel, title="Overall Evaluation Metrics", style="bold white"))

    if args.export:
        os.makedirs(DEFAULT_REPORT_DIR, exist_ok=True)
        eval_json = os.path.join(DEFAULT_REPORT_DIR, "evaluation_benchmark.json")
        import json
        with open(eval_json, "w", encoding="utf-8") as f:
            json.dump(summary.to_dict(), f, indent=2)
        console.print(f"[bold green]✓ Evaluation benchmark saved to:[/bold green] [cyan]{eval_json}[/cyan]")

def cmd_generate(args):
    import datasets.generate_datasets as gen
    console.print("[bold yellow]Generating synthetic datasets and ground truth...[/bold yellow]")
    gen.generate_customer_signups_csv()
    gen.generate_support_tickets_csv()
    gen.generate_marketing_leads_csv()
    gen.generate_sqlite_database()
    gen.generate_ground_truth()
    console.print("[bold green]✓ Datasets and ground truth generated successfully.[/bold green]")

def cmd_serve(args):
    from web.app import run_server
    port = args.port or 5000
    console.print(f"[bold green]Starting PrivLens Web Dashboard at http://127.0.0.1:{port}[/bold green]")
    run_server(port=port, host="127.0.0.1")

def main():
    parser = argparse.ArgumentParser(
        description="PrivLens: PII Discovery, Evidence Inventory, and Governance Gap Engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # scan subcommand
    scan_p = subparsers.add_parser("scan", help="Scan datasets and generate technical evidence inventory")
    scan_p.add_argument("--path", "-p", help="Path to dataset directory or file (CSV or SQLite)")
    scan_p.add_argument("--rules", "-r", help="Path to detection_rules.yaml")
    scan_p.add_argument("--gov", "-g", help="Path to governance_registry.yaml")
    scan_p.add_argument("--export", "-e", action="store_true", help="Export reports to reports/ directory")

    # evaluate subcommand
    eval_p = subparsers.add_parser("evaluate", help="Compute per-class precision, recall, and F1 against ground truth")
    eval_p.add_argument("--path", "-p", help="Path to dataset directory or file")
    eval_p.add_argument("--rules", "-r", help="Path to detection_rules.yaml")
    eval_p.add_argument("--ground-truth", "-gt", help="Path to ground_truth.json")
    eval_p.add_argument("--export", "-e", action="store_true", help="Export evaluation benchmark results to JSON")

    # generate-data subcommand
    subparsers.add_parser("generate-data", help="Re-generate synthetic datasets and ground truth")

    # serve subcommand
    serve_p = subparsers.add_parser("serve", help="Launch interactive Web UI dashboard")
    serve_p.add_argument("--port", type=int, default=5000, help="Web server port (default 5000)")

    args = parser.parse_args()
    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "generate-data":
        cmd_generate(args)
    elif args.command == "serve":
        cmd_serve(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
