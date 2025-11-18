# AI-Based Evaluation System - Setup Notes

## Installation

1. Install required packages:
```bash
pip install sentence-transformers>=2.0.0 transformers>=4.0.0 torch>=1.9.0 Pillow>=8.0.0 numpy>=1.21.0
```

2. (Optional) Set Hugging Face Token for private models:
```bash
# Windows PowerShell
$env:HF_TOKEN="your-hf-token-here"
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

## URL Routes

- **Teacher Questions**: `/Teacher/questions/` - List all questions
- **Create Question**: `/Teacher/questions/create/`
- **Update Question**: `/Teacher/questions/<id>/update/`
- **Delete Question**: `/Teacher/questions/<id>/delete/`
- **Student Upload**: `/Student/upload/` - Upload answer
- **Student Result**: `/Student/result/<answer_id>/` - View evaluation result

## Features Implemented

1. **Teacher App**:
   - Question model with `question_text` and `model_answer`
   - Full CRUD operations for questions
   - Admin panel registration

2. **Student App**:
   - StudentAnswer model with score and feedback
   - Upload answer form
   - AI-based automatic evaluation
   - Result display page

3. **AI Evaluation**:
   - Uses sentence transformers (embedding-based similarity)
   - Calculates semantic similarity between student and model answers
   - Converts similarity to score (0-10) with automatic feedback
   - Graceful error handling

## Notes

- Students can only submit one answer per question (enforced by database constraint)
- If a student submits again for the same question, their previous answer is updated
- Evaluation happens synchronously upon submission using embedding-based similarity
- Uses sentence-transformers model (all-MiniLM-L6-v2) for semantic comparison
- Score is calculated based on cosine similarity between answer embeddings
- Feedback is automatically generated based on the similarity score

