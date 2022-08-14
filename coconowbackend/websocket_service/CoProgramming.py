from inspect import getfile
from multiprocessing import managers
from multiprocessing.pool import ApplyResult
from tokenize import group
from turtle import clear
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
import time
from file.tools import *
from threading import BoundedSemaphore

consumerSemaphore = BoundedSemaphore(1)

Manager = {}

def isRetain(op):
  return type(op) == int and op>0

def isInsert(op):
  return type(op) == str

def isDelete(op):
  return type(op) == int and op<0

def applyOperation(pid,path,ops):
    manage = getFileManage(pid,path)
    index = 0
    for op in ops:
        if isRetain(op):
            index += op
        elif isDelete(op):
            manage.content = manage.content[0:index] + manage.content[index-op:]
        elif isInsert(op):
            manage.content = manage.content[0:index] + op + manage.content[index:]
    # print(manage.content)

class GroupManage:
    def __init__(self):
        self.group = {}
        self.files = {}
        self.channels = []

class FileManage:
    def __init__(self):
        self.users = {}
        self.content = ""
        self.revision = 0

def getGroupManage(pid):
    if Manager.get(pid) is None:
        Manager[pid] = GroupManage()
    return  Manager[pid]

def getFileManage(pid,path):
    GroupManage = getGroupManage(pid)
    if GroupManage.files.get(path) is None:
        GroupManage.files[path] = FileManage()
    return GroupManage.files[path]


def removeFileManage(pid,path):
    GroupManage = getGroupManage(pid)
    GroupManage.files.pop(path)

def exitFile(pid,uid,path):
    fileManager = getFileManage(pid,path)
    fileManager.users[uid] -= 1
    if fileManager.users[uid] == 0:
        fileManager.users.pop(uid)
    if len(fileManager.users) == 0:
        filePath = tmppath(pid,path)
        with open(filePath,'w') as file:
            file.write(fileManager.content)
        dockersave(pid,path)
        removetmp(pid,path)
        Manager[pid].files.pop(path)

def openFile(pid,uid,path):
    fileManager = getFileManage(pid,path)
    # print(fileManager.users)
    if len(fileManager.users) == 0:
        filepath = dockeropen(pid,path)  
        filesize=os.path.getsize(filepath)   
        if filesize>=1024*1024:
            raise NameError        
        with open(filepath,'r') as file:
            fileManager.content = file.read()
    if fileManager.users.get(uid) is None:
        fileManager.users[uid] = 1
    else:
        fileManager.users[uid] += 1




def sendProjectMessage(pid,delta):
    groupManager = getGroupManage(pid)
    for channel in groupManager.channels:
        channel.send(text_data=json.dumps(delta))


def checkFileOpen(pid,path):
    if Manager.get(pid) is None:
        return True
    GroupManager = getGroupManage(pid)
    for key,item in GroupManager.files.items():
        # print(key,path)
        if key[:len(path)] == path:
            return False
    return True







def saveAllFiles(pid):
    groupManager = getGroupManage(pid)
    for path,fileManager in groupManager.files.items():
        filePath = tmppath(pid,path)
        with open(filePath,'w') as file:
            file.write(fileManager.content)
        dockersave(pid,path)

class CoProgrammingConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()


    def disconnect(self, close_code):


        # Leave room group
        if self.room_group_name is not None:
            
            # groupManager.channels.remove(self)
            uid = self.uid
            pid = self.pid

            if not len(self.paths) == 0:
                for path in self.paths:
                    exitFile(pid,uid,path)
            groupManager = getGroupManage(pid)
            groupManager.group[uid] -= 1
            if groupManager.group[uid] == 0:
                groupManager.group.pop(uid)
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'coop_send',
                        'delta': {
                            'type': 'memberDisconnect',
                            'pid': pid,
                            'uid': uid,
                            'group': list(groupManager.group.keys())
                        },
                        'channel_name': self.channel_name,
                    }
                )
            if len(groupManager.group) == 0:
                if len(groupManager.files) != 0:
                    raise ValueError
                else:
                    Manager.pop(pid)
            groupVar = groupManager.group

            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )
            


             
        # print(operateManage) 



    # Receive message from WebSocket
    def receive(self, text_data):
        delta = json.loads(text_data)
        # print("receive delta",delta)
        consumerSemaphore.acquire()

        type = delta['type']
        if type == 'initializeTabs':
            uid = delta['uid']
            pid = delta['pid']
            self.uid = uid
            self.pid = pid
            self.paths = []
            self.room_group_name = str(pid)+"_operation"

            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            # print("connect",self.channel_name,self.uid)

            groupManager = getGroupManage(pid)
            # print('user is ',groupManager.group.get(uid))
            if groupManager.group.get(uid) is None:
                groupManager.group[uid] = 1
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'coop_send',
                        'delta': {
                            'type': 'memberConnect',
                            'pid': pid,
                            'uid': uid,
                            'group': list(groupManager.group.keys())
                        },
                        'channel_name': self.channel_name,
                    }
                )
            else:
                groupManager.group[uid] += 1   

            groupManager.channels.append(self)

            

            # groupManager.channelLayer = self.channel_layer


            

            self.send(text_data=json.dumps({
                'type': 'initializeTabs',
                'group': list(groupManager.group.keys())
            }))


         

            
        elif type == 'initializeFile':
            uid = delta['uid']
            pid = delta['pid']
            path = delta['path']
            openError=False
            try:
                openFile(pid,uid,path)
            except ValueError:
                print(path+"是二进制文件，打开失败")
                self.send(text_data=json.dumps({
                    'type': 'openFail',
                    'message': path+"是二进制文件，打开失败",
                }))
                removeFileManage(pid,path)
            except NameError:
                print(path+"文件大小过大，打开失败")
                self.send(text_data=json.dumps({
                    'type': 'openFail',
                    'message': path+"文件大小过大，打开失败",
                }))
                removeFileManage(pid,path)
            except Exception as e:
                print(e)
            else:
                self.paths.append(path)    
                fileManager = getFileManage(pid,path)
                self.send(text_data=json.dumps({
                    'type': 'initializeFile',
                    'content': fileManager.content,
                    'revision': fileManager.revision,
                    'path' : path
                }))
            
            

        elif type == 'saveAll':
            pid = delta['pid']
            # print(delta)
            saveAllFiles(pid)
            async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'coop_send',
                        'delta': {
                            'type': 'saveDone',
                            'pid': pid,
                        },
                        'channel_name': '',
                    }
                )

        elif type == 'closeFile':
            pid=delta['pid']
            uid=delta['uid']
            path=delta['path']
            exitFile(pid,uid,path)
            self.paths.remove(path)


        elif type == 'operation':
            uid = delta['uid']
            pid = delta['pid']
            path = delta['path']
            fileManager = getFileManage(pid,path)


            
            if delta['revision'] == fileManager.revision:
                fileManager.revision += 1
                applyOperation(pid,path,delta['operation'])
                # time.sleep(1)
                # print("send ack to",self.channel_name,"in",self.room_group_name)
                self.send(text_data=json.dumps({'type' : 'ack', 'path' : path}))

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'coop_send',
                        'delta': delta,
                        'channel_name':self.channel_name,
                    }
                )
            else:
                # print("nak delta",delta)
                # time.sleep(1)
                self.send(text_data=json.dumps(
                    {'type' : 'nak', 'path' : path }
                ))
            # saveAllFiles(pid)
            

        # print("receive delta",self.room_group_name,self.channel_name,delta)
        consumerSemaphore.release()

        

    # Receive message from room group
    def coop_send(self, event):
        
        if self.channel_name != event['channel_name'] :
            delta = event['delta']
            if delta['type'] == 'operation':
                if not event['delta']['path'] in self.paths:
                    # print("not send",delta['path'] , self.paths,self.channel_name)
                    return
                # print("send",delta['path'] , self.paths,self.channel_name)
            # Send message to WebSocket 
            # print("send delta to",self.channel_name,"in",self.room_group_name)
            self.send(text_data=json.dumps(delta))







