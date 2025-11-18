from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Question
from .forms import QuestionForm

class Dashboard(TemplateView):
    template_name="Teacher/dashboard.html"

class AssignmentForm(TemplateView):
    template_name="Teacher/assignment_form.html"

class AssignmentList(TemplateView):
    template_name="Teacher/assignment_list.html"

class SubmissionList(TemplateView):
    template_name="Teacher/submission_list.html"

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
    success_url = reverse_lazy('question_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Question created successfully!')
        return super().form_valid(form)

class QuestionUpdateView(LoginRequiredMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'Teacher/question_form.html'
    success_url = reverse_lazy('question_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Question updated successfully!')
        return super().form_valid(form)

class QuestionDeleteView(LoginRequiredMixin, DeleteView):
    model = Question
    template_name = 'Teacher/question_confirm_delete.html'
    success_url = reverse_lazy('question_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Question deleted successfully!')
        return super().delete(request, *args, **kwargs)

    