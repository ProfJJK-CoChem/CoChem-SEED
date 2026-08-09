# 🌱 **CoChem-SEED: Student Evaluation & Educational Dashboard**

Welcome to your Computational Chemistry Lab workspace!

If you have never written code before, don't worry—you do not need to be a computer scientist to run these labs. CoChem-SEED is designed to act as a virtual Teaching Assistant (TA), running complex chemistry simulations in the background and presenting you with a simple, interactive laboratory notebook.

---

## **🎯 What does this do?**

CoChem-SEED allows you to execute professional-grade chemistry simulations (powered by advanced computational engines) right from your web browser:

* **Socratic Interactions:** The system prompts you with interactive questions as you progress through your lab exercise.
* **FERPA Privacy Guards:** Uses cryptographic hashing to protect your Student ID; personal data is never written to the disk in plain text.
* **Automated PDF Compilation:** When you finish a lab exercise, the dashboard strips away raw Python code blocks and compiles a formatted PDF report ready for Canvas upload.

---

## **🚀 Getting Started (Quick Setup)**

Your instructor has already pre-configured the backend settings. All you need to do is launch your notebook!

1. **Open the Lab Workspace:** Click the workspace link provided by your professor (usually a GitHub Codespace or JupyterHub link).
2. **Open the Notebook:** In the file list, double-click the target lab notebook (e.g., `Chemistry_Lab_1.ipynb` under the `notebooks/` directory).
3. **Run the Initialization Cell:** Click inside the first gray cell and press `Shift + Enter` (or click the **Play** button at the top of your screen).
4. **Follow the Prompts:** The interactive system will guide you step-by-step from there.

---

## **📂 File Topology & Core Scripts**

For developers and instructors, the core logic is structured under `core_logic/`:

1. **[core_logic/cochem_seed_ingest.py](file:///d:/GitHub-Repo/CoChem-SEED/core_logic/cochem_seed_ingest.py)** (Reaction Selection Matrix):
   * Renders the progressive disclosure dropdown panels for mechanism/substrate selection.
   * Bootstrap-creates and verifies the curriculum database (`seed_curriculum.db`).

2. **[core_logic/cochem_seed_dispatch.py](file:///d:/GitHub-Repo/CoChem-SEED/core_logic/cochem_seed_dispatch.py)** (Job Dispatcher):
   * Handles local and remote execution routes for student molecular submissions.

3. **[core_logic/cochem_seed_spectra.py](file:///d:/GitHub-Repo/CoChem-SEED/core_logic/cochem_seed_spectra.py)** (Spectra Emulator):
   * Parses vibrational outputs and renders interactive IR/NMR plots.

4. **[core_logic/cochem_seed_viewer.py](file:///d:/GitHub-Repo/CoChem-SEED/core_logic/cochem_seed_viewer.py)** (3D Coordinate Viewer):
   * Integrates 3D structural renders directly into the notebook cells.

5. **[core_logic/cochem_seed_export.py](file:///d:/GitHub-Repo/CoChem-SEED/core_logic/cochem_seed_export.py)** (PDF manuscript compiler):
   * Generates clean report printouts for LMS uploads.

---

## **⚠️ Note on Session Restores**

If you accidentally close your browser window or lose your internet connection during a quiz question, **do not panic.** CoChem-SEED automatically serializes your exact state to `eval_telemetry.json` and will restore your session when you re-open your lab notebook.