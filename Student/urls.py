from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/",views.Dashboard.as_view(),name="Sdashboard"),
    path("assignment/",views.AssignmentView.as_view(),name="assignment"),
    path("result/",views.ResultList.as_view(),name="result"),
    path("resultDetail/",views.ResultDetail.as_view(),name="resultDetail"),
]
