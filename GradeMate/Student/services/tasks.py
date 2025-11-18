from celery import shared_task
from Student.models import StudentAssignment
from services.ocr import extract_text_from_file
from services.grading import auto_grade
from services.plagiarism import check_plagiarism
import os

@shared_task
def process_submission(submission_id):
    """
    Process a student submission:
    1. Extract text from uploaded file if needed
    2. Auto-grade if answer key exists
    3. Check for plagiarism
    """
    try:
        submission = StudentAssignment.objects.get(id=submission_id)
        text = submission.answer_text

        # Extract text from file if file exists and no text is present
        if submission.file and (not text or not text.strip()):
            try:
                file_path = submission.file.path
                if os.path.exists(file_path):
                    print(f"📄 Extracting text from file: {file_path}")
                    text = extract_text_from_file(file_path)
                    if text and text.strip():
                        submission.answer_text = text
                        print(f"✅ Extracted text: {len(text)} characters")
                    else:
                        print(f"⚠️ No text extracted from file")
                else:
                    print(f"⚠️ File not found at path: {file_path}")
            except Exception as e:
                print(f"❌ Error extracting text from file: {e}")
                # Continue processing even if OCR fails
        
        # Update text variable after extraction
        text = submission.answer_text
        
        # Auto-grade if answer key exists and we have text
        if submission.assignment.answer_key and text and text.strip():
            try:
                answer_key_path = submission.assignment.answer_key.path
                if os.path.exists(answer_key_path):
                    print(f"📝 Extracting text from answer key: {answer_key_path}")
                    key_text = extract_text_from_file(answer_key_path)
                    if key_text and key_text.strip():
                        score = auto_grade(text, key_text)
                        submission.score = int(round(score))
                        submission.is_graded = True
                        print(f"✅ Graded submission: {submission.score}/100")
                    else:
                        print(f"⚠️ Could not extract text from answer key")
                else:
                    print(f"⚠️ Answer key file not found at path: {answer_key_path}")
            except Exception as e:
                print(f"❌ Error during auto-grading: {e}")
        
        # Check for plagiarism if we have text
        if text and text.strip():
            try:
                others = StudentAssignment.objects.filter(
                    assignment=submission.assignment
                ).exclude(id=submission.id).exclude(answer_text__isnull=True).exclude(answer_text='').values_list('answer_text', flat=True)
                
                if others:
                    plagiarism_detected = check_plagiarism(text, list(others))
                    submission.plagiarism = plagiarism_detected
                    if plagiarism_detected:
                        print(f"⚠️ Plagiarism detected for submission {submission.id}")
                    else:
                        print(f"✅ No plagiarism detected")
                else:
                    submission.plagiarism = False
            except Exception as e:
                print(f"❌ Error during plagiarism check: {e}")
        
        submission.save()
        print(f"✅ Successfully processed submission {submission.id}")
        
    except StudentAssignment.DoesNotExist:
        print(f"❌ Submission {submission_id} not found")
    except Exception as e:
        print(f"❌ Error processing submission {submission_id}: {e}")
        raise