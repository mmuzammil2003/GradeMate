from django.db import models
from USER.models import User
from Teacher.models import Question

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
