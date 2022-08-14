from logging import error
from channels.generic.websocket import WebsocketConsumer
import paramiko
import time
import threading
from django.contrib.auth.models import User
from accounts.models import Member, Project
import json


class SSHRecvThread(threading.Thread):
    def __init__(self,comsumer):
        threading.Thread.__init__(self)
        self.comsumer = comsumer
    def run(self):
        while True:
            out = self.comsumer.chan.recv(1024)
            # 这里可以不用动
            if len(out) == 0:
                break
            print(out)
            out=out.decode('utf-8',errors='ignore')
            # print('out',repr(out))
            self.comsumer.send(out)
            

class WebSSHService(WebsocketConsumer):

    def connect(self):
        self.accept()
        self.sh = paramiko.SSHClient()  # 1 创建SSH对象
        self.chan = None


    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data['type'] == 'init':
            user=User.objects.get(pk=int(data['uid']))
            project=Project.objects.get(pk=int(data['pid']))
            username=None
            if Member.objects.get(uid=user,pid=project).privilege=='owner':
                username="root"
            else:
                username=user.username
            self.sh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 2 允许连接不在know_hosts文件中的主机
            self.sh.connect("124.70.221.116",port=20000+int(data['pid']),username=username, password="root")  # 3 连接服务器
            self.chan=self.sh.invoke_shell(term='xterm')
            self.recvThread = SSHRecvThread(self)
            self.recvThread.setDaemon(True)
            self.recvThread.start()
            #self.chan.send('export LC_ALL="en_US.UTF-8";cd /home\n')
            # print("webssh连接成功")
        elif data['type'] == 'opt':
            if self.chan is None:
                # print("webssh error!")
                self.send('no connect!')
            opt = data['opt']
            self.chan.send(opt)

        

    def disconnect(self, code):
        # print('webssh断开连接')
        pass