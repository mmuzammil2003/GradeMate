from django.urls import reverse_lazy
from django.views.generic import CreateView,TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import RegistrationForm, LoginForm
from .models import User


class RegisterView(CreateView):
    model = User
    form_class = RegistrationForm
    template_name = "USER/register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)  # optional: auto login after registration
        return super().form_valid(form)


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "USER/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.role == "student":
            return reverse_lazy("Sdashboard")
        elif user.role == "teacher":
            return reverse_lazy("Tdashboard")
        return reverse_lazy("dashboard")  # fallback


from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from .forms import RegistrationForm, LoginForm
from .models import User


class RegisterView(CreateView):
    model = User
    form_class = RegistrationForm
    template_name = "USER/register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)  # auto login after registration (optional)
        return super().form_valid(form)


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "USER/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.role == "student":
            return reverse_lazy("Sdashboard")
        elif user.role == "teacher":
            return reverse_lazy("Tdashboard")
        return reverse_lazy("dashboard")  # fallback


class CustomLogoutView(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        # Allow GET logout (clicking link in navbar)
        if request.method == "GET":
            logout(request)
            return redirect(self.next_page)
        return super().dispatch(request, *args, **kwargs)

