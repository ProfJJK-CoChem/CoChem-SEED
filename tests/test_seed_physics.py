import pytest
from app.physics_local import predict_ir, generate_3d
from app.api_sdbs import fetch_sdbs
from app.socratic_llm import grade_intent

def test_predict_ir_ethanol():
    res = predict_ir("CCO")
    assert res["status"] == "success"
    assert "Alcohol/Phenol O-H stretch" in res["functional_groups"]
    assert 3400.0 in res["frequencies"]

def test_predict_ir_acetone():
    res = predict_ir("CC(=O)C")
    assert res["status"] == "success"
    assert "Carbonyl C=O stretch" in res["functional_groups"]
    assert 1715.0 in res["frequencies"]

def test_predict_ir_invalid():
    res = predict_ir("INVALID_SMILES_STRING")
    assert res["status"] == "invalid_smiles"
    assert res["frequencies"] == []

def test_generate_3d_methane():
    res = generate_3d("C")
    assert res["status"] == "success"
    assert "xyz" in res
    assert len(res["xyz"]) > 0

def test_generate_3d_invalid():
    res = generate_3d("XYZ_NOT_REAL")
    assert res["status"] == "invalid_smiles"
    assert res["xyz"] == ""

def test_fetch_sdbs_missing_config():
    with pytest.raises(NotImplementedError) as excinfo:
        fetch_sdbs("LFQSCWFLJHTTHZ-UHFFFAOYSA-N")
    assert "[MISSING DATA]" in str(excinfo.value)

def test_grade_intent():
    res = grade_intent("student_1", "I observe a strong carbonyl peak due to anharmonicity and solvent interaction.", 1715.0, 1720.0)
    assert "feedback" in res
    assert res["score"] == 25
    assert len(res["concepts_identified"]) == 2
