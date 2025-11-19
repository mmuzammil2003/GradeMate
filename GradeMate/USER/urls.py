from django.urls import path
from .views import RegisterView, CustomLoginView, CustomLogoutView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
]
