import os
import numpy as np
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from sentence_transformers import SentenceTransformer

# Try to get HF token from environment, fallback to None
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize models with error handling
try:
    if HF_TOKEN:
        processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-handwritten", token=HF_TOKEN)
        ocr_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-handwritten", token=HF_TOKEN)
        embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", token=HF_TOKEN)
        print("✅ Using Hugging Face Hub models with token")
    else:
        processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-handwritten")
        ocr_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-handwritten")
        embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        print("✅ Using local models")
except Exception as e:
    print(f"⚠️ Error loading models: {e}")
    processor = None
    ocr_model = None
    embedding_model = None

def extract_text_from_file(path):
    """
    Extract text from an image file using OCR.
    Supports various image formats (PNG, JPG, JPEG, WEBP, etc.)
    """
    if not processor or not ocr_model:
        raise Exception("OCR models not loaded. Please check model initialization.")
    
    try:
        # Open and convert image to RGB
        image = Image.open(path).convert("RGB")
        pixel_values = processor(image, return_tensors="pt").pixel_values
        generated_ids = ocr_model.generate(pixel_values)
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return generated_text.strip()
    except Exception as e:
        print(f"❌ OCR error for file {path}: {e}")
        raise Exception(f"Failed to extract text from file: {str(e)}")

def get_embedding(text):
    """
    Get embedding vector for text using sentence transformer.
    """
    if not embedding_model:
        raise Exception("Embedding model not loaded. Please check model initialization.")
    
    if not text or not text.strip():
        # Return zero vector if text is empty
        return [0.0] * 384
    
    try:
        embedding = embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        # Return zero vector as fallback
        return [0.0] * 384

def cosine_similarity(vec1, vec2):
    """
    Calculate cosine similarity between two vectors.
    Returns a value between 0 and 1.
    """
    v1, v2 = np.array(vec1), np.array(vec2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(np.dot(v1, v2) / (norm1 * norm2))
