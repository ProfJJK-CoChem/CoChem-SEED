import rdkit.Chem as Chem
import rdkit.Chem.AllChem as AllChem

def predict_ir(smiles: str):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": "Invalid SMILES", "engine": "RDKit-Local-Proxy"}
    
    # RDKit-based proxy for IR frequencies using SMARTS patterns
    patterns = {
        "O-H": ("[OX2H]", 3300.0, 1.0),
        "N-H": ("[NX3H,NX3H2]", 3400.0, 0.7),
        "C-H sp": ("[CX2H]", 3300.0, 0.5),
        "C-H sp2": ("[CX3H]", 3100.0, 0.6),
        "C-H sp3": ("[CX4H]", 2950.0, 0.8),
        "C#N": ("[CX2]#[NX1]", 2250.0, 0.9),
        "C=O": ("[CX3]=[OX1]", 1710.0, 1.5),
        "C=C": ("[CX3]=[CX3]", 1650.0, 0.4),
        "Aromatic C=C": ("c1ccccc1", 1500.0, 0.5),
        "C-O": ("[CX4][OX2]", 1100.0, 1.2)
    }
    
    frequencies = []
    intensities = []
    
    for name, (smarts, freq, intens) in patterns.items():
        pat = Chem.MolFromSmarts(smarts)
        if pat and mol.HasSubstructMatch(pat):
            frequencies.append(freq)
            intensities.append(intens)
            
    # Default baseline if no groups match
    if not frequencies:
        frequencies = [1000.0]
        intensities = [0.1]
        
    return {
        "frequencies": frequencies,
        "intensities": intensities,
        "engine": "RDKit-Local-Proxy"
    }

def generate_3d(smiles: str):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": "Invalid SMILES", "engine": "RDKit-Local"}
    
    mol = Chem.AddHs(mol)
    res = AllChem.EmbedMolecule(mol, randomSeed=42)
    if res != 0:
        res = AllChem.EmbedMolecule(mol, useRandomCoords=True, randomSeed=42)
        if res != 0:
            return {"error": "Failed to embed molecule", "engine": "RDKit-Local"}
            
    AllChem.MMFFOptimizeMolecule(mol)
    xyz = Chem.MolToXYZBlock(mol)
    
    return {
        "xyz": xyz,
        "engine": "RDKit-Local"
    }
