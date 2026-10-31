"""
Flask REST API and Web Dashboard Server for PrivLens.
"""

import os
import json
from flask import Flask, jsonify, request, render_template, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename

from privlens.scanner.engine import ScannerEngine
from privlens.governance.mapper import GovernanceMapper
from privlens.evaluation.metrics import BenchmarkEvaluator
from privlens.reporters.json_reporter import JSONReporter
from privlens.reporters.markdown_reporter import MarkdownReporter
from privlens.reporters.pdf_reporter import PDFReporter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_PATH = os.path.join(BASE_DIR, "config", "detection_rules.yaml")
GOV_PATH = os.path.join(BASE_DIR, "config", "governance_registry.yaml")
DATA_DIR = os.path.join(BASE_DIR, "datasets", "synthetic")
GROUND_TRUTH_PATH = os.path.join(BASE_DIR, "datasets", "ground_truth.json")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".csv", ".db", ".sqlite", ".sqlite3"}

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static")
)
CORS(app)

# Cached runtime state
engine = ScannerEngine(RULES_PATH)
mapper = GovernanceMapper(GOV_PATH)
evaluator = BenchmarkEvaluator(GROUND_TRUTH_PATH)

cached_inventory = []
cached_evaluation = None

def refresh_scan(target_path: str = DATA_DIR):
    global cached_inventory, cached_evaluation
    discovered = engine.scan_path(target_path)
    cached_inventory = mapper.map_all(discovered)
    cached_evaluation = evaluator.evaluate(discovered)
    return cached_inventory, cached_evaluation

# Initial state: clean and empty until user uploads a dataset
# (Past synthetic results are not carried)
# cached_inventory = []
# cached_evaluation = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/summary", methods=["GET"])
def get_summary():
    total_fields = len(cached_inventory)
    pii_fields = [it for it in cached_inventory if it.discovery.is_candidate_pii]
    non_pii = [it for it in cached_inventory if not it.discovery.is_candidate_pii]
    all_gaps = [gap for it in cached_inventory for gap in it.gaps]
    
    # Class distribution
    class_dist = {}
    for it in pii_fields:
        cname = it.discovery.candidate_class_name or "Unknown"
        class_dist[cname] = class_dist.get(cname, 0) + 1

    # Governance status distribution
    gov_dist = {}
    for it in pii_fields:
        st = it.governance.governance_status
        gov_dist[st] = gov_dist.get(st, 0) + 1

    return jsonify({
        "total_fields": total_fields,
        "candidate_pii_count": len(pii_fields),
        "non_pii_count": len(non_pii),
        "gap_count": len(all_gaps),
        "class_distribution": class_dist,
        "governance_distribution": gov_dist,
        "evaluation_macro_f1": cached_evaluation.macro_f1 if cached_evaluation else 0.0,
        "legal_disclaimer": (
            "Technical evidence observation only. Not an automated lawful-basis decision, "
            "nor an inference of universal cross-border data transfer. Requires human privacy review."
        )
    })

@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    return jsonify({
        "count": len(cached_inventory),
        "items": [it.to_dict() for it in cached_inventory]
    })

@app.route("/api/gaps", methods=["GET"])
def get_gaps():
    all_gaps = [gap.to_dict() for it in cached_inventory for gap in it.gaps]
    return jsonify({
        "count": len(all_gaps),
        "gaps": sorted(all_gaps, key=lambda x: (x["severity"] != "CRITICAL", x["severity"] != "HIGH"))
    })

@app.route("/api/evaluation", methods=["GET"])
def get_evaluation():
    if not cached_evaluation:
        all_discovered = [it.discovery for it in cached_inventory]
        ev = evaluator.evaluate(all_discovered)
        return jsonify(ev.to_dict())
    return jsonify(cached_evaluation.to_dict())

@app.route("/api/rules", methods=["GET"])
def get_rules():
    return jsonify({
        "data_classes": engine.get_data_classes(),
        "rules": engine.get_rules()
    })

@app.route("/api/scan", methods=["POST"])
def trigger_scan():
    req_data = request.get_json() or {}
    path = req_data.get("path", DATA_DIR)
    refresh_scan(path)
    return jsonify({
        "message": f"Scan completed successfully for {path}",
        "total_fields": len(cached_inventory),
        "candidate_pii_count": sum(1 for it in cached_inventory if it.discovery.is_candidate_pii)
    })

@app.route("/api/upload-and-scan", methods=["POST"])
def upload_and_scan():
    global cached_inventory, cached_evaluation
    if "files" not in request.files and "file" not in request.files:
        return jsonify({"error": "No file uploaded. Please select a CSV or SQLite database file."}), 400

    uploaded_files = request.files.getlist("files")
    if not uploaded_files or (len(uploaded_files) == 1 and uploaded_files[0].filename == ""):
        single_file = request.files.get("file")
        if single_file and single_file.filename != "":
            uploaded_files = [single_file]
        else:
            return jsonify({"error": "No file selected."}), 400

    scan_mode = request.form.get("mode", "replace")  # "replace" by default so past results are not carried
    scanned_filenames = []
    newly_discovered_fields = []

    if scan_mode == "replace":
        # Clean up older uploaded files in UPLOAD_DIR so past results are not carried
        if os.path.exists(UPLOAD_DIR):
            for old_f in os.listdir(UPLOAD_DIR):
                old_path = os.path.join(UPLOAD_DIR, old_f)
                try:
                    if os.path.isfile(old_path):
                        os.remove(old_path)
                except Exception:
                    pass

    for file_obj in uploaded_files:
        filename = secure_filename(file_obj.filename)
        if not filename:
            continue
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({
                "error": f"Unsupported file type '{filename}'. Supported formats: CSV (.csv) and SQLite Database (.db, .sqlite, .sqlite3)."
            }), 400

        save_path = os.path.join(UPLOAD_DIR, filename)
        file_obj.save(save_path)
        scanned_filenames.append(filename)

        # Run scanner engine on uploaded file
        discovered = engine.scan_path(save_path)
        newly_discovered_fields.extend(discovered)

    new_inventory = mapper.map_all(newly_discovered_fields)

    if scan_mode == "replace":
        cached_inventory = new_inventory
    else:
        # Append mode: avoid duplicate field IDs
        existing_ids = {it.field_id for it in cached_inventory}
        for item in new_inventory:
            if item.field_id not in existing_ids:
                cached_inventory.append(item)
                existing_ids.add(item.field_id)

    # Re-evaluate ground truth if available
    all_discovered = [it.discovery for it in cached_inventory]
    cached_evaluation = evaluator.evaluate(all_discovered)

    new_pii_count = sum(1 for it in new_inventory if it.discovery.is_candidate_pii)
    total_pii_count = sum(1 for it in cached_inventory if it.discovery.is_candidate_pii)

    return jsonify({
        "success": True,
        "message": f"Successfully processed and scanned {len(scanned_filenames)} file(s).",
        "scanned_files": scanned_filenames,
        "scanned_fields_count": len(new_inventory),
        "new_pii_detected": new_pii_count,
        "total_fields": len(cached_inventory),
        "total_pii_fields": total_pii_count,
        "items": [it.to_dict() for it in new_inventory]
    })

@app.route("/api/sample-files", methods=["GET"])
def get_sample_files():
    sample_dir = os.path.join(BASE_DIR, "datasets", "synthetic")
    samples = []
    descriptions = {
        "customer_signups.csv": "Customer Signups (Personal Identity, Contact, Location)",
        "kyc_verification_records.csv": "KYC Verification (Government Identifiers: Aadhaar, PAN, Passport, Voter ID, DL)",
        "digital_payments_log.csv": "Digital Payments Log (Financial: Bank Accounts, IFSC, Cards, UPI)",
        "enterprise_data.db": "Enterprise SQLite DB (Employees, Delivery Dispatch, Legacy Shadow Vault)"
    }
    if os.path.exists(sample_dir):
        for f in os.listdir(sample_dir):
            if f.endswith((".csv", ".db", ".sqlite", ".sqlite3")):
                p = os.path.join(sample_dir, f)
                samples.append({
                    "name": f,
                    "size_bytes": os.path.getsize(p),
                    "ext": os.path.splitext(f)[1].lower(),
                    "description": descriptions.get(f, f"Synthetic {os.path.splitext(f)[1].upper()} data repository")
                })
    return jsonify({"samples": samples})

@app.route("/api/load-sample", methods=["POST"])
def load_sample():
    global cached_inventory, cached_evaluation
    import shutil
    data = request.get_json() or {}
    sample_name = data.get("sample_name", "")
    sample_dir = os.path.join(BASE_DIR, "datasets", "synthetic")
    sample_path = os.path.join(sample_dir, secure_filename(sample_name))
    if not os.path.exists(sample_path):
        return jsonify({"error": f"Sample fixture '{sample_name}' not found."}), 404

    target_path = os.path.join(UPLOAD_DIR, secure_filename(sample_name))
    shutil.copyfile(sample_path, target_path)

    mode = data.get("mode", "replace")
    discovered = engine.scan_path(target_path)
    new_inventory = mapper.map_all(discovered)

    if mode == "replace":
        cached_inventory = new_inventory
    else:
        existing_ids = {it.field_id for it in cached_inventory}
        for item in new_inventory:
            if item.field_id not in existing_ids:
                cached_inventory.append(item)
                existing_ids.add(item.field_id)

    all_discovered = [it.discovery for it in cached_inventory]
    cached_evaluation = evaluator.evaluate(all_discovered)

    return jsonify({
        "success": True,
        "sample_name": sample_name,
        "scanned_fields_count": len(new_inventory),
        "total_fields": len(cached_inventory),
        "total_pii_fields": sum(1 for it in cached_inventory if it.discovery.is_candidate_pii)
    })

@app.route("/api/reset-scan", methods=["POST"])
def reset_scan():
    global cached_inventory, cached_evaluation
    cached_inventory = []
    cached_evaluation = None
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            try:
                os.remove(os.path.join(UPLOAD_DIR, f))
            except Exception:
                pass
    return jsonify({"success": True, "message": "Scan workspace reset to clean state."})

@app.route("/api/review-finding", methods=["POST"])
def review_finding():
    data = request.get_json() or {}
    field_id = data.get("field_id")
    decision = data.get("decision", "CONFIRMED")  # CONFIRMED, REJECTED, UNCERTAIN
    
    found = False
    for item in cached_inventory:
        if item.field_id == field_id:
            found = True
            item.governance.governance_status = decision
            if decision == "REJECTED":
                item.discovery.is_candidate_pii = False
            elif decision == "CONFIRMED":
                item.discovery.is_candidate_pii = True
            break
            
    if not found:
        return jsonify({"error": f"Finding '{field_id}' not found in active inventory."}), 404
        
    return jsonify({"success": True, "field_id": field_id, "status": decision})

@app.route("/api/uploads", methods=["GET"])
def list_uploads():
    files = []
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            p = os.path.join(UPLOAD_DIR, f)
            if os.path.isfile(p):
                files.append({
                    "name": f,
                    "size_bytes": os.path.getsize(p),
                    "ext": os.path.splitext(f)[1].lower()
                })
    return jsonify({"uploads": files})

@app.route("/api/test-rule", methods=["POST"])
def test_rule():
    data = request.get_json() or {}
    col_name = data.get("column_name", "test_column")
    sample_text = data.get("samples") if data.get("samples") is not None else data.get("sample_text", "")
    
    # split lines preserving values with commas (e.g., coordinates, addresses)
    if isinstance(sample_text, str):
        if "\n" in sample_text:
            lines = [s.strip() for s in sample_text.split("\n") if s.strip()]
        elif "," in sample_text and len(sample_text.split(",")) > 2:
            lines = [s.strip() for s in sample_text.split(",") if s.strip()]
        else:
            lines = [sample_text.strip()] if sample_text.strip() else []
    else:
        lines = sample_text

    is_pii, cid, cname, conf, evidence, previews = engine.rule_matcher.evaluate_column(col_name, lines)
    return jsonify({
        "column_name": col_name,
        "sample_count": len(lines),
        "is_candidate_pii": is_pii,
        "candidate_class_id": cid,
        "candidate_class_name": cname,
        "confidence_score": conf,
        "evidence_checklist": [
            {
                "rule_id": e.rule_id,
                "rule_name": e.rule_name,
                "matched_by_header": e.matched_by_header,
                "matched_by_value": e.matched_by_value,
                "sample_match_count": e.sample_match_count,
                "match_ratio": e.match_ratio,
                "details": e.details
            } for e in evidence
        ],
        "masked_previews": previews
    })

@app.route("/api/export/markdown", methods=["GET"])
def export_markdown():
    content = MarkdownReporter.generate_report(cached_inventory, cached_evaluation)
    return Response(
        content,
        mimetype="text/markdown",
        headers={"Content-Disposition": "attachment;filename=privlens_technical_report.md"}
    )

@app.route("/api/export/pdf", methods=["GET"])
def export_pdf():
    pdf_out = os.path.join(BASE_DIR, "reports", "privlens_technical_report.pdf")
    PDFReporter.generate_report(cached_inventory, cached_evaluation, output_path=pdf_out)
    with open(pdf_out, "rb") as f:
        pdf_bytes = f.read()
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment;filename=privlens_technical_report.pdf"}
    )

@app.route("/api/export/json", methods=["GET"])
def export_json():
    data = JSONReporter.generate_report(cached_inventory, cached_evaluation)
    return Response(
        json.dumps(data, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=privlens_inventory.json"}
    )

def run_server(host="127.0.0.1", port=5000):
    app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    run_server()
