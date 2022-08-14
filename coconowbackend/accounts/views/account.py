import email
import os
from pickle import TRUE
import re
from django.contrib.auth.models import User
from requests import request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
import json
from accounts.models import Member
import coconow.settings
from django.core import mail
import random

verify_list={}


from rest_framework.authentication import SessionAuthentication, BasicAuthentication  
class CsrfExemptSessionAuthentication(SessionAuthentication): 
 
    def enforce_csrf(self, request): 
        return  # To not perform the csrf check previously happening

class Register(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self, request, format=None):
        data = json.loads(request.body)
        username = data.get("username").strip()
        password = data.get("password").strip()
        email = data.get("email").strip()
        verify_code = data.get("verify_code").strip()
        # empty field
        if not username or not password or not email or username == "" or password=="" or email == "":
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户名、密码、邮箱不能为空"
                }
            })
        if email not in verify_list or verify_list[email]!=verify_code:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"验证码错误"
                }
            },status=400)
        # user already exists
        elif User.objects.filter(username=username).exists():
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户名已存在"
                }
            })
        # email already exists
        elif User.objects.filter(email=email).exists():
            return Response({
                "message":"failure",
                "data":{
                    "detail":"邮箱已存在"
                }
            })
        # success
        else:
            user=User.objects.create_user(username=username, password=password,email=email)
            verify_list.pop(email)

            os.system('cp /home/mjy/coconow/static/avatar/default.jpg /home/mjy/coconow/static/avatar/'+str(user.id)+'.jpg')

            return Response({
                "message":"success"
            })

class Verify(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self, request, format=None):
        data = json.loads(request.body)
        email = data.get("email").strip()
        if User.objects.filter(email=email).exists():
            return Response({
                "message":"failure",
                "data":{
                    "detail":"邮箱已存在"
                }
            })
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        characters = "".join(random.sample(alphabet, 5))
        sendemail(str(email),str('欢迎注册coconow'),str('您的验证码是: ')+characters)
        verify_list[email]=characters
        return Response({
            "message":"success"
        })

class ForgetPasswd1(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self, request, format=None):
        data = json.loads(request.body)
        email = data.get("email").strip()
        if not User.objects.filter(email=email).exists():
            return Response({
                "message":"failure",
                "data":{
                    "detail":"邮箱不存在"
                }
            })

        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        characters = "".join(random.sample(alphabet, 5))
        sendemail(str(email),str('coconow修改密码'),str('您的验证码是: ')+characters)
        verify_list[email]=characters
        return Response({
            "message":"success"
        })

class ForgetPasswd2(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self, request, format=None):
        data = json.loads(request.body)
        email = data.get("email").strip()
        password = data.get("password").strip()
        verify_code = data.get("verify_code").strip()
        if email not in verify_list or verify_list[email]!=verify_code:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"验证码错误"
                }
            },status=400)
        user=User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return Response({
                "message":"success"
            })
        
        

class Login(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self, request, format=None):
        # print(coconow.settings.UPLOAD_TEMPFILE_PATH)
        user = request.user
        if user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"已登录用户不能再次登录"
                }
            })
        data = json.loads(request.body)
        username = data.get("username").strip()
        password = data.get("password").strip()
        email= data.get("email").strip()
        
        user = None
        if email=="":
            user=authenticate(username=username,password=password)
            # failure
            if not user:
                return Response({
                    "message":"failure",
                    "data":{
                        "detail":"用户名/邮箱或密码不正确"
                    }
                })
            # success
            else:
                login(request, user)
                request.session["id"] = user.id
                return Response({
                    "message":"success"
                })
        elif username=="":
            if not User.objects.filter(email=email).exists():
                return Response({
                    "message":"failure",
                    "data":{
                        "detail":"用户名/邮箱或密码不正确"
                    }
                })
            user=authenticate(username=User.objects.filter(email=email)[0].username,password=password)
            if not user:
                return Response({
                    "message":"failure",
                    "data":{
                        "detail":"用户名/邮箱或密码不正确"
                    }
                })
            # success
            else:
                login(request, user)
                request.session["id"] = user.id
                return Response({
                    "message":"success"
                })

class MyInfo(APIView):
    def get(self, request, format=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户未登录"
                }
            })
        else:
            id = User.objects.filter(username=user.username).first()
            members = list(Member.objects.filter(uid = id))
            projectsinfo = []
            for membership in members:
                projectsinfo.append({"pid": membership.pid.id, "pname": membership.pid.pname, "privilege": membership.privilege,"color":membership.colour})
            return Response({
                "message":"success",
                "data":{
                    "uid": user.id,
                    "username":user.username,
                    "email":user.email,
                    "projects":projectsinfo,
                }
            })

class Logout(APIView):
    def get(self, request, format=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "message": "failure",
                "data":{
                    "detail": "用户未登录"
                }
            })
        else:
            logout(request)
            return Response({
                "message": "success",
            })

class GetIdentity(APIView):
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "isLogin": "False"
            })
        else:
            return Response({
                "isLogin":"True"
            })

class UploadAvatar(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self, request):
        # 判断用户登录
        user=request.user
        if not user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户未登录"
                }
            },status=400)
        else:
            files = request.FILES.getlist('file')
            file_path = os.path.join(os.path.join(coconow.settings.BASE_DIR, 'static/avatar'),str(user.id)+'.jpg')
            for f in files:
                with open(file_path,'wb+') as fp :
                    for chunk in f.chunks():
                        fp.write(chunk)
                
            return Response({
                "message":"success"
            })
        

def sendemail(to,subject,message):
    subject = subject  # 主题
    from_email = coconow.settings.EMAIL_FROM  # 发件人，在settings.py中已经配置
    to_email = to  # 邮件接收者列表
    # 发送的消息
    message = message  # 发送普通的消息使用的时候message
    mail.send_mail(subject, message, from_email, [to_email])
    return TRUE
