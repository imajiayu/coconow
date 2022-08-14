from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    pname = models.CharField(max_length=128)

class Member(models.Model):
    pid = models.ForeignKey("Project", on_delete=models.CASCADE)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    privilege = models.CharField(max_length=128)
    colour = models.CharField(max_length=128,default='')
    class Meta:
        unique_together = ("pid", "uid")
