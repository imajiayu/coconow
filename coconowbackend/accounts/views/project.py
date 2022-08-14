import os
from pickle import TRUE
from random import randint
import time
from click import command
from django.contrib.auth.models import User
from django.http import QueryDict
import paramiko
from requests import delete
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import Member, Project
from rest_framework import permissions
from websocket_service.CoProgramming import checkFileOpen,sendProjectMessage

from rest_framework.authentication import SessionAuthentication, BasicAuthentication  
class CsrfExemptSessionAuthentication(SessionAuthentication): 
 
    def enforce_csrf(self, request): 
        return  # To not perform the csrf check previously happening

def dockerSSH(port,command): #输入端口与命令,返回stdout
    sh = paramiko.SSHClient()  # 1 创建SSH对象
    sh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 2 允许连接不在know_hosts文件中的主机
    sh.connect("124.70.221.116",port=port, username="root", password="root")  # 3 连接服务器
    stdin, stdout, stderr = sh.exec_command(command=command)
    return stdout.read().decode("utf-8")

colorlist=['#FF0000','#FFFF00','#008000','#0000FF','#FFA500','#008B8B','#8A2BE2','#FFC0CB']

class ProjectInfo(APIView):
    def get(self, request, pk):
        members = Member.objects.filter(pid=pk)
        res = []
        for membership in members:
            res.append({"id": membership.uid.id, "username": membership.uid.username, "privilege": membership.privilege, "color":membership.colour})
        return Response({
            "message":"success",
            "pid": pk,
            "membermsg":res
        })

class CreateProject(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self,request,format=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户未登录"
                }
            })
        else:
            data = request.data
            pname = data.get("pname")
            if Project.objects.filter(pname=pname).exists():
                return Response({
                "message":"failure",
                "data":{
                    "detail":"项目名已存在"
                }
                })
            else:
                pid=Project.objects.create(pname=pname).id
                command="docker run -d -p " + str(20000+pid)+":22 --name="+pname+" stdc:v3 /usr/sbin/sshd -D"
                os.system(command)
                command='docker cp /home/mjy/coconow/accounts/walkTree.py '+pname+':/'
                os.system(command)

                
                Member.objects.create(pid=Project.objects.get(pname=pname), uid=request.user, privilege="owner",colour=colorlist[randint(0,len(colorlist)-1)])
                return Response({
                "message":"success",
                "data":{
                    "pid":pid
                }
                })

class RemoveProject(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def delete(self,request,format=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户未登录"
                }
            })
        
        pid = request.GET["pid"]
        if Project.objects.filter(pk=pid).count()==0:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"项目不存在"
                }
            })

        member=Member.objects.filter(pid=pid,privilege="owner")
        if member.exists():
            if member.first().uid.id==request.user.id:
                project=Project.objects.get(id=pid)
                command="docker rm -f "+project.pname
                os.system(command)

                project.delete()

                members=Member.objects.filter(pid=pid)
                members.delete()

                return Response({
                "message":"success",
            })
            else:
                return Response({
                "message":"failure",
                "data":{
                    "detail":"非项目拥有者"
                }
            })
        else:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"删除时发生错误"
                }
            })  

class InviteUser(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self, request, format = None):
        # 前端向后端发送项目id（pid）和被邀请的人的名称（invitename）来邀请成员进来
        user = request.user
        data = request.data
        pid = data.get("pid")
        project = Project.objects.get(pk=pid)
        if not user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户未登录"
                }
            })
        else:
            invitename = data.get("invitename").strip()
            users = User.objects.filter(username=invitename)
            # invited user does not exist
            if users.count() == 0:
                return Response({
                    "message": "failure",
                    "data": {
                        "detail": "被邀请的用户不存在"
                    }
                })
            
            elif Member.objects.filter(uid=users[0],pid=project).exists():
                return Response({
                "message": "failure",
                "data": {
                    "detail": "用户已经在项目中"
                }
            })

            else:
                used_color=[x.colour for x in Member.objects.filter(pid=project)]
                unused_color=[x for x in colorlist if x not in used_color]
                Member.objects.create(pid=project, uid=users.first(), privilege="collaborator",colour=unused_color[randint(0,len(unused_color)-1)])
                port=20000+int(pid)
                stdout=dockerSSH(port,'useradd -d /'+str(invitename)+' -m '+invitename)
                
                sh = paramiko.SSHClient()
                sh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 2 允许连接不在know_hosts文件中的主机
                sh.connect("124.70.221.116",port=port,username="root", password="root") 
                chan=sh.invoke_shell(term='xterm')
                chan.send('passwd '+invitename+'\n')
                time.sleep(0.1)
                chan.send('root\n')
                time.sleep(0.1)
                chan.send('root\n')

                return Response({
                    "message":"success"
                })

class RemoveUser(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self, request, format = None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户未登录"
                }
            })       
        else:
            data = request.data
            pid = data.get("pid")
            target_username = data.get("username")
            project = Project.objects.get(pk=pid)
            current_membership = Member.objects.filter(pid=project,uid=user).first()
            # 检查是否是这个项目的owner
            if current_membership.privilege != "owner":
                return Response({
                    "message": "failure",
                    "data":{
                        "detail": "你不是项目拥有者，不可以删除用户"
                    }
                })
            # 检查是否有这个成员
            target_user = User.objects.filter(username=target_username)
            target_membership = Member.objects.filter(pid=project,uid=target_user)
            if not target_user.exists() or not Member.objects.filter(pid=project,uid=target_user[0]).exists():
                return Response({
                    "message": "failure",
                    "data": {
                        "detail": "该用户不在此项目中"
                    }
                })
            # owner不能删除自己
            if user.id == target_user[0].id:
                return Response({
                    "message": "failure",
                    "data": {
                        "detail": "你不能删除自己"
                    }
                })
            # 删除此成员
            t=Member.objects.get(pid=project,uid=target_user[0]).delete()
            sendProjectMessage(pid,{"type":"deleteMember","uid":target_user[0].id})
            return Response({
                "message":"success"
            })