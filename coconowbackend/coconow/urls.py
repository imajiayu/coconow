from django.urls import include
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include("accounts.urls.account")),
    path('api/projects/', include("accounts.urls.project")),
    path('api/files/', include("file.urls")),
]