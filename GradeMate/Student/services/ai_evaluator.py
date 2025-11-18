from .ocr import get_embedding, cosine_similarity

def evaluate_answer(model_answer, student_answer):
    """
    Evaluate student answer against model answer using embedding-based similarity.
    Returns a dictionary with 'score' (0-10) and 'feedback'.
    Uses sentence transformers to calculate semantic similarity.
    """
    try:
        # Validate inputs
        if not model_answer or not model_answer.strip():
            return {
                "score": 0.0,
                "feedback": "Evaluation error: Model answer is empty."
            }
        
        if not student_answer or not student_answer.strip():
            return {
                "score": 0.0,
                "feedback": "Your answer is empty. Please provide a complete answer."
            }
        
        # Get embeddings for both answers
        try:
            emb_student = get_embedding(student_answer)
            emb_model = get_embedding(model_answer)
        except Exception as e:
            print(f"❌ Error getting embeddings: {e}")
            return {
                "score": 0.0,
                "feedback": "Evaluation error: Could not process answers. Please try again."
            }
        
        # Calculate cosine similarity (returns value between 0 and 1)
        similarity = cosine_similarity(emb_student, emb_model)
        
        # Convert similarity (0-1) to score (0-10)
        score = similarity * 10
        
        # Round to 1 decimal place
        score = round(score, 1)
        
        # Ensure score is within bounds
        if score < 0:
            score = 0.0
        elif score > 10:
            score = 10.0
        
        # Generate feedback based on score
        feedback = generate_feedback(score, similarity)
        
        return {
            "score": score,
            "feedback": feedback
        }
        
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        return {
            "score": 0.0,
            "feedback": "Evaluation error"
        }


def generate_feedback(score, similarity):
    """
    Generate constructive feedback based on the score and similarity.
    """
    if score >= 9.0:
        return f"Excellent work! Your answer demonstrates a strong understanding of the topic (similarity: {similarity:.1%}). You've covered the key points comprehensively and accurately."
    elif score >= 7.0:
        return f"Good answer! You've captured most of the important concepts (similarity: {similarity:.1%}). Consider adding more detail or examples to strengthen your response."
    elif score >= 5.0:
        return f"Your answer shows some understanding (similarity: {similarity:.1%}), but it's missing several key points. Review the topic and try to include more relevant information."
    elif score >= 3.0:
        return f"Your answer needs improvement (similarity: {similarity:.1%}). It only partially addresses the question. Please review the material and provide a more complete response."
    else:
        return f"Your answer doesn't align well with the expected response (similarity: {similarity:.1%}). Please review the topic thoroughly and provide a more accurate and complete answer."
