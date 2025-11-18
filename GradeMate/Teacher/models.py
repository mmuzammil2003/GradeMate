from django.db import models
from USER.models import User

# Create your models here.

class Question(models.Model):
    question_text = models.TextField(help_text="The question to be answered by students")
    model_answer = models.TextField(help_text="The model/expected answer for AI evaluation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_questions', null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Question"
        verbose_name_plural = "Questions"
    
    def __str__(self):
        return f"Question {self.id}: {self.question_text[:50]}..."
