from django.contrib import admin
from .models import Question

# Register your models here.

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'question_text_short', 'model_answer_short', 'created_by', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['question_text', 'model_answer']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Question Details', {
            'fields': ('question_text', 'model_answer')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def question_text_short(self, obj):
        return obj.question_text[:100] + '...' if len(obj.question_text) > 100 else obj.question_text
    question_text_short.short_description = 'Question Text'
    
    def model_answer_short(self, obj):
        return obj.model_answer[:100] + '...' if len(obj.model_answer) > 100 else obj.model_answer
    model_answer_short.short_description = 'Model Answer'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
