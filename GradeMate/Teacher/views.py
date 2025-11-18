from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Question, Assignment, Subject, Classroom, Notification
from .forms import QuestionForm, AssignmentForm, SubmissionGradingForm
from .utils import find_students_for_classroom
from USER.models import User

class Dashboard(LoginRequiredMixin, TemplateView):
    template_name="Teacher/dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user
        
        # Get assignments
        assignments = Assignment.objects.filter(teacher=teacher)
        active_assignments = assignments.filter(is_active=True)
        
        # Statistics
        context['total_assignments_count'] = assignments.count()
        context['active_assignments'] = active_assignments.count()
        context['active_students_count'] = User.objects.filter(role='student').count()  # Total students
        context['recent_assignments'] = assignments.order_by('-created_at')[:5]
        
        # Get pending evaluations (submissions not yet graded)
        from Student.models import StudentAssignment
        pending_submissions = StudentAssignment.objects.filter(
            assignment__teacher=teacher,
            is_graded=False
        )
        context['pending_evaluations_count'] = pending_submissions.count()
        
        # Get assignments with pending evaluations
        assignment_ids_with_pending = pending_submissions.values_list('assignment_id', flat=True).distinct()
        context['pending_evaluation_assignments'] = Assignment.objects.filter(
            id__in=assignment_ids_with_pending
        )[:5]
        
        # Calculate average grade
        graded_submissions = StudentAssignment.objects.filter(
            assignment__teacher=teacher,
            is_graded=True
        )
        if graded_submissions.exists():
            total_score = sum(float(sub.score) for sub in graded_submissions)
            max_score = sum(float(sub.assignment.max_score) for sub in graded_submissions)
            context['average_grade'] = round((total_score / max_score * 100), 1) if max_score > 0 else 0
        else:
            context['average_grade'] = 0
        
        context['subjects'] = Subject.objects.all()
        context['classrooms'] = Classroom.objects.all()
        return context

class AssignmentFormView(LoginRequiredMixin, TemplateView):
    template_name="Teacher/assignment_form.html"

class AssignmentList(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = 'Teacher/assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 10
    
    def get_queryset(self):
        # Show all assignments for teachers, but prioritize own assignments
        if self.request.user.is_superuser:
            return Assignment.objects.all().order_by('-created_at')
        if hasattr(self.request.user, 'role') and self.request.user.role == 'teacher':
            # Show all assignments, but order by own assignments first
            own_assignments = Assignment.objects.filter(teacher=self.request.user)
            other_assignments = Assignment.objects.exclude(teacher=self.request.user)
            # Combine: own assignments first, then others
            return (own_assignments | other_assignments).distinct().order_by('-created_at')
        return Assignment.objects.filter(teacher=self.request.user).order_by('-created_at')

class SubmissionList(LoginRequiredMixin, ListView):
    template_name="Teacher/submission_list.html"
    context_object_name = 'submissions'
    paginate_by = 20
    
    def get_queryset(self):
        from Student.models import StudentAssignment
        # Get all submissions for assignments created by this teacher
        return StudentAssignment.objects.filter(
            assignment__teacher=self.request.user
        ).order_by('-submitted_at')

# Question CRUD Views
class QuestionListView(LoginRequiredMixin, ListView):
    model = Question
    template_name = 'Teacher/question_list.html'
    context_object_name = 'questions'
    paginate_by = 10
    
    def get_queryset(self):
        return Question.objects.all()

class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'Teacher/question_form.html'
    success_url = reverse_lazy('Teacher:question_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Question created successfully!')
        return super().form_valid(form)

class QuestionUpdateView(LoginRequiredMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'Teacher/question_form.html'
    success_url = reverse_lazy('Teacher:question_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Question updated successfully!')
        return super().form_valid(form)

class QuestionDeleteView(LoginRequiredMixin, DeleteView):
    model = Question
    template_name = 'Teacher/question_confirm_delete.html'
    success_url = reverse_lazy('Teacher:question_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Question deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Assignment CRUD Views
class AssignmentCreateView(LoginRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'Teacher/assignment_form.html'
    success_url = reverse_lazy('Teacher:assignment_list')
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user
        
        # Extract text from key answer file if provided
        if form.instance.key_answer_file and not form.instance.key_answer_text:
            try:
                from Student.services.ocr import extract_text_from_file
                file_path = form.instance.key_answer_file.path
                if file_path:
                    extracted_text = extract_text_from_file(file_path)
                    if extracted_text:
                        form.instance.key_answer_text = extracted_text
            except Exception as e:
                print(f"⚠️ Could not extract text from key answer file: {e}")
        
        response = super().form_valid(form)
        
        # Create notifications for all students in the assigned classroom
        assignment = form.instance
        students = find_students_for_classroom(assignment.classroom)
        
        notification_count = 0
        for student in students:
            notification, created = Notification.objects.get_or_create(
                assignment=assignment,
                student=student,
                defaults={
                    'message': f"New assignment: {assignment.title} in {assignment.subject.name}. Due: {assignment.due_date.strftime('%Y-%m-%d %H:%M')}"
                }
            )
            if created:
                notification_count += 1
        
        if notification_count > 0:
            messages.success(self.request, f'Assignment created and notifications sent to {notification_count} students!')
        else:
            messages.warning(self.request, f'Assignment created but no students found for classroom "{assignment.classroom.name}". Please check that students have matching class_grade.')
        return response

class AssignmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'Teacher/assignment_form.html'
    success_url = reverse_lazy('Teacher:assignment_list')
    
    def get_queryset(self):
        # Only allow editing assignments created by this teacher
        # Superusers can edit any assignment
        if self.request.user.is_superuser:
            return Assignment.objects.all()
        return Assignment.objects.filter(teacher=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Assignment updated successfully!')
        return super().form_valid(form)

class AssignmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Assignment
    template_name = 'Teacher/assignment_confirm_delete.html'
    success_url = reverse_lazy('Teacher:assignment_list')
    
    def get_queryset(self):
        # Only allow deleting assignments created by this teacher
        # Superusers can delete any assignment
        if self.request.user.is_superuser:
            return Assignment.objects.all()
        return Assignment.objects.filter(teacher=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Assignment deleted successfully!')
        return super().delete(request, *args, **kwargs)

class AssignmentDetailView(LoginRequiredMixin, DetailView):
    model = Assignment
    template_name = 'Teacher/assignment_detail.html'
    context_object_name = 'assignment'
    
    def get_queryset(self):
        # Allow all authenticated users in the teacher app to view any assignment
        # This fixes the issue where assignments created in admin might not be visible
        # The teacher app should be accessible only to teachers anyway (via URL routing)
        return Assignment.objects.all()
    
    def get_object(self, queryset=None):
        """
        Override to provide better error handling
        """
        if queryset is None:
            queryset = self.get_queryset()
        
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is None:
            raise AttributeError(
                "AssignmentDetailView must be called with a pk in the URLconf."
            )
        
        try:
            obj = queryset.get(pk=pk)
        except Assignment.DoesNotExist:
            # If not found in filtered queryset, check if it exists at all
            if Assignment.objects.filter(pk=pk).exists():
                # Assignment exists but user doesn't have permission
                from django.core.exceptions import PermissionDenied
                raise PermissionDenied("You don't have permission to view this assignment.")
            else:
                # Assignment doesn't exist
                from django.http import Http404
                raise Http404(f"No Assignment found matching the query (pk={pk})")
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from Student.models import StudentAssignment
        submissions = StudentAssignment.objects.filter(
            assignment=self.object
        ).order_by('-submitted_at')
        context['submissions'] = submissions
        
        # Use flexible matching to count students
        students = find_students_for_classroom(self.object.classroom)
        context['total_students'] = students.count()
        context['submitted_count'] = submissions.count()
        
        # Calculate pending count
        context['pending_count'] = max(0, context['total_students'] - context['submitted_count'])
        
        # Calculate average score if there are graded submissions
        graded_submissions = submissions.filter(is_graded=True)
        if graded_submissions.exists():
            total_score = sum(float(sub.score) for sub in graded_submissions)
            max_score = sum(float(sub.assignment.max_score) for sub in graded_submissions)
            context['average_score'] = round((total_score / max_score * 100), 1) if max_score > 0 else 0
        else:
            context['average_score'] = None
        
        return context

class SubmissionDetailView(LoginRequiredMixin, DetailView):
    template_name = 'Teacher/submission_detail.html'
    context_object_name = 'submission'
    
    def get_queryset(self):
        from Student.models import StudentAssignment
        return StudentAssignment.objects.filter(assignment__teacher=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submission = self.get_object()
        context['form'] = SubmissionGradingForm(instance=submission)
        return context
    
    def post(self, request, *args, **kwargs):
        submission = self.get_object()
        form = SubmissionGradingForm(request.POST, instance=submission)
        
        if form.is_valid():
            submission = form.save(commit=False)
            submission.is_graded = True
            submission.evaluated_at = timezone.now()
            submission.save()
            messages.success(request, 'Grade saved successfully!')
            return redirect('Teacher:submission_detail', pk=submission.pk)
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(request, self.template_name, context)
