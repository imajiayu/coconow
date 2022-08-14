from distutils.command.upload import upload
from django.urls import include
from django.contrib import admin
from django.urls import path
from file.views import FileList, CreateFile, RemoveFile, CreateDir,RemoveDir,UploadFile,DownloadFile

urlpatterns = [
    path("filelist/<int:pk>/", FileList.as_view(), name="filelist"),
    path("createfile/<int:pk>/", CreateFile.as_view(), name="createfile"),
    path("removefile/<int:pk>/", RemoveFile.as_view(), name="removefile"),
    path("createdir/<int:pk>/", CreateDir.as_view(), name="createDir"),
    path("removedir/<int:pk>/", RemoveDir.as_view(), name="removeDir"),
    path("uploadfile/<int:pk>/", UploadFile.as_view(), name="uploadfile"),
    path("downloadfile/<int:pk>/", DownloadFile.as_view(), name="downloadfile"),
]