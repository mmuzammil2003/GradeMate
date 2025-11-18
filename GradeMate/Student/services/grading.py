from .ocr import get_embedding, cosine_similarity

def auto_grade(student_text, key_text):
    emb_student = get_embedding(student_text)
    emb_key = get_embedding(key_text)
    return round(cosine_similarity(emb_student, emb_key) * 100, 2)
