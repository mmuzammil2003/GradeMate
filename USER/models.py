from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    Role_choices=(
        ("student","Student"),
        ("teacher","Teacher"),
    )
    name=models.CharField(max_length=20,null=False,blank=False)
    role=models.CharField(max_length=10,choices=Role_choices)
    mobile=models.CharField(max_length=15,blank=True,null=True)
    class_grade=models.CharField(max_length=5,blank=True,null=True)
    subject=models.CharField(max_length=5,blank=True,null=True)

    def __str__(self):
        return f"{self.name}({self.role})"
    
 