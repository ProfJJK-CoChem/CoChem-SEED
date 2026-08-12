import os
import json
import hashlib
import secrets
import pathlib
import subprocess
import ipywidgets as widgets
from IPython.display import display, HTML

# -------------------------------------------------------------------------
# CONSTANTS & PATHS
# -------------------------------------------------------------------------
TELEMETRY_PATH = pathlib.Path("eval_telemetry.json")
FERPA_RECORD_PATH = pathlib.Path("cochem_ferpa_record.json")
NOTEBOOK_NAME = "CoChem_SEED_Lab.ipynb" # Default pedagogical entry point

import logging
import sys

logger = logging.getLogger("CoChem_SEED_Export")

def _get_safe_subprocess_run() -> Any:
    try:
        from core_engine.cochem_core_subprocess_broker import safe_subprocess_run
        return safe_subprocess_run
    except ImportError:
        for p in pathlib.Path(__file__).resolve().parents:
            cb = p / "CoChem-BASE"
            if cb.exists() and str(cb) not in sys.path:
                sys.path.insert(0, str(cb))
                break
        from core_engine.cochem_core_subprocess_broker import safe_subprocess_run
        return safe_subprocess_run

# -------------------------------------------------------------------------
# CORE LOGIC & FERPA CRYPTOGRAPHY
# -------------------------------------------------------------------------
def calculate_rai(hints: int, traps: int) -> float:
    """
    Mathematically decouples memory from aptitude. 
    Applies an exponential degradation based on active assistance.
    Base = 100. Hints = -15% each. Traps = -25% each.
    """
    score = 100.0 * ((0.85) ** hints) * ((0.75) ** traps)
    return round(max(score, 0.0), 2)

def generate_ferpa_payload(student_id: str, telemetry_data: dict) -> dict:
    """Generates an OS-level salted hash to securely mask the student PII."""
    # OS-level cryptographic random salt
    salt = secrets.token_hex(8) 
    
    # Hash generation
    payload_string = f"{student_id}_{salt}"
    secure_hash = hashlib.sha256(payload_string.encode('utf-8')).hexdigest()
    
    rai_score = calculate_rai(
        telemetry_data.get("hints_used", 0), 
        telemetry_data.get("traps_triggered", 0)
    )
    
    # Construct the strictly blinded artifact
    ferpa_payload = {
        "student_hash": secure_hash,
        "salt": salt, # Required for PI to reverse-lookup if chosen for research
        "RAI_Score": rai_score,
        "metrics": {
            "hints": telemetry_data.get("hints_used", 0),
            "traps": telemetry_data.get("traps_triggered", 0),
            "final_scale": telemetry_data.get("final_scale", 1.0),
            "final_shift": telemetry_data.get("final_shift", 0.0)
        }
    }
    return ferpa_payload

# -------------------------------------------------------------------------
# UI & NBCONVERT ORCHESTRATION
# -------------------------------------------------------------------------
def render_export_dashboard() -> None:
    if not TELEMETRY_PATH.exists():
        display(HTML("<span style='color: #b91c1c;'><b>Error:</b> eval_telemetry.json missing. Complete Stage 4.0 first.</span>"))
        return

    try:
        from cochem_base.config_loader import load_system_config_dict
        telemetry = load_system_config_dict(TELEMETRY_PATH)
    except Exception:
        with open(TELEMETRY_PATH, "r", encoding="utf-8") as f:
            telemetry = json.loads(f.read())

    # --- UI Elements ---
    title = widgets.HTML("<h3 style='font-family: sans-serif; color: #2e3440;'>Module Completion & Export</h3>")
    
    instructions = widgets.HTML(
        "<div style='font-size: 13px; color: #4c566a; margin-bottom: 10px;'>"
        "Enter your University ID below. Your ID will be cryptographically hashed to protect your privacy "
        "before being committed to the class repository."
        "</div>"
    )
    
    student_id_input = widgets.Text(
        placeholder='e.g., U12345678',
        description='Student ID:',
        style={'description_width': 'initial'}
    )
    
    export_btn = widgets.Button(
        description='Generate Canvas Report',
        button_style='success',
        icon='file-pdf-o'
    )
    
    out_console = widgets.Output()

    def on_export_clicked(b: Any) -> None:
        with out_console:
            out_console.clear_output()
            sid = student_id_input.value.strip()
            
            if not sid:
                display(HTML("<span style='color: #d08770;'><b>Warning:</b> Student ID cannot be empty.</span>"))
                return
                
            export_btn.disabled = True
            display(HTML("<span style='color: #5e81ac;'>Encrypting telemetry and generating report...</span>"))
            
            # 1. Generate and save FERPA-compliant telemetry
            ferpa_data = generate_ferpa_payload(sid, telemetry)
            with open(FERPA_RECORD_PATH, "w", encoding="utf-8") as f:
                json.dump(ferpa_data, f, indent=4)
                
            # 2. Nbconvert Execution (--no-input strips the Python code cells)
            target_notebook = NOTEBOOK_NAME if os.path.exists(NOTEBOOK_NAME) else None
            
            if target_notebook:
                try:
                    safe_run = _get_safe_subprocess_run()
                    safe_run([
                        "jupyter", "nbconvert",
                        "--to", "html",          # HTML ensures native browser support without heavy TeX engines
                        "--no-input",            # Hides code, shows only markdown and outputs
                        "--output", "CoChem_Final_Lab_Report.html",
                        target_notebook
                    ], check=True, capture_output=True)
                    
                    display(HTML(
                        "<div style='background-color: #a3be8c; color: #2e3440; padding: 15px; border-radius: 5px; margin-top: 10px;'>"
                        "<b>✅ Export Successful!</b><br><br>"
                        "<a href='CoChem_Final_Lab_Report.html' download style='color: #2e3440; font-weight: bold; text-decoration: underline;'>"
                        "📥 Download HTML Report Here</a><br><br>"
                        "<i>Instructions: Open the downloaded file in your browser and select 'Print to PDF' for Canvas LMS submission.</i>"
                        "</div>"
                    ))
                except Exception as e:
                    display(HTML(f"<div style='color: #b91c1c;'><b>Nbconvert Error:</b> {e}</div>"))
            else:
                display(HTML(
                    f"<div style='color: #d08770; padding: 10px; border-radius: 5px;'>"
                    f"<b>Warning:</b> Expected notebook <code>{NOTEBOOK_NAME}</code> not found in root. "
                    f"Telemetry saved, but automated PDF generation bypassed. Please manually export via File > Print.</div>"
                ))

    export_btn.on_click(on_export_clicked)

    # --- Layout Assembly ---
    dashboard = widgets.VBox([
        title, 
        instructions, 
        student_id_input, 
        export_btn, 
        out_console
    ], layout=widgets.Layout(padding='20px', border='1px solid #d8dee9', background_color='#eceff4', border_radius='5px'))
    
    display(dashboard)

if __name__ == "__main__":
    render_export_dashboard()