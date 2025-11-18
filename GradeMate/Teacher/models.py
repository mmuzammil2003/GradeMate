from django.db import models
from django.core.validators import FileExtensionValidator
from USER.models import User

# Create your models here.

class Subject(models.Model):
    """Subject model (e.g., Mathematics, Science, English)"""
    name = models.CharField(max_length=100, unique=True, help_text="Subject name (e.g., Mathematics, Science)")
    code = models.CharField(max_length=10, unique=True, help_text="Subject code (e.g., MATH, SCI)")
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Classroom(models.Model):
    """Classroom/Class model (e.g., Grade 10-A, Grade 10-B)"""
    name = models.CharField(max_length=50, unique=True, help_text="Class name (e.g., Grade 10-A)")
    grade = models.CharField(max_length=10, help_text="Grade level (e.g., 10, 11)")
    section = models.CharField(max_length=10, blank=True, help_text="Section (e.g., A, B)")
    
    class Meta:
        ordering = ['grade', 'section']
        verbose_name = "Classroom"
        verbose_name_plural = "Classrooms"
    
    def __str__(self):
        return self.name


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


class Assignment(models.Model):
    """Assignment model for teachers to assign to classes"""
    title = models.CharField(max_length=200, help_text="Assignment title")
    description = models.TextField(help_text="Assignment description/instructions")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments', limit_choices_to={'role': 'teacher'})
    key_answer_file = models.FileField(
        upload_to='assignments/key_answers/',
        help_text="Upload the key answer file (PDF, DOC, TXT)",
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt'])]
    )
    key_answer_text = models.TextField(blank=True, help_text="Key answer text (extracted from file or manually entered)")
    due_date = models.DateTimeField(help_text="Assignment due date")
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=10.0, help_text="Maximum score")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Is assignment active?")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"
    
    def __str__(self):
        return f"{self.title} - {self.classroom.name} ({self.subject.name})"


class Notification(models.Model):
    """Notification model to notify students about new assignments"""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='notifications')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', limit_choices_to={'role': 'student'})
    message = models.TextField(help_text="Notification message")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        unique_together = ['assignment', 'student']
    
    def __str__(self):
        return f"Notification for {self.student.name} - {self.assignment.title}"
