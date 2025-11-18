from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/",views.Dashboard.as_view(),name="Sdashboard"),
    path("assignment/",views.AssignmentView.as_view(),name="assignment"),
    path("result/",views.ResultList.as_view(),name="result"),
    path("resultDetail/",views.ResultDetail.as_view(),name="resultDetail"),
    # AI Evaluation URLs
    path("upload/",views.UploadAnswerView.as_view(),name="upload_answer"),
    path("result/<int:answer_id>/",views.ResultView.as_view(),name="result_detail"),
]
