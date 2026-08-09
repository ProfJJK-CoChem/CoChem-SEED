"""
CoChem-SEED: Active Learning Problem Generators & Socratic Evaluators
Procedural problem generation for rotational spectroscopy, IR vibrational modes, and NMR spin system splitting.
"""

import math
import random
from typing import Dict, Any, List

class SeedRotationalGenerator:
    ROTATION_CONSTANT_FACTOR = 505379.005

    def generate_problem(self, difficulty: int = 1) -> Dict[str, Any]:
        if difficulty == 1:
            I_a = round(random.uniform(15.0, 45.0), 4)
            I_b = round(random.uniform(50.0, 120.0), 4)
            I_c = I_b
            rotor = "prolate"
        else:
            I_a = round(random.uniform(15.0, 35.0), 4)
            I_b = round(random.uniform(40.0, 80.0), 4)
            I_c = round(random.uniform(85.0, 160.0), 4)
            rotor = "asymmetric"

        A = round(self.ROTATION_CONSTANT_FACTOR / I_a, 2)
        B = round(self.ROTATION_CONSTANT_FACTOR / I_b, 2)
        C = round(self.ROTATION_CONSTANT_FACTOR / I_c, 2)

        return {
            "I_a": I_a, "I_b": I_b, "I_c": I_c,
            "target": {"A": A, "B": B, "C": C, "rotor": rotor},
            "difficulty": difficulty
        }

    def evaluate(self, problem: Dict[str, Any], answer: Dict[str, Any]) -> Dict[str, Any]:
        target = problem["target"]
        errors = []
        score = 100.0
        for k in ["A", "B", "C"]:
            val = answer.get(k)
            if val is None or abs(val - target[k]) > abs(target[k]) * 0.03:
                errors.append(f"Mismatched {k}: submitted {val}, expected {target[k]}")
                score -= 30.0
        if answer.get("rotor", "").lower() != target["rotor"].lower():
            errors.append(f"Mismatched rotor type: submitted {answer.get('rotor')}, expected {target['rotor']}")
            score -= 10.0
        score = max(0.0, round(score, 1))
        return {"score": score, "passed": score >= 80.0, "errors": errors}

class SeedIRGenerator:
    FUNCTIONAL_GROUPS = ["O-H", "N-H", "C=O", "C-H sp3", "C-H sp2", "C=C"]

    def generate_problem(self, difficulty: int = 1) -> Dict[str, Any]:
        num_active = min(2 + difficulty, 4)
        active = random.sample(self.FUNCTIONAL_GROUPS, num_active)
        eliminated = [g for g in self.FUNCTIONAL_GROUPS if g not in active]
        return {
            "active_groups": active,
            "eliminated_groups": eliminated,
            "difficulty": difficulty
        }

    def evaluate(self, problem: Dict[str, Any], submission: Dict[str, str]) -> Dict[str, Any]:
        score = 100.0
        errors = []
        step = 100.0 / len(self.FUNCTIONAL_GROUPS)
        for g in self.FUNCTIONAL_GROUPS:
            ans = submission.get(g, "Unassigned")
            expected = "Present" if g in problem["active_groups"] else "Eliminated"
            if ans != expected:
                score -= step
                errors.append(f"Group {g}: marked {ans}, expected {expected}")
        score = max(0.0, round(score, 1))
        return {"score": score, "passed": score >= 80.0, "errors": errors}

class SeedNMRGenerator:
    PATTERNS = [
        {"name": "Ethyl", "peaks": [{"shift": 1.2, "mult": "Triplet"}, {"shift": 3.4, "mult": "Quartet"}]},
        {"name": "Isopropyl", "peaks": [{"shift": 1.1, "mult": "Doublet"}, {"shift": 4.0, "mult": "Septet"}]}
    ]

    def generate_problem(self, difficulty: int = 1) -> Dict[str, Any]:
        pat = random.choice(self.PATTERNS)
        offset = round(random.uniform(-0.2, 0.2), 2)
        peaks = [{"shift": round(p["shift"] + offset, 2), "mult": p["mult"]} for p in pat["peaks"]]
        return {"pattern": pat["name"], "peaks": peaks, "difficulty": difficulty}

    def evaluate(self, problem: Dict[str, Any], submission: List[Dict[str, Any]]) -> Dict[str, Any]:
        truth = problem["peaks"]
        if len(submission) != len(truth):
            return {"score": 0.0, "passed": False, "errors": ["Peak count mismatch"]}
        score = 100.0
        errors = []
        for s, t in zip(submission, truth):
            if abs(s.get("shift", 0) - t["shift"]) > 0.05 or str(s.get("mult")).lower() != str(t["mult"]).lower():
                errors.append(f"Mismatched peak at {t['shift']} ({t['mult']})")
                score -= (100.0 / len(truth))
        score = max(0.0, round(score, 1))
        return {"score": score, "passed": score >= 80.0, "errors": errors}
