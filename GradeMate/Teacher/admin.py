import os
from django.contrib import admin
from .models import Question, Subject, Classroom, Assignment, Notification
from .utils import find_students_for_classroom

# Register your models here.

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description_short']
    search_fields = ['name', 'code']
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['name', 'grade', 'section']
    list_filter = ['grade', 'section']
    search_fields = ['name', 'grade', 'section']


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


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'classroom', 'teacher', 'due_date', 'max_score', 'is_active', 'created_at', 'has_key_answer_text']
    list_filter = ['subject', 'classroom', 'is_active', 'created_at', 'due_date']
    search_fields = ['title', 'description', 'subject__name', 'classroom__name']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['extract_text_from_files']
    
    fieldsets = (
        ('Assignment Details', {
            'fields': ('title', 'description', 'subject', 'classroom', 'teacher')
        }),
        ('Answer Key', {
            'fields': ('key_answer_file', 'key_answer_text')
        }),
        ('Settings', {
            'fields': ('due_date', 'max_score', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_key_answer_text(self, obj):
        """Check if key answer text exists"""
        return bool(obj.key_answer_text)
    has_key_answer_text.boolean = True
    has_key_answer_text.short_description = 'Has Answer Text'
    
    def extract_text_from_files(self, request, queryset):
        """Admin action to extract text from key answer files"""
        from Student.services.ocr import extract_text_from_file
        success_count = 0
        error_count = 0
        
        for assignment in queryset:
            if assignment.key_answer_file:
                try:
                    file_path = assignment.key_answer_file.path
                    if file_path and os.path.exists(file_path):
                        extracted_text = extract_text_from_file(file_path)
                        if extracted_text:
                            assignment.key_answer_text = extracted_text
                            assignment.save(update_fields=['key_answer_text'])
                            success_count += 1
                        else:
                            error_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    print(f"⚠️ Error extracting text from {assignment.title}: {e}")
                    error_count += 1
            else:
                error_count += 1
        
        self.message_user(
            request,
            f'Successfully extracted text from {success_count} assignment(s). {error_count} assignment(s) had errors or no files.'
        )
    extract_text_from_files.short_description = 'Extract text from key answer files'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set on creation
            # Only set teacher if user is a teacher, otherwise let them select it
            if hasattr(request.user, 'role') and request.user.role == 'teacher':
                obj.teacher = request.user
            elif not obj.teacher:
                # If no teacher is set and user is not a teacher, set to first available teacher
                # or leave it to be set manually
                from USER.models import User
                teacher = User.objects.filter(role='teacher').first()
                if teacher:
                    obj.teacher = teacher
        
        # Save the assignment first (file will be saved by Django)
        super().save_model(request, obj, form, change)
        
        # Extract text from key answer file if provided and no text exists
        if obj.key_answer_file and not obj.key_answer_text:
            try:
                from Student.services.ocr import extract_text_from_file
                file_path = obj.key_answer_file.path
                if file_path and os.path.exists(file_path):
                    extracted_text = extract_text_from_file(file_path)
                    if extracted_text:
                        # Update the text field directly in database to avoid recursion
                        Assignment.objects.filter(pk=obj.pk).update(key_answer_text=extracted_text)
                        obj.key_answer_text = extracted_text  # Update instance for immediate use
            except Exception as e:
                import traceback
                print(f"⚠️ Could not extract text from key answer file: {e}")
                print(traceback.format_exc())
        
        # Create notifications for all students in the assigned classroom (only on creation)
        if not change and obj.is_active:
            students = find_students_for_classroom(obj.classroom)
            
            notification_count = 0
            for student in students:
                notification, created = Notification.objects.get_or_create(
                    assignment=obj,
                    student=student,
                    defaults={
                        'message': f"New assignment: {obj.title} in {obj.subject.name}. Due: {obj.due_date.strftime('%Y-%m-%d %H:%M')}"
                    }
                )
                if created:
                    notification_count += 1
            
            if notification_count == 0:
                print(f"⚠️ Warning: No students found for classroom '{obj.classroom.name}'. Students may not see this assignment.")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['assignment__title', 'student__name', 'message']
    readonly_fields = ['created_at']
