from django.urls import path
from . import views

app_name = 'Student'

urlpatterns = [
    path("dashboard/",views.Dashboard.as_view(),name="Sdashboard"),
    path("assignments/",views.AssignmentView.as_view(),name="assignments"),
    path("assignments/<int:pk>/",views.AssignmentDetailView.as_view(),name="assignment_detail"),
    path("assignments/<int:assignment_id>/submit/",views.SubmitAssignmentView.as_view(),name="submit_assignment"),
    path("assignments/<int:pk>/result/",views.AssignmentResultView.as_view(),name="assignment_result"),
    path("result/",views.ResultList.as_view(),name="result"),
    path("resultDetail/<int:pk>/",views.ResultDetail.as_view(),name="resultDetail"),
    path("notifications/",views.NotificationListView.as_view(),name="notifications"),
    # AI Evaluation URLs (for questions)
    path("upload/",views.UploadAnswerView.as_view(),name="upload_answer"),
    path("result/<int:pk>/",views.ResultView.as_view(),name="result_detail"),
]
