from django.db import models
from django.core.validators import FileExtensionValidator
from USER.models import User
from Teacher.models import Question, Assignment

# Create your models here.

class StudentAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_answers')
    answer_text = models.TextField(help_text="Student's answer")
    score = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, help_text="Score out of 10")
    feedback = models.TextField(blank=True, help_text="AI-generated feedback")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    evaluated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Student Answer"
        verbose_name_plural = "Student Answers"
        constraints = [
            models.UniqueConstraint(fields=['question', 'student'], name='unique_student_question_answer')
        ]
    
    def __str__(self):
        return f"{self.student.name} - Question {self.question.id} - Score: {self.score}/10"


class StudentAssignment(models.Model):
    """Student submission for assignments - supports file uploads"""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_submissions', limit_choices_to={'role': 'student'})
    file = models.FileField(
        upload_to='assignments/submissions/',
        blank=True,
        null=True,
        help_text="Upload your answer file (PDF, DOC, images)",
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'webp'])]
    )
    answer_text = models.TextField(blank=True, help_text="Answer text (extracted from file or manually entered)")
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="Score received")
    feedback = models.TextField(blank=True, help_text="AI-generated feedback")
    submitted_at = models.DateTimeField(auto_now_add=True)
    evaluated_at = models.DateTimeField(null=True, blank=True)
    is_graded = models.BooleanField(default=False)
    plagiarism = models.BooleanField(default=False, help_text="Plagiarism detected")
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Student Assignment"
        verbose_name_plural = "Student Assignments"
        unique_together = ['assignment', 'student']
    
    def __str__(self):
        return f"{self.student.name} - {self.assignment.title} - Score: {self.score}/{self.assignment.max_score}"
