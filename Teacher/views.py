from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView

class Dashboard(TemplateView):
    template_name="Teacher/dashboard.html"

class AssignmentForm(TemplateView):
    template_name="Teacher/assignment_form.html"

class AssignmentList(TemplateView):
    template_name="Teacher/assignment_list.html"

class SubmissionList(TemplateView):
    template_name="Teacher/submission_list.html"

    