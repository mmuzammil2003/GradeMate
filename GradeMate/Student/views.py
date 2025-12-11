import os
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from .models import StudentAnswer, StudentAssignment
from .forms import StudentAnswerForm, AssignmentSubmissionForm
from Teacher.models import Assignment, Subject, Classroom, Notification
from Teacher.utils import find_students_for_classroom
from .services.ai_evaluator import evaluate_answer
from .services.ocr import extract_text_from_file
from .services.plagiarism import check_plagiarism

# Create your views here.

class Dashboard(LoginRequiredMixin, TemplateView):
    template_name="Student/dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user
        
        # Get assignments for student using flexible matching
        # Method 1: Get assignments where student has notifications (most reliable)
        notification_assignments = Assignment.objects.filter(
            notifications__student=student,
            is_active=True
        ).distinct()
        
        # Method 2: Get assignments by matching student's class_grade with classroom names
        student_class = student.class_grade
        classroom_assignments = Assignment.objects.none()
        
        if student_class:
            student_class = student_class.strip()
            # Try exact match first
            classroom_assignments = Assignment.objects.filter(
                classroom__name__iexact=student_class,
                is_active=True
            )
            
            # Also try matching by checking if student would be found for each classroom
            all_classrooms = Classroom.objects.all()
            matching_classroom_ids = []
            for classroom in all_classrooms:
                students_in_classroom = find_students_for_classroom(classroom)
                if student in students_in_classroom:
                    matching_classroom_ids.append(classroom.id)
            
            if matching_classroom_ids:
                additional_assignments = Assignment.objects.filter(
                    classroom__id__in=matching_classroom_ids,
                    is_active=True
                )
                classroom_assignments = (classroom_assignments | additional_assignments).distinct()
        
        # Combine both methods - notifications take priority but include classroom matches too
        assignments = (notification_assignments | classroom_assignments).distinct().order_by('-created_at')
        
        # Get student's submissions
        submissions = StudentAssignment.objects.filter(student=student)
        submitted_assignment_ids = submissions.values_list('assignment_id', flat=True)
        
        # Statistics
        context['total_assignments_count'] = assignments.count()
        context['pending_assignments_count'] = assignments.exclude(
            id__in=submitted_assignment_ids
        ).count()
        context['completed_assignments_count'] = submissions.filter(is_graded=True).count()
        
        # Calculate average score
        graded_submissions = submissions.filter(is_graded=True)
        if graded_submissions.exists():
            total_score = sum(float(sub.score) for sub in graded_submissions)
            max_score = sum(float(sub.assignment.max_score) for sub in graded_submissions)
            context['average_score'] = round((total_score / max_score * 100), 1) if max_score > 0 else 0
        else:
            context['average_score'] = 0
        
        # Upcoming assignments (not yet submitted)
        context['upcoming_assignments'] = assignments.exclude(
            id__in=submitted_assignment_ids
        ).order_by('due_date')[:5]
        
        # Recent results (graded submissions)
        context['recent_results'] = graded_submissions.order_by('-evaluated_at')[:5]
        
        # Get unread notifications
        context['notifications'] = Notification.objects.filter(
            student=student,
            is_read=False
        ).order_by('-created_at')[:5]
        
        context['subjects'] = Subject.objects.all()
        if student_class:
            context['teachers'] = Assignment.objects.filter(
                classroom__name__iexact=student_class
            ).values_list('teacher__name', 'teacher__id', 'subject__name').distinct()
        else:
            context['teachers'] = []
        
        # Debug information (can be removed in production)
        context['debug_student_class'] = student_class
        context['debug_assignments_count'] = assignments.count()
        
        return context

class AssignmentView(LoginRequiredMixin, ListView):
    template_name="Student/assignment_view.html"
    context_object_name = 'assignments'
    paginate_by = 10
    
    def get_queryset(self):
        student = self.request.user
        student_class = student.class_grade
        
        # Filter by subject if provided
        subject_id = self.request.GET.get('subject')
        
        # Get assignments using flexible matching (same as dashboard)
        # Method 1: Get assignments where student has notifications
        notification_assignments = Assignment.objects.filter(
            notifications__student=student,
            is_active=True
        ).distinct()
        
        # Method 2: Get assignments by matching student's class_grade with classroom names
        classroom_assignments = Assignment.objects.none()
        
        if student_class:
            student_class = student_class.strip()
            # Try exact match first
            classroom_assignments = Assignment.objects.filter(
                classroom__name__iexact=student_class,
                is_active=True
            )
            
            # Also try matching by checking if student would be found for each classroom
            all_classrooms = Classroom.objects.all()
            matching_classroom_ids = []
            for classroom in all_classrooms:
                students_in_classroom = find_students_for_classroom(classroom)
                if student in students_in_classroom:
                    matching_classroom_ids.append(classroom.id)
            
            if matching_classroom_ids:
                additional_assignments = Assignment.objects.filter(
                    classroom__id__in=matching_classroom_ids,
                    is_active=True
                )
                classroom_assignments = (classroom_assignments | additional_assignments).distinct()
        
        # Combine both methods
        queryset = (notification_assignments | classroom_assignments).distinct()
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get submitted assignment IDs for this student
        submitted_ids = StudentAssignment.objects.filter(
            student=self.request.user
        ).values_list('assignment_id', flat=True)
        context['submitted_ids'] = list(submitted_ids)
        context['subjects'] = Subject.objects.all()
        return context

class ResultDetail(LoginRequiredMixin, DetailView):
    template_name="Student/result_detail.html"
    context_object_name = 'submission'
    
    def get_queryset(self):
        return StudentAssignment.objects.filter(student=self.request.user)

class ResultList(LoginRequiredMixin, ListView):
    template_name="Student/result_list.html"
    context_object_name = 'submissions'
    paginate_by = 10
    
    def get_queryset(self):
        return StudentAssignment.objects.filter(
            student=self.request.user,
            is_graded=True
        ).order_by('-evaluated_at')

# AI Evaluation Views
class UploadAnswerView(LoginRequiredMixin, TemplateView):
    template_name = 'Student/upload.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = StudentAnswerForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = StudentAnswerForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data['question']
            answer_text = form.cleaned_data['answer_text']
            
            # Check if student already answered this question
            existing_answer = StudentAnswer.objects.filter(
                question=question,
                student=request.user
            ).first()
            
            if existing_answer:
                # Update existing answer
                student_answer = existing_answer
                student_answer.answer_text = answer_text
            else:
                # Create new answer
                student_answer = form.save(commit=False)
                student_answer.student = request.user
            
            # Save the answer first
            student_answer.save()
            
            # Evaluate using AI
            try:
                evaluation_result = evaluate_answer(
                    model_answer=question.model_answer,
                    student_answer=answer_text
                )
                
                # Update student answer with evaluation results
                student_answer.score = evaluation_result['score']
                student_answer.feedback = evaluation_result['feedback']
                student_answer.evaluated_at = timezone.now()
                student_answer.save()
                
                # Redirect to result page
                return redirect('Student:result_detail', pk=student_answer.pk)
                
            except Exception as e:
                messages.error(request, f'Error during evaluation: {str(e)}')
                return redirect('Student:upload_answer')
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(request, self.template_name, context)

class ResultView(LoginRequiredMixin, DetailView):
    template_name = 'Student/result.html'
    context_object_name = 'student_answer'
    
    def get_queryset(self):
        return StudentAnswer.objects.filter(student=self.request.user)

# Assignment Submission Views
class AssignmentDetailView(LoginRequiredMixin, DetailView):
    model = Assignment
    template_name = 'Student/assignment_detail.html'
    context_object_name = 'assignment'
    
    def get_queryset(self):
        student = self.request.user
        # Get assignments using flexible matching
        # Method 1: Get assignments where student has notifications
        notification_assignments = Assignment.objects.filter(
            notifications__student=student,
            is_active=True
        ).distinct()
        
        # Method 2: Get assignments by matching student's class_grade with classroom names
        classroom_assignments = Assignment.objects.none()
        student_class = student.class_grade
        
        if student_class:
            student_class = student_class.strip()
            # Try exact match first
            classroom_assignments = Assignment.objects.filter(
                classroom__name__iexact=student_class,
                is_active=True
            )
            
            # Also try matching by checking if student would be found for each classroom
            all_classrooms = Classroom.objects.all()
            matching_classroom_ids = []
            for classroom in all_classrooms:
                students_in_classroom = find_students_for_classroom(classroom)
                if student in students_in_classroom:
                    matching_classroom_ids.append(classroom.id)
            
            if matching_classroom_ids:
                additional_assignments = Assignment.objects.filter(
                    classroom__id__in=matching_classroom_ids,
                    is_active=True
                )
                classroom_assignments = (classroom_assignments | additional_assignments).distinct()
        
        # Combine both methods
        return (notification_assignments | classroom_assignments).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if student has already submitted
        submission = StudentAssignment.objects.filter(
            assignment=self.object,
            student=self.request.user
        ).first()
        context['submission'] = submission
        context['form'] = AssignmentSubmissionForm(instance=submission)
        return context

class SubmitAssignmentView(LoginRequiredMixin, TemplateView):
    template_name = 'Student/submit_assignment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignment_id = self.kwargs.get('assignment_id')
        student = self.request.user
        
        # Get assignment using flexible matching
        try:
            assignment = Assignment.objects.get(id=assignment_id, is_active=True)
        except Assignment.DoesNotExist:
            from django.http import Http404
            raise Http404("Assignment not found")
        
        # Verify student has access to this assignment
        has_notification = Notification.objects.filter(
            assignment=assignment,
            student=student
        ).exists()
        
        has_classroom_access = False
        if student.class_grade:
            students_in_classroom = find_students_for_classroom(assignment.classroom)
            has_classroom_access = student in students_in_classroom
        
        if not (has_notification or has_classroom_access):
            from django.http import Http404
            raise Http404("You don't have access to this assignment")
        context['assignment'] = assignment
        
        # Check if already submitted
        existing_submission = StudentAssignment.objects.filter(
            assignment=assignment,
            student=self.request.user
        ).first()
        
        context['form'] = AssignmentSubmissionForm(instance=existing_submission)
        return context
    
    def post(self, request, *args, **kwargs):
        assignment_id = self.kwargs.get('assignment_id')
        student = request.user
        
        # Get assignment using flexible matching
        try:
            assignment = Assignment.objects.get(id=assignment_id, is_active=True)
        except Assignment.DoesNotExist:
            from django.http import Http404
            raise Http404("Assignment not found")
        
        # Verify student has access to this assignment
        has_notification = Notification.objects.filter(
            assignment=assignment,
            student=student
        ).exists()
        
        has_classroom_access = False
        if student.class_grade:
            students_in_classroom = find_students_for_classroom(assignment.classroom)
            has_classroom_access = student in students_in_classroom
        
        if not (has_notification or has_classroom_access):
            from django.http import Http404
            raise Http404("You don't have access to this assignment")
        
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Check if already submitted
            existing_submission = StudentAssignment.objects.filter(
                assignment=assignment,
                student=request.user
            ).first()
            
            if existing_submission:
                submission = existing_submission
                # Update existing submission
                if form.cleaned_data['file']:
                    submission.file = form.cleaned_data['file']
                if form.cleaned_data['answer_text']:
                    submission.answer_text = form.cleaned_data['answer_text']
            else:
                submission = form.save(commit=False)
                submission.assignment = assignment
                submission.student = request.user
            
            # Save the submission first so the file is written to disk
            submission.save()
            
            # Extract text from student's file if provided and no text exists
            if submission.file and not submission.answer_text:
                try:
                    # Now we can access the file path after saving
                    file_path = submission.file.path
                    if os.path.exists(file_path):
                        extracted_text = extract_text_from_file(file_path)
                        if extracted_text and extracted_text.strip():
                            submission.answer_text = extracted_text
                            # Save again with extracted text
                            submission.save(update_fields=['answer_text'])
                    else:
                        messages.warning(request, f'File not found at {file_path}. Please try uploading again.')
                except Exception as e:
                    messages.warning(request, f'Could not extract text from file: {str(e)}. Please enter text manually.')
            
            # Ensure we have key answer text - extract from file if needed
            key_answer_text = assignment.key_answer_text
            if not key_answer_text and assignment.key_answer_file:
                try:
                    key_file_path = assignment.key_answer_file.path
                    if os.path.exists(key_file_path):
                        key_answer_text = extract_text_from_file(key_file_path)
                        if key_answer_text and key_answer_text.strip():
                            # Save extracted text to assignment for future use
                            Assignment.objects.filter(pk=assignment.pk).update(key_answer_text=key_answer_text)
                            assignment.key_answer_text = key_answer_text
                except Exception as e:
                    print(f"⚠️ Could not extract text from key answer file: {e}")
            
            # Check for duplicate/plagiarized submissions before grading
            if submission.answer_text and submission.answer_text.strip():
                other_answers_qs = StudentAssignment.objects.filter(
                    assignment=assignment
                ).exclude(id=submission.id).exclude(
                    answer_text__isnull=True
                ).exclude(
                    answer_text__exact=''
                )
                
                if other_answers_qs.exists():
                    other_answers = list(other_answers_qs.values_list('answer_text', flat=True))
                    try:
                        if check_plagiarism(submission.answer_text, other_answers):
                            submission.plagiarism = True
                            submission.is_graded = False
                            submission.score = 0
                            submission.feedback = ''
                            submission.evaluated_at = None
                            submission.save(update_fields=['plagiarism', 'is_graded', 'score', 'feedback', 'evaluated_at'])
                            
                            messages.error(
                                request,
                                'Submission rejected because it matches another student\'s submission. Please submit your own work.'
                            )
                            return redirect('Student:assignment_detail', pk=assignment.pk)
                    except Exception as e:
                        print(f"⚠️ Error during plagiarism check for submission {submission.pk}: {e}")
                        # Continue with evaluation but mark as not graded yet
            
            # Evaluate using AI if we have both key answer and student answer
            if key_answer_text and key_answer_text.strip() and submission.answer_text and submission.answer_text.strip():
                try:
                    print(f"🤖 Starting AI evaluation for submission {submission.pk}")
                    evaluation_result = evaluate_answer(
                        model_answer=key_answer_text,
                        student_answer=submission.answer_text
                    )
                    
                    # Convert score from 0-10 to 0-max_score scale
                    max_score = float(assignment.max_score)
                    raw_score = float(evaluation_result['score'])
                    scaled_score = (raw_score / 10.0) * max_score
                    
                    submission.score = round(scaled_score, 2)
                    submission.feedback = evaluation_result['feedback']
                    submission.is_graded = True
                    submission.evaluated_at = timezone.now()
                    submission.save()
                    
                    print(f"✅ Evaluation complete: Score {submission.score}/{max_score}")
                    messages.success(request, f'Assignment submitted and evaluated successfully! Your score: {submission.score}/{max_score}')
                    return redirect('Student:assignment_result', pk=submission.pk)
                    
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    print(f"❌ Error during evaluation: {e}")
                    print(f"Error details: {error_details}")
                    messages.error(request, f'Error during evaluation: {str(e)}. Please contact your teacher.')
                    submission.is_graded = False
                    submission.save()
            elif not key_answer_text or not key_answer_text.strip():
                messages.warning(request, 'Assignment submitted successfully! However, automatic grading is not available as no answer key is provided.')
                return redirect('Student:assignment_detail', pk=assignment.pk)
            elif not submission.answer_text or not submission.answer_text.strip():
                messages.warning(request, 'Assignment submitted successfully! However, automatic grading requires text content. Please ensure your file contains text or enter text manually.')
                return redirect('Student:assignment_detail', pk=assignment.pk)
            
            # If we reach here, something unexpected happened
            messages.info(request, 'Assignment submitted successfully!')
            return redirect('Student:assignment_detail', pk=assignment.pk)
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(request, self.template_name, context)

class AssignmentResultView(LoginRequiredMixin, DetailView):
    template_name = 'Student/assignment_result.html'
    context_object_name = 'submission'
    
    def get_queryset(self):
        return StudentAssignment.objects.filter(student=self.request.user)

class NotificationListView(LoginRequiredMixin, ListView):
    template_name = 'Student/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(
            student=self.request.user
        ).order_by('-created_at')
    
    def post(self, request, *args, **kwargs):
        # Mark notification as read
        notification_id = request.POST.get('notification_id')
        if notification_id:
            notification = get_object_or_404(
                Notification,
                id=notification_id,
                student=request.user
            )
            notification.is_read = True
            notification.save()
            messages.success(request, 'Notification marked as read.')
        return redirect('Student:notifications')
