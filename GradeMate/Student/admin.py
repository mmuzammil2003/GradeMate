from django.contrib import admin
from .models import StudentAnswer

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
