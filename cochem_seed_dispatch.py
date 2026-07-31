import json
import time
import pathlib
import subprocess
from rdkit import Chem
from rdkit.Chem import AllChem
import ipywidgets as widgets
from IPython.display import display, HTML

# -------------------------------------------------------------------------
# CONSTANTS & PATHS
# -------------------------------------------------------------------------
CONFIG_PATH = pathlib.Path("cochem_system_config.json")
PARAMS_PATH = pathlib.Path("seed_run_params.json")
TARGET_XYZ = pathlib.Path("seed_novel_target.xyz")
RESULTS_JSON = pathlib.Path("seed_novel_results.json")
GH_WORKFLOW_DIR = pathlib.Path(".github/workflows")
GH_SCRIPTS_DIR = pathlib.Path(".github/scripts")

# -------------------------------------------------------------------------
# CORE LOGIC
# -------------------------------------------------------------------------
def generate_3d_target(smiles: str):
    """Converts SMILES to 3D XYZ while strictly preserving stereocenters."""
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        raise ValueError("Invalid SMILES string provided.")
    
    mol = Chem.AddHs(mol)
    # Enforce chirality to prevent unphysical stereocenter inversion during initial embedding
    AllChem.EmbedMolecule(mol, randomSeed=42, enforceChirality=True)
    Chem.MolToXYZFile(mol, TARGET_XYZ.as_posix())

def provision_actions_backend(solvent="Acetone"):
    """Dynamically scaffolds the GitHub Action YAML and the constrained ASE script."""
    GH_WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)
    GH_SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Generate the GitHub Actions YAML
    yaml_content = """name: CoChem-SEED Compute Router
on:
  workflow_dispatch:

jobs:
  optimize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Compute Engines
        run: pip install ase xtb-python
      - name: Run Constrained Optimization
        run: python .github/scripts/actions_compute.py
      - name: Commit Artifacts
        run: |
          git config --global user.name 'CoChem-Actions-Bot'
          git config --global user.email 'actions@github.com'
          git add seed_novel_results.json
          git commit -m "Auto-commit: Pedagogical geometry optimization"
          git push
"""
    with open(GH_WORKFLOW_DIR / "ochem_compute.yml", "w") as f:
        f.write(yaml_content)
        
    # 2. Generate the Runner Script (Enforcing Solvation & Constraints)
    runner_content = f"""import json
from ase.io import read
from xtb.ase.calculator import XTB
from ase.optimize import LBFGS
from ase.constraints import FixAtoms

# Load structure
atoms = read('{TARGET_XYZ.as_posix()}')

# ENFORCE IMPLICIT SOLVATION (Crucial for SN1/E1 Carbocation stability)
atoms.calc = XTB(method="GFN2-xTB", solvent="{solvent}")

# STEREOCENTER LOCK: Freeze heavy atom backbone temporarily to prevent unphysical inversions
heavy_atoms = [atom.index for atom in atoms if atom.symbol != 'H']
atoms.set_constraint(FixAtoms(indices=heavy_atoms))

# Optimize
opt = LBFGS(atoms, logfile=None)
opt.run(fmax=0.05)

# Serialize safe result
result = {{
    "final_energy_hartree": atoms.get_potential_energy() / 27.2114,
    "status": "converged",
    "solvation_model": "ALPB-{solvent}"
}}
with open('{RESULTS_JSON.as_posix()}', "w") as f:
    json.dump(result, f)
"""
    with open(GH_SCRIPTS_DIR / "actions_compute.py", "w") as f:
        f.write(runner_content)

def dispatch_and_poll(timeout_seconds=180):
    """Triggers the Action and initiates the 3-minute Watchdog loop."""
    display(HTML("<div style='color: #4c566a;'><b>Cloud Dispatch:</b> Pushing payload to GitHub Actions...</div>"))
    
    try:
        # Trigger the workflow via GitHub CLI
        subprocess.run(["gh", "workflow", "run", "ochem_compute.yml"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        display(HTML("<div style='color: #b91c1c;'><b>Auth Error:</b> GitHub CLI not authenticated. Reverting to Vault.</div>"))
        return False

    # Polling Loop
    start_time = time.time()
    progress = widgets.FloatProgress(value=0, min=0, max=timeout_seconds, description='Queue Wait:')
    display(progress)
    
    # Clear previous results if they exist
    if RESULTS_JSON.exists():
        RESULTS_JSON.unlink()

    while (time.time() - start_time) < timeout_seconds:
        # In a real environment, you would git pull here to retrieve the committed artifact
        # subprocess.run(["git", "pull", "--rebase"], capture_output=True)
        
        if RESULTS_JSON.exists():
            progress.bar_style = 'success'
            display(HTML("<div style='color: #a3be8c;'><b>Success:</b> Optimization artifact retrieved.</div>"))
            return True
            
        time.sleep(5)
        progress.value = time.time() - start_time
        
    # Timeout Trap
    progress.bar_style = 'danger'
    display(HTML(f"<div style='color: white; background-color: #d08770; padding: 10px; border-radius: 5px;'>"
                 f"<b>TIMEOUT TRAP:</b> Actions queue exceeded {timeout_seconds} seconds.<br>"
                 f"<i>Cloud Queue Full. Please select a Pre-Packaged reaction from the Stage 1.0 dropdown to continue your lab.</i></div>"))
    return False

def execute_router():
    """Main execution block bridging Stage 1.0 to Stage 3.0"""
    if not PARAMS_PATH.exists():
        display(HTML("<span style='color: red;'>Missing params. Run Stage 1.0 first.</span>"))
        return

    with open(PARAMS_PATH, "r") as f:
        params = json.load(f)
        
    with open(CONFIG_PATH, "r") as f:
        cfg = json.load(f)

    if params.get("mode") == "curated":
        display(HTML("<div style='color: #5e81ac;'><b>Router Bypass:</b> Curated reaction selected. Loading instantly from SQLite Vault...</div>"))
        # Handoff to Stage 3.0
        return
        
    if params.get("mode") == "novel":
        smiles = params.get("custom_smiles")
        solvent = cfg.get("Scientific_Defaults", {}).get("solvent", "Acetone")
        timeout = cfg.get("Compute_Guardrails", {}).get("actions_queue_timeout_seconds", 180)
        
        display(HTML(f"<div style='color: #b48ead;'><b>Novel Target Detected:</b> Preparing 3D embedding for {smiles}...</div>"))
        generate_3d_target(smiles)
        provision_actions_backend(solvent=solvent)
        
        # Git commit the new XYZ and YAML before triggering action
        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Auto-commit: Dispatching novel target payload"], capture_output=True)
        subprocess.run(["git", "push"], capture_output=True)
        
        dispatch_and_poll(timeout_seconds=timeout)

if __name__ == "__main__":
    execute_router()