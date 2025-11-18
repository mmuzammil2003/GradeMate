from .ocr import get_embedding, cosine_similarity

def check_plagiarism(student_text, others, threshold=0.9):
    emb_student = get_embedding(student_text)
    for text in others:
        if text:
            emb_other = get_embedding(text)
            if cosine_similarity(emb_student, emb_other) > threshold:
                return True
    return False
