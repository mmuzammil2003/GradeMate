from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django import forms

from .models import User

class RegistrationForm(UserCreationForm):
    class Meta:
        model=User
        fields=["username","name","email","mobile","class_grade","role","subject","password1","password2",]

        def clean(self):
            cleaned_data=super().clean()
            role=cleaned_data.get("role")

            if role=="student" and not cleaned_data.get("class_grade"):
                self.add_error("class_grade","Students must enter their Class Grade")
            if role=="teacher" and not cleaned_data.get("subject"):
                self.add_error("subject","Teacher must enter teh Subject they teach")
            return cleaned_data
        
class LoginForm(AuthenticationForm):
    username=forms.CharField(widget=forms.TextInput(attrs={"class":"form-input"}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"Form-input"}))
                