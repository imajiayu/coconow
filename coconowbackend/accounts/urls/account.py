from django.urls import path
from accounts.views import account

urlpatterns = [
    path("verify/",account.Verify.as_view(), name='verify'),
    path("register/",account.Register.as_view(), name='register'),
    path('login/', account.Login.as_view(), name='login'),
    path("myinfo/", account.MyInfo.as_view(), name="myinfo"),
    path("logout/", account.Logout.as_view(), name="logout"),
    path("getIdentity/", account.GetIdentity.as_view(), name="getIdentity"),
    path('forgetpassword1/', account.ForgetPasswd1.as_view(), name='forgetpassword1'),
    path('forgetpassword2/', account.ForgetPasswd2.as_view(), name='forgetpassword2'),
    path("uploadavatar/", account.UploadAvatar.as_view(), name="uploadavatar"),
]