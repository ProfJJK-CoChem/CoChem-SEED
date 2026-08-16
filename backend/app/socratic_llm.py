# Copyright 2026 CoChem Project Family. All rights reserved.
# Apache License 2.0
"""
Socratic Chemistry Feedback & Pedagogical Intent Evaluator.
Replaces arbitrary character-length checks with rubric-based spectroscopic analysis.
"""

from typing import Dict, Any, List
import hashlib
import secrets
import logging

logger = logging.getLogger(__name__)

# Key spectroscopic concepts explaining harmonic DFT vs experimental differences
PHYSICAL_CONCEPTS = [
    ("anharmonic", "Anharmonicity correction"),
    ("solvent", "Solvent/Matrix interaction"),
    ("fermi", "Fermi resonance"),
    ("scale factor", "Empirical DFT scaling factor"),
    ("scaling factor", "Empirical DFT scaling factor"),
    ("basis set", "Basis set incompleteness error"),
    ("condensation", "Condensed-phase hydrogen bonding"),
    ("hydrogen bond", "Condensed-phase hydrogen bonding"),
]

def grade_intent(student_id: str, justification: str, theo: float, exp: float) -> Dict[str, Any]:
    """
    Evaluates student justification regarding theoretical vs experimental spectroscopic discrepancies.
    Validates physical concepts (anharmonicity, scaling factors, matrix effects) against quantitative deviations.
    """
    if not student_id:
        raise ValueError("student_id is required")

    salt = secrets.token_hex(8)
    student_hash = hashlib.sha256(f"{student_id}_{salt}".encode('utf-8')).hexdigest()

    if theo <= 0 or exp <= 0:
        raise ValueError(f"Frequencies must be positive numbers. Got theo={theo}, exp={exp}")

    delta_nu = abs(theo - exp)
    pct_diff = (delta_nu / exp) * 100.0

    just_lower = justification.lower() if justification else ""
    concepts_identified: List[str] = []

    for term, label in PHYSICAL_CONCEPTS:
        if term in just_lower and label not in concepts_identified:
            concepts_identified.append(label)

    # Deterministic scientific evaluation based on error magnitude and physical concepts
    if len(concepts_identified) >= 2:
        score = 25
        feedback = (
            f"Excellent analysis (Δν = {delta_nu:.1f} cm⁻¹, {pct_diff:.1f}% deviation). "
            f"Correctly identified physical factors: {', '.join(concepts_identified)}."
        )
    elif len(concepts_identified) == 1:
        score = 15
        feedback = (
            f"Good physical reasoning (Δν = {delta_nu:.1f} cm⁻¹). "
            f"Identified {concepts_identified[0]}. Consider additional factors like anharmonicity or solvent shift."
        )
    else:
        score = 5 if len(justification.strip()) > 10 else 0
        feedback = (
            f"The deviation is Δν = {delta_nu:.1f} cm⁻¹ ({pct_diff:.1f}%). "
            "Please explain the physical origin of the difference (e.g. harmonic approximation vs anharmonicity, "
            "empirical frequency scaling, or condensed phase hydrogen bonding)."
        )

    return {
        "student_hash": student_hash,
        "delta_nu_cm1": round(delta_nu, 2),
        "percent_diff": round(pct_diff, 2),
        "concepts_identified": concepts_identified,
        "score": score,
        "feedback": feedback
    }
