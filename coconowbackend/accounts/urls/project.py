from urllib.parse import urlparse
from django.urls import path
from accounts.views import project

urlpatterns = [
    path("create/", project.CreateProject.as_view(), name="create"),
    path("info/<int:pk>/", project.ProjectInfo.as_view(), name="projectinfo"),
    path("remove/", project.RemoveProject.as_view(), name="remove"),
    path("inviteuser/", project.InviteUser.as_view(), name="InviteUser"),
    path("removeuser/", project.RemoveUser.as_view(), name="RemoveUser"),
]