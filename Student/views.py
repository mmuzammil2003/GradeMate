from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.

class Dashboard(TemplateView):
    template_name="Student/dashboard.html"

class AssignmentView(TemplateView):
    template_name="Student/assignment_view.html"

class ResultDetail(TemplateView):
    template_name="Student/result_detail.html"

class ResultList(TemplateView):
    template_name="Student/result_list.html"
