from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from .models import StudentAnswer
from .forms import StudentAnswerForm
from .services.ai_evaluator import evaluate_answer

# Create your views here.

class Dashboard(TemplateView):
    template_name="Student/dashboard.html"

class AssignmentView(TemplateView):
    template_name="Student/assignment_view.html"

class ResultDetail(TemplateView):
    template_name="Student/result_detail.html"

class ResultList(TemplateView):
    template_name="Student/result_list.html"

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
                return redirect('result_detail', answer_id=student_answer.id)
                
            except Exception as e:
                messages.error(request, f'Error during evaluation: {str(e)}')
                return redirect('upload_answer')
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(request, self.template_name, context)

class ResultView(LoginRequiredMixin, TemplateView):
    template_name = 'Student/result.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        answer_id = self.kwargs.get('answer_id')
        student_answer = get_object_or_404(
            StudentAnswer,
            id=answer_id,
            student=self.request.user
        )
        context['student_answer'] = student_answer
        return context
