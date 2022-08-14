from platform import java_ver
import time
from urllib import response
from click import command
import paramiko
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.http import JsonResponse,FileResponse
from rest_framework.views import APIView
from accounts.models import Member, Project
from websocket_service.CoProgramming import checkFileOpen,sendProjectMessage
import json
import os

from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from coconow.settings import UPLOAD_TEMPFILE_PATH  
class CsrfExemptSessionAuthentication(SessionAuthentication): 
    def enforce_csrf(self, request): 
        return  # To not perform the csrf check previously happening

# Create your views here.
def dockerSSH(username,port,command): #输入端口与命令,返回stdout
    sh = paramiko.SSHClient()  # 1 创建SSH对象
    sh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 2 允许连接不在know_hosts文件中的主机
    sh.connect("124.70.221.116",port=port, username=username, password="root")  # 3 连接服务器
    stdin, stdout, stderr = sh.exec_command(command=command)
    return stdout.read().decode("utf-8")


class FileList(APIView):
    def get(self, request, pk):
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
            if not Member.objects.filter(pid=pk,uid=user.id).exists():
                return Response({
                "message":"failure",
                "data":{
                    "detail":"非法访问项目",
                }
            },status=400)
            port=20000+int(pk)
            stdout=dockerSSH("root",port,'python /walkTree.py')
            return JsonResponse({
                'filelist':json.loads(stdout),
            })


class CreateFile(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self, request, pk):
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
            if not Member.objects.filter(pid=pk,uid=user.id).exists():
                return Response({
                "message":"failure",
                "data":{
                    "detail":"非法访问项目",
                }
            },status=400)
            path=request.data.get("dir")
            name=request.data.get("name")
            dir=os.path.join(path,name)
            port=20000+int(pk)
            if Member.objects.filter(pid=pk,uid=user.id)[0].privilege=="owner":
                dockerSSH("root",port,'touch /home'+str(dir))
            else:
                dockerSSH(user.username,port,'touch /home'+str(dir))

            sendProjectMessage(pk,{"type":"refresh","message":user.username+"创建了文件"+dir,"uid":user.id})
            return Response({
                "message":"success"
            })

class RemoveFile(APIView):
    def get(self, request, pk):
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
            project=Project.objects.get(pk=pk)
            if not Member.objects.filter(pid=project,uid=user).exists():
                return Response({
                "message":"failure",
                "data":{
                    "detail":"非法删除项目",
                }
            },status=400)
            
            path = request.GET["path"]
            port=20000+int(pk)
            if checkFileOpen(pk,path):
                if Member.objects.filter(pid=project,uid=user)[0].privilege=="owner":
                    sendProjectMessage(pk,{"type":"refresh","message":user.username+"删除了文件"+path,"uid":user.id})
                    dockerSSH("root",port,'rm /home'+str(path))
                else:
                    sh = paramiko.SSHClient()
                    sh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 2 允许连接不在know_hosts文件中的主机
                    sh.connect("124.70.221.116",port=port,username=user.username, password="root") 
                    chan=sh.invoke_shell(term='xterm')
                    stdout=chan.recv(1024)
                    chan.send('rm /home'+str(path)+'\n')
                    time.sleep(0.1)
                    if chan.recv_ready():
                        stdout=chan.recv(1024)
                        if "write-protected" in stdout.decode() or "Operation not permitted" in stdout.decode():
                            return Response({
                            "message":"无删除权限",
                            "data":{
                                "detail":"无删除权限"
                            }
                        },status=400)
                    sendProjectMessage(pk,{"type":"refresh","message":user.username+"删除了文件"+path,"uid":user.id})
                    return Response({
                        "message":"success"
                    })

            else:
                return Response({
                "message":"该文件正在被使用",
                "data":{
                    "detail":"该文件正在被使用"
                }
            },status=400)
                
            #sendProjectMessage(pk,{"type":"refresh","message":user.username+"删除了文件"+path,"uid":user.id})
            return Response({
                "message":"success"
            })

class CreateDir(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self, request, pk):
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
            if not Member.objects.filter(pid=pk,uid=user.id).exists():
                return Response({
                "message":"failure",
                "data":{
                    "detail":"非法访问项目",
                }
            },status=400)
            path=request.data.get("dir")
            name=request.data.get("name")
            port=20000+int(pk)
            dir=os.path.join(path,name)
            if Member.objects.filter(pid=pk,uid=user.id)[0].privilege=="owner":
                dockerSSH("root",port,'mkdir /home'+str(dir))
            else:
                dockerSSH(user.username,port,'mkdir /home'+str(dir))
            
            sendProjectMessage(pk,{"type":"refresh","message":user.username+"创建了目录"+dir,"uid":user.id})
            return Response({
                "message":"success"
            })

class RemoveDir(APIView):
    def get(self, request, pk):
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
            project=Project.objects.get(pk=pk)
            if not Member.objects.filter(pid=project,uid=user).exists():
                return Response({
                "message":"failure",
                "data":{
                    "detail":"非法删除项目或不是拥有者",
                }
            },status=400)

            path = request.GET["path"]

            
            port=20000+int(pk)
            if checkFileOpen(pk,path):
                if Member.objects.filter(pid=project,uid=user)[0].privilege=="owner":
                    sendProjectMessage(pk,{"type":"refresh","message":user.username+"删除了目录"+path,"uid":user.id})
                    dockerSSH("root",port,'rm -rf /home'+str(path))
                else:
                    sh = paramiko.SSHClient()
                    sh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 2 允许连接不在know_hosts文件中的主机
                    sh.connect("124.70.221.116",port=port,username=user.username, password="root") 
                    chan=sh.invoke_shell(term='xterm')
                    chan.recv(1024)
                    chan.send('rm -rf /home'+str(path)+'\n')
                    time.sleep(0.1)
                    if chan.recv_ready():
                        stdout=chan.recv(1024)
                        if "Operation not permitted" in stdout.decode():
                            return Response({
                            "message":"无删除权限",
                            "data":{
                                "detail":"无删除权限"
                            }
                        },status=400)

                    sendProjectMessage(pk,{"type":"refresh","message":user.username+"删除了目录"+path,"uid":user.id})
                    return Response({
                        "message":"success"
                    })

            else:
                return Response({
                "message":"该文件正在被使用",
                "data":{
                    "detail":"该文件正在被使用"
                }
            },status=400)
            
            return Response({
                "message":"success"
            })

class UploadFile(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self, request, pk):
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
            if not Member.objects.filter(pid=pk,uid=user.id).exists():
                return Response({
                "message":"failure",
                "data":{
                    "detail":"非法访问",
                }
            },status=400)

            files = request.FILES.getlist('file')
            dir = request.POST.get('dir')
            dockername=Project.objects.get(id=pk).pname
            for f in files:
                file_path = os.path.join(UPLOAD_TEMPFILE_PATH,f.name)
                with open(file_path,'wb+') as fp :
                    for chunk in f.chunks():
                        fp.write(chunk)
                command='docker cp '+file_path+' '+dockername+':'+'/home'+dir+'/'+f.name
                os.system(command)
                os.system('rm -f '+file_path)

                port=20000+int(pk)
                project=Project.objects.get(pk=pk)
                if Member.objects.get(uid=user,pid=project).privilege=="owner":
                    dockerSSH("root",port,'chown root '+'/home'+dir+'/'+f.name)
                else:
                    dockerSSH("root",port,'chown '+user.username+'/home'+dir+'/'+f.name)
                
            sendProjectMessage(pk,{"type":"refresh","message":user.username+"上传了文件"+dir+'/'+f.name,"uid":user.id})
            return Response({
                "message":"success"
            })

class DownloadFile(APIView):
    def get(self, request, pk):
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
            if not Member.objects.filter(pid=pk,uid=user.id).exists():
                return Response({
                "message":"非法删除项目或不是拥有者",
                "data":{
                    "detail":"非法删除项目或不是拥有者",
                }
            },status=400)
            
            
            path = request.GET.get('path')
            dockername=Project.objects.get(id=pk).pname
            fname=os.path.basename(path)
            fpath=os.path.join(UPLOAD_TEMPFILE_PATH,fname)
            command='docker cp '+dockername+':/home'+path+' '+fpath
            os.system(command)
            ret=FileResponse(open(fpath,'rb'),as_attachment=True)
            os.system('rm -f '+fpath)
            return ret

