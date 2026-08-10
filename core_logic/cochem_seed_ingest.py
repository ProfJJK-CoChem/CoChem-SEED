import json
import hashlib
import sqlite3
import pathlib
import ipywidgets as widgets
from IPython.display import display, HTML

# -------------------------------------------------------------------------
# CONSTANTS & CONFIGURATION
# -------------------------------------------------------------------------
CONFIG_PATH = pathlib.Path("cochem_system_config.json")
PARAMS_OUTPUT_PATH = pathlib.Path("seed_run_params.json")

# In a production deployment, this hash is hardcoded by the CI/CD pipeline
# after building the authoritative SQLite curriculum vault.
CANONICAL_VAULT_HASH = "DEVELOPMENT_MODE_UNLOCKED" 

# -------------------------------------------------------------------------
# CORE LOGIC & SECURITY GUARDS
# -------------------------------------------------------------------------
def load_config():
    """Loads the authoritative system configuration, enforcing the air-gap."""
    if not CONFIG_PATH.exists():
        display(HTML("<div style='color: white; background-color: #b91c1c; padding: 10px; border-radius: 5px; font-family: monospace;'>"
                     "<b>CRITICAL ERROR:</b> cochem_system_config.json not found. Run Stage 0.0 first.</div>"))
        return None
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def _dev_bootstrap_db(db_path):
    """Developer helper: Mocks the curriculum database if it doesn't exist yet."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS reactions 
                      (id INTEGER PRIMARY KEY, rxn_class TEXT, name TEXT, target_smiles TEXT)''')
    
    # Curated Organic Chemistry Reactions Dataset (MOCK-28 / Suggestion 28 Resolved)
    mocks = [
        ("SN2", "Primary Halide - Chloromethane", "CCl"),
        ("SN2", "Primary Halide - Chloroethane", "CCCl"),
        ("SN2", "Secondary Halide - 2-Chloropropane", "CC(C)Cl"),
        ("SN2", "Tertiary Halide (Steric Trap)", "CC(C)(C)Cl"),
        ("SN1", "Tertiary Carbocation - t-Butyl Chloride", "CC(C)(C)Cl"),
        ("SN1", "Tertiary Carbocation - 2-Bromo-2-methylbutane", "CCC(C)(C)Br"),
        ("E2", "Zaitsev Product Bias - 2-Bromobutane", "CC(Br)CC"),
        ("E2", "Hofmann Product Bias - 2-Bromo-2,3-dimethylbutane", "CC(C)C(C)(Br)C"),
        ("E1", "Acid-Catalyzed Dehydration - Cyclohexanol", "C1CCCCCC1O"),
        ("Electrophilic Addition", "Alkene Bromination - Ethene", "C=C"),
        ("Electrophilic Addition", "Markovnikov Hydration - Propene", "CC=C"),
        ("Electrophilic Addition", "Anti-Markovnikov Hydroboration - Propene", "CC=C"),
        ("Diels-Alder", "1,3-Butadiene + Ethylene", "C=CC=C"),
        ("Aromatic Substitution", "Benzene Nitration", "c1ccccc1"),
        ("Aromatic Substitution", "Toluene Friedel-Crafts Alkylation", "Cc1ccccc1")
    ]
    cursor.executemany("INSERT OR IGNORE INTO reactions (rxn_class, name, target_smiles) VALUES (?, ?, ?)", mocks)
    conn.commit()
    conn.close()

def verify_vault_integrity(db_path, strict_mode=True):
    """Performs a SHA-256 chunked hash check to prevent student tampering."""
    if not db_path.exists():
        _dev_bootstrap_db(db_path) # Auto-generate for testing if missing
        
    sha256_hash = hashlib.sha256()
    with open(db_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            
    calculated_hash = sha256_hash.hexdigest()
    
    if strict_mode and CANONICAL_VAULT_HASH != "DEVELOPMENT_MODE_UNLOCKED":
        if calculated_hash != CANONICAL_VAULT_HASH:
            display(HTML(f"<div style='color: white; background-color: #b91c1c; padding: 10px; border-radius: 5px; font-family: monospace;'>"
                         f"<b>FERPA/INTEGRITY LOCK:</b> Vault hash mismatch.<br>"
                         f"Expected: {CANONICAL_VAULT_HASH}<br>Got: {calculated_hash}<br>"
                         f"<i>Please re-pull the repository to restore the untampered curriculum data.</i></div>"))
            return False
    return True

def fetch_curriculum_options(db_path):
    """Extracts the available curated reactions for the progressive disclosure UI."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT rxn_class, id, name FROM reactions")
    rows = cursor.fetchall()
    conn.close()
    
    # Restructure into a nested dict: { 'SN2': [('Name', id)], ... }
    curriculum = {}
    for rxn_class, rxn_id, name in rows:
        if rxn_class not in curriculum:
            curriculum[rxn_class] = []
        curriculum[rxn_class].append((name, rxn_id))
    return curriculum

# -------------------------------------------------------------------------
# PROGRESSIVE DISCLOSURE UI (IPYWIDGETS)
# -------------------------------------------------------------------------
def render_ui():
    cfg = load_config()
    if not cfg: return
    
    db_path = pathlib.Path(cfg["Paths"]["curriculum_vault"])
    strict_mode = cfg.get("Data_Privacy", {}).get("static_vault_verification", True)
    
    if not verify_vault_integrity(db_path, strict_mode):
        return
        
    curriculum_data = fetch_curriculum_options(db_path)
    
    # --- UI Elements ---
    title = widgets.HTML("<h3 style='font-family: sans-serif; color: #2e3440;'>CoChem-SEED: Reaction Selection Matrix</h3>")
    
    class_dropdown = widgets.Dropdown(
        options=list(curriculum_data.keys()) + ["Novel Target (Advanced)"],
        description='Mechanism:',
        style={'description_width': 'initial'}
    )
    
    reaction_dropdown = widgets.Dropdown(
        options=curriculum_data.get(class_dropdown.value, []),
        description='Substrate:',
        style={'description_width': 'initial'}
    )
    
    custom_smiles_input = widgets.Text(
        placeholder='e.g. CCO',
        description='SMILES:',
        disabled=True,
        style={'description_width': 'initial'}
    )
    
    submit_btn = widgets.Button(
        description='Lock Selection & Proceed',
        button_style='success',
        icon='check'
    )
    
    output_console = widgets.Output()
    
    # --- Interactivity Observers ---
    def on_class_change(change):
        selected_class = change['new']
        if selected_class == "Novel Target (Advanced)":
            reaction_dropdown.disabled = True
            reaction_dropdown.options = []
            custom_smiles_input.disabled = False
        else:
            reaction_dropdown.disabled = False
            custom_smiles_input.disabled = True
            custom_smiles_input.value = ""
            reaction_dropdown.options = curriculum_data.get(selected_class, [])
            
    class_dropdown.observe(on_class_change, names='value')
    
    def on_submit(b):
        with output_console:
            output_console.clear_output()
            
            payload = {
                "mode": "curated" if class_dropdown.value != "Novel Target (Advanced)" else "novel",
                "reaction_class": class_dropdown.value,
                "reaction_id": reaction_dropdown.value if not reaction_dropdown.disabled else None,
                "custom_smiles": custom_smiles_input.value if not custom_smiles_input.disabled else None
            }
            
            # Validation traps
            if payload["mode"] == "novel" and not payload["custom_smiles"].strip():
                display(HTML("<span style='color: red;'><b>Error:</b> Please provide a valid SMILES string.</span>"))
                return
                
            # Serialize state for Stage 2.0/3.0 to consume
            with open(PARAMS_OUTPUT_PATH, "w") as f:
                json.dump(payload, f, indent=4)
                
            display(HTML("<span style='color: green;'><b>Success:</b> Parameters locked to <code>seed_run_params.json</code>. Ready for Stage 2.0 Dispatch.</span>"))

    submit_btn.on_click(on_submit)
    
    # --- Layout Assembly ---
    ui_box = widgets.VBox([
        title,
        widgets.HBox([class_dropdown, reaction_dropdown]),
        custom_smiles_input,
        submit_btn,
        output_console
    ], layout=widgets.Layout(padding='20px', border='1px solid #d8dee9', border_radius='5px', background_color='#eceff4'))
    
    display(ui_box)

if __name__ == "__main__":
    render_ui()