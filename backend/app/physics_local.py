def predict_ir(smiles: str):
    # Mocking MACE IR local execution
    return {
        "frequencies": [1700.5, 2950.0],
        "intensities": [1.5, 0.8],
        "engine": "MACE-IR-Local"
    }

def generate_3d(smiles: str):
    # Mocking MACE-OFF24 3D generation
    return {
        "xyz": "3\nWater\nO 0 0 0\nH 0.75 0.58 0\nH -0.75 0.58 0",
        "engine": "MACE-OFF24"
    }
