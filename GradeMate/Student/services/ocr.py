import os
import numpy as np
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from sentence_transformers import SentenceTransformer
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PyPDF2 not available. PDF text extraction will not work.")

# Try to get HF token from environment, fallback to None
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize models with lazy loading
processor = None
ocr_model = None
embedding_model = None
_embedding_model_loading = False

def _load_embedding_model():
    """Lazy load the embedding model on first use."""
    global embedding_model, _embedding_model_loading
    
    if embedding_model is not None:
        return embedding_model
    
    if _embedding_model_loading:
        # Model is currently loading, wait a bit
        import time
        for _ in range(10):  # Wait up to 5 seconds
            time.sleep(0.5)
            if embedding_model is not None:
                return embedding_model
        raise Exception("Model loading timeout. Please try again.")
    
    _embedding_model_loading = True
    try:
        print("🔄 Loading embedding model (this may take a moment on first use)...")
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        
        # Try loading with retry
        max_retries = 2
        for attempt in range(max_retries):
            try:
                if HF_TOKEN:
                    print(f"   Attempt {attempt + 1}/{max_retries}: Loading with HF token...")
                    embedding_model = SentenceTransformer(model_name, token=HF_TOKEN)
                else:
                    print(f"   Attempt {attempt + 1}/{max_retries}: Loading from local cache or downloading...")
                    embedding_model = SentenceTransformer(model_name)
                
                print("✅ Embedding model loaded successfully!")
                _embedding_model_loading = False
                return embedding_model
            except Exception as load_error:
                if attempt < max_retries - 1:
                    print(f"   ⚠️ Attempt {attempt + 1} failed: {load_error}. Retrying...")
                    import time
                    time.sleep(2)  # Wait before retry
                else:
                    raise load_error
                    
    except ImportError as e:
        _embedding_model_loading = False
        embedding_model = None
        raise Exception(f"sentence-transformers package not installed. Please run: pip install sentence-transformers")
    except Exception as e:
        print(f"❌ Error loading embedding model: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        _embedding_model_loading = False
        embedding_model = None
        error_msg = str(e)
        if "Connection" in error_msg or "network" in error_msg.lower() or "download" in error_msg.lower():
            raise Exception(f"Failed to download/load embedding model: {error_msg}. Please check your internet connection and try again.")
        else:
            raise Exception(f"Failed to load embedding model: {error_msg}. Please ensure sentence-transformers is properly installed: pip install sentence-transformers")

def _load_ocr_models():
    """Lazy load OCR models on first use."""
    global processor, ocr_model
    
    if processor is not None and ocr_model is not None:
        return processor, ocr_model
    
    try:
        print("🔄 Loading OCR models...")
        if HF_TOKEN:
            processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-handwritten", token=HF_TOKEN)
            ocr_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-handwritten", token=HF_TOKEN)
            print("✅ OCR models loaded (with HF token)")
        else:
            processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-handwritten")
            ocr_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-handwritten")
            print("✅ OCR models loaded (local)")
        return processor, ocr_model
    except Exception as e:
        print(f"❌ Error loading OCR models: {e}")
        processor = None
        ocr_model = None
        raise Exception(f"Failed to load OCR models: {str(e)}")

def extract_text_from_file(path):
    """
    Extract text from a file using OCR or PDF extraction.
    Supports various image formats (PNG, JPG, JPEG, WEBP, etc.) and PDF files.
    """
    file_extension = os.path.splitext(path)[1].lower()
    
    # Handle PDF files
    if file_extension == '.pdf':
        if not PDF_AVAILABLE:
            raise Exception("PyPDF2 is not installed. Cannot extract text from PDF files.")
        
        try:
            text = ""
            with open(path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"❌ PDF extraction error for file {path}: {e}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    # Handle image files with OCR
    try:
        _load_ocr_models()
    except Exception as e:
        raise Exception(f"OCR models not available: {str(e)}")
    
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
    Uses lazy loading to load the model on first use.
    """
    # Load model if not already loaded
    try:
        model = _load_embedding_model()
    except Exception as e:
        print(f"❌ Failed to load embedding model: {e}")
        raise Exception(f"Embedding model not available: {str(e)}. Please ensure sentence-transformers is installed: pip install sentence-transformers")
    
    if not text or not text.strip():
        # Return zero vector if text is empty
        return [0.0] * 384
    
    try:
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        import traceback
        traceback.print_exc()
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
