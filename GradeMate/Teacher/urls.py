from django.urls import path
from . import views
urlpatterns = [
    path("dashboard/",views.Dashboard.as_view(),name="Tdashboard"),
    path("AssignmentForm/",views.AssignmentForm.as_view(),name="TAssignment"),
    path("AssignmentList/",views.AssignmentList.as_view(),name="TAssignmentList"),
    path("SubmissionList/",views.SubmissionList.as_view(),name="TSubmissionList"),
]
