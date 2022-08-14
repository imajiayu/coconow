from django.db import models
from django.contrib.auth.models import User
from accounts.models import Project

class ChatRecord(models.Model):
  pid = models.ForeignKey(Project, on_delete=models.CASCADE)
  uid = models.ForeignKey(User, on_delete=models.CASCADE)
  message = models.TextField(max_length=200)
  timestamp = models.DateTimeField(auto_now_add=True)


# Create your models here.
