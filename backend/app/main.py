from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from .physics_local import predict_ir, generate_3d
from .api_sdbs import fetch_sdbs
from .socratic_llm import grade_intent

app = FastAPI(title="CoChem-SEED API")

class MoleculeRequest(BaseModel):
    smiles: str

class SpectralRequest(BaseModel):
    smiles: str
    target_peak: float

class SocraticRequest(BaseModel):
    student_id: str
    student_justification: str
    theoretical_peak: float
    experimental_peak: float

@app.get("/")
def read_root():
    return {"status": "CoChem-SEED Backend Active"}

@app.post("/api/physics/generate_3d")
def api_generate_3d(req: MoleculeRequest):
    return generate_3d(req.smiles)

@app.post("/api/physics/predict_ir")
def api_predict_ir(req: MoleculeRequest):
    return predict_ir(req.smiles)

@app.get("/api/db/sdbs/{inchi_key}")
def api_fetch_sdbs(inchi_key: str):
    return fetch_sdbs(inchi_key)

@app.post("/api/grade")
def api_grade(req: SocraticRequest):
    return grade_intent(req.student_id, req.student_justification, req.theoretical_peak, req.experimental_peak)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
