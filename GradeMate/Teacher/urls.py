from django.urls import path
from . import views

app_name = 'Teacher'

urlpatterns = [
    path("dashboard/",views.Dashboard.as_view(),name="Tdashboard"),
    path("AssignmentForm/",views.AssignmentFormView.as_view(),name="TAssignment"),
    path("AssignmentList/",views.AssignmentList.as_view(),name="assignment_list"),
    path("SubmissionList/",views.SubmissionList.as_view(),name="TSubmissionList"),
    # Assignment CRUD URLs
    path("assignments/create/",views.AssignmentCreateView.as_view(),name="assignment_create"),
    path("assignments/<int:pk>/",views.AssignmentDetailView.as_view(),name="assignment_detail"),
    path("assignments/<int:pk>/update/",views.AssignmentUpdateView.as_view(),name="assignment_update"),
    path("assignments/<int:pk>/delete/",views.AssignmentDeleteView.as_view(),name="assignment_delete"),
    path("submissions/<int:pk>/",views.SubmissionDetailView.as_view(),name="submission_detail"),
    # Question CRUD URLs
    path("questions/",views.QuestionListView.as_view(),name="question_list"),
    path("questions/create/",views.QuestionCreateView.as_view(),name="question_create"),
    path("questions/<int:pk>/update/",views.QuestionUpdateView.as_view(),name="question_update"),
    path("questions/<int:pk>/delete/",views.QuestionDeleteView.as_view(),name="question_delete"),
]
