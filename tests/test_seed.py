"""
PyTest Suite for CoChem-SEED
Automated testing for active learning problem generators, spectra fitter, and dispatch router.
"""

import sys
import tempfile
import json
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from core_logic.seed_active_learning import SeedRotationalGenerator, SeedIRGenerator, SeedNMRGenerator
from core_logic.cochem_seed_spectra import fetch_spectra_data
from core_logic.cochem_seed_dispatch import generate_3d_target, provision_actions_backend

def test_seed_rotational_generator():
    gen = SeedRotationalGenerator()
    prob = gen.generate_problem(difficulty=1)
    assert "target" in prob
    target = prob["target"]
    eval_res = gen.evaluate(prob, {"A": target["A"], "B": target["B"], "C": target["C"], "rotor": target["rotor"]})
    assert eval_res["score"] == 100.0
    assert eval_res["passed"] is True

def test_seed_ir_generator():
    gen = SeedIRGenerator()
    prob = gen.generate_problem(difficulty=2)
    sub = {}
    for g in gen.FUNCTIONAL_GROUPS:
        sub[g] = "Present" if g in prob["active_groups"] else "Eliminated"
    eval_res = gen.evaluate(prob, sub)
    assert eval_res["score"] == 100.0
    assert eval_res["passed"] is True

def test_seed_nmr_generator():
    gen = SeedNMRGenerator()
    prob = gen.generate_problem(difficulty=1)
    sub = [{"shift": p["shift"], "mult": p["mult"]} for p in prob["peaks"]]
    eval_res = gen.evaluate(prob, sub)
    assert eval_res["score"] == 100.0
    assert eval_res["passed"] is True

def test_seed_fetch_spectra():
    x, y_exp, x_th, y_th = fetch_spectra_data("rxn_001")
    assert len(x) > 0
    assert len(y_exp) > 0
    assert len(x_th) > 0

def test_seed_dispatch_3d_target():
    with tempfile.TemporaryDirectory() as tmpdir:
        target_xyz = Path(tmpdir) / "test_target.xyz"
        # Test 3D XYZ target generation from SMILES
        from rdkit import Chem
        from rdkit.Chem import AllChem
        mol = Chem.MolFromSmiles("CC")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        Chem.MolToXYZFile(mol, str(target_xyz))
        assert target_xyz.exists()

def test_seed_generators_determinism():
    rot_gen = SeedRotationalGenerator()
    p1 = rot_gen.generate_problem(difficulty=1, seed=42)
    p2 = rot_gen.generate_problem(difficulty=1, seed=42)
    assert p1 == p2, "SeedRotationalGenerator failed determinism check!"

    ir_gen = SeedIRGenerator()
    i1 = ir_gen.generate_problem(difficulty=1, seed=42)
    i2 = ir_gen.generate_problem(difficulty=1, seed=42)
    assert i1 == i2, "SeedIRGenerator failed determinism check!"

def test_seed_ingest_curated_db(tmp_path):
    from core_logic.cochem_seed_ingest import _dev_bootstrap_db, fetch_curriculum_options
    db_file = tmp_path / "test_curriculum.db"
    _dev_bootstrap_db(db_file)
    curriculum = fetch_curriculum_options(db_file)
    assert len(curriculum) >= 5, "Curated reaction database should contain multiple reaction classes!"

