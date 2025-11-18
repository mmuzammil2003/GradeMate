from django.contrib import admin
from .models import StudentAnswer, StudentAssignment

# Register your models here.

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'question_id', 'score', 'uploaded_at', 'evaluated_at']
    list_filter = ['score', 'uploaded_at', 'evaluated_at', 'question']
    search_fields = ['student__name', 'student__username', 'answer_text', 'feedback']
    readonly_fields = ['uploaded_at', 'evaluated_at']
    
    fieldsets = (
        ('Answer Details', {
            'fields': ('student', 'question', 'answer_text')
        }),
        ('Evaluation Results', {
            'fields': ('score', 'feedback')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'evaluated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def question_id(self, obj):
        return f"Q{obj.question.id}"
    question_id.short_description = 'Question ID'


@admin.register(StudentAssignment)
class StudentAssignmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'score', 'is_graded', 'plagiarism', 'submitted_at', 'evaluated_at']
    list_filter = ['is_graded', 'plagiarism', 'submitted_at', 'evaluated_at', 'assignment__subject']
    search_fields = ['student__name', 'assignment__title', 'answer_text', 'feedback']
    readonly_fields = ['submitted_at', 'evaluated_at']
    
    fieldsets = (
        ('Submission Details', {
            'fields': ('student', 'assignment', 'file', 'answer_text')
        }),
        ('Evaluation Results', {
            'fields': ('score', 'feedback', 'is_graded', 'plagiarism')
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'evaluated_at'),
            'classes': ('collapse',)
        }),
    )
