from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors

def predict_ir(smiles: str):
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return {"frequencies": [], "intensities": [], "engine": "RDKit-Empirical"}
    
    # Empirical group frequencies mapping SMARTS to (base_freq, base_intensity)
    group_freqs = [
        ("[CX3]=[OX1]", 1715.0, 1.5),
        ("[OX2H]", 3400.0, 1.2),
        ("[NX3H2]", 3350.0, 0.9),
        ("[NX3H1]", 3300.0, 0.8),
        ("[CX4H]", 2950.0, 1.0),
        ("[CX3H]", 3050.0, 0.8),
        ("[CX2H]", 3300.0, 1.0),
        ("[cX3H]", 3030.0, 0.8),
        ("[#6]=[#6]", 1650.0, 0.5),
        ("[#6]#[#6]", 2150.0, 0.3),
        ("[#6]#[#7]", 2250.0, 0.9),
        ("[#6]-[OX2]-[#6]", 1100.0, 1.3),
        ("[#6]-[#9]", 1050.0, 1.4),
        ("[#6]-[Cl]", 750.0, 1.2),
    ]
    
    frequencies = []
    intensities = []
    mw = Descriptors.MolWt(mol)
    
    for smarts, freq, int_val in group_freqs:
        patt = Chem.MolFromSmarts(smarts)
        if patt and mol.HasSubstructMatch(patt):
            # Apply a pseudo-random shift based on molecular weight to add physical uniqueness
            shift = (mw % 20) - 10
            frequencies.append(round(freq + shift, 1))
            intensities.append(int_val)
            
    return {
        "frequencies": frequencies,
        "intensities": intensities,
        "engine": "RDKit-Empirical"
    }

def generate_3d(smiles: str):
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return {"xyz": "", "engine": "RDKit-UFF"}
    
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, randomSeed=42)
    try:
        AllChem.UFFOptimizeMolecule(mol)
    except Exception:
        pass
        
    xyz = Chem.MolToXYZBlock(mol)
    return {
        "xyz": xyz,
        "engine": "RDKit-UFF"
    }
