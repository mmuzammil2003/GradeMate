from django.urls import path
from . import views
urlpatterns = [
    path("dashboard/",views.Dashboard.as_view(),name="Tdashboard"),
    path("AssignmentForm/",views.AssignmentForm.as_view(),name="TAssignment"),
    path("AssignmentList/",views.AssignmentList.as_view(),name="TAssignmentList"),
    path("SubmissionList/",views.SubmissionList.as_view(),name="TSubmissionList"),
    # Question CRUD URLs
    path("questions/",views.QuestionListView.as_view(),name="question_list"),
    path("questions/create/",views.QuestionCreateView.as_view(),name="question_create"),
    path("questions/<int:pk>/update/",views.QuestionUpdateView.as_view(),name="question_update"),
    path("questions/<int:pk>/delete/",views.QuestionDeleteView.as_view(),name="question_delete"),
]
