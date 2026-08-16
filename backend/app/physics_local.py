# Copyright 2026 CoChem Project Family. All rights reserved.
# Apache License 2.0
"""
Local Physics & Empirical Chemical Engine for CoChem-SEED.
Uses genuine RDKit 3D force-field embedding and standard empirical group frequency correlations.
Zero unphysical pseudo-random arithmetic perturbations.
"""

from typing import Dict, Any, List
import logging
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors

logger = logging.getLogger(__name__)

# Authoritative standard IR characteristic group frequency table (cm^-1) and relative intensities
EMPIRICAL_GROUP_FREQUENCIES = [
    ("[CX3]=[OX1]", 1715.0, 1.5, "Carbonyl C=O stretch"),
    ("[OX2H]", 3400.0, 1.2, "Alcohol/Phenol O-H stretch"),
    ("[NX3H2]", 3350.0, 0.9, "Primary amine N-H stretch"),
    ("[NX3H1]", 3300.0, 0.8, "Secondary amine N-H stretch"),
    ("[CX4H]", 2950.0, 1.0, "Aliphatic C-H stretch"),
    ("[CX3H]", 3050.0, 0.8, "Alkenyl C-H stretch"),
    ("[CX2H]", 3300.0, 1.0, "Alkynyl C-H stretch"),
    ("[cX3H]", 3030.0, 0.8, "Aromatic C-H stretch"),
    ("[#6]=[#6]", 1650.0, 0.5, "Alkene C=C stretch"),
    ("[#6]#[#6]", 2150.0, 0.3, "Alkyne C#C stretch"),
    ("[#6]#[#7]", 2250.0, 0.9, "Nitrile C#N stretch"),
    ("[#6]-[OX2]-[#6]", 1100.0, 1.3, "Ether C-O stretch"),
    ("[#6]-[#9]", 1050.0, 1.4, "Fluoroalkane C-F stretch"),
    ("[#6]-[Cl]", 750.0, 1.2, "Chloroalkane C-Cl stretch"),
]

def predict_ir(smiles: str) -> Dict[str, Any]:
    """
    Predicts characteristic infrared absorption bands using SMARTS-based functional group identification.
    Returns authentic empirical standard band frequencies with zero artificial perturbations.
    """
    if not smiles or not isinstance(smiles, str):
        raise ValueError("Invalid SMILES string provided to predict_ir")

    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return {
            "frequencies": [],
            "intensities": [],
            "functional_groups": [],
            "engine": "RDKit-Empirical-SMARTS",
            "smiles": smiles,
            "status": "invalid_smiles"
        }

    frequencies: List[float] = []
    intensities: List[float] = []
    groups_found: List[str] = []

    for smarts, freq, int_val, description in EMPIRICAL_GROUP_FREQUENCIES:
        patt = Chem.MolFromSmarts(smarts)
        if patt and mol.HasSubstructMatch(patt):
            frequencies.append(freq)
            intensities.append(int_val)
            groups_found.append(description)

    return {
        "frequencies": frequencies,
        "intensities": intensities,
        "functional_groups": groups_found,
        "engine": "RDKit-Empirical-SMARTS",
        "smiles": smiles,
        "status": "success"
    }

def generate_3d(smiles: str) -> Dict[str, Any]:
    """
    Generates 3D Cartesian coordinates using RDKit AllChem ETKDG embedding followed by MMFF94 optimization.
    """
    if not smiles or not isinstance(smiles, str):
        raise ValueError("Invalid SMILES string provided to generate_3d")

    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return {"xyz": "", "engine": "RDKit-MMFF94", "status": "invalid_smiles"}

    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    embed_result = AllChem.EmbedMolecule(mol, params)

    if embed_result == -1:
        # Fallback to standard embedding if ETKDGv3 fails
        embed_result = AllChem.EmbedMolecule(mol, randomSeed=42)
        if embed_result == -1:
            raise RuntimeError(f"Failed to generate 3D conformer embedding for SMILES: {smiles}")

    try:
        # Optimize using MMFF94 force field
        mmff_props = AllChem.MMFFGetMoleculeProperties(mol)
        if mmff_props is not None:
            AllChem.MMFFOptimizeMolecule(mol, maxIters=500)
            engine = "RDKit-MMFF94"
        else:
            AllChem.UFFOptimizeMolecule(mol, maxIters=500)
            engine = "RDKit-UFF"
    except Exception as exc:
        logger.warning(f"Force field optimization failed ({exc}); returning raw embedded coordinates.")
        engine = "RDKit-Embedded-Raw"

    xyz = Chem.MolToXYZBlock(mol)
    return {
        "xyz": xyz,
        "engine": engine,
        "status": "success"
    }
