import hashlib
import secrets

def grade_intent(student_id: str, justification: str, theo: float, exp: float):
    # FERPA compliant hash
    salt = secrets.token_hex(8)
    student_hash = hashlib.sha256(f"{student_id}_{salt}".encode('utf-8')).hexdigest()
    
    # Mocking LLM grading logic
    prompt = "You are a strict Socratic Chemistry TA..."
    
    score = 0
    feedback = ""
    if len(justification) > 20:
        score = 20
        feedback = "Good justification of the difference."
    else:
        score = -10
        feedback = "Please elaborate on why the theoretical harmonic frequency differs from the experimental peak."
        
    return {
        "student_hash": student_hash,
        "score": score,
        "feedback": feedback
    }
