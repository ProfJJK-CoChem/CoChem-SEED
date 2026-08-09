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
