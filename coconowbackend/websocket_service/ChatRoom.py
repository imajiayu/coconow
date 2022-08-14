from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from pymysql import Timestamp
from websocket_service.models import ChatRecord
from accounts.models import Project
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
import json
import time

MAX_RECORD_NUM = 100

class ChatRoomConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()



    def disconnect(self, close_code):
        # Leave room group
        if getattr(self,"room_group_name")is not None:
          async_to_sync(self.channel_layer.group_discard)(
              self.room_group_name,
              self.channel_name
          )
        
        # print(operateManage) 



    # Receive message from WebSocket
    def receive(self, text_data):
        delta = json.loads(text_data)
        # t1 = time.time()
        
        type = delta['type']
        uid = delta['uid']
        pid = delta['pid']
        if type == 'initialize':
            self.uid = uid
            self.pid = pid
            self.room_group_name = str(pid)+"_chat"

            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            record_set = ChatRecord.objects.filter(pid=pid).order_by('timestamp')
            record_data = []
            record_num = len(record_set)
            l = max(record_num-MAX_RECORD_NUM,0)
            for index in range(l,record_num):
                record = record_set[index]
                data = model_to_dict(record,fields=['pid','uid','message'])
                data['timestamp'] = record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                # print(data)
                record_data.append(data)
                


            self.send(text_data=json.dumps({
                'type': 'initialize',
                'records': record_data
            }))

        elif type == 'message':
            message = delta['message']
            project = Project.objects.get(id=pid)
            user = User.objects.get(id=uid)
            ChatRecord.objects.create(pid=project,uid=user,message=message)

            async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
              'type': 'coop_send',
              'delta': delta,
              'channel_name':self.channel_name,
            }
            )
        
        # print("receive message",self.room_group_name,self.channel_name,delta)
        # print("use time",time.time()-t1)

        

    # Receive message from room group
    def coop_send(self, event):
        #if self.channel_name == event['channel_name']:
            
        #    return
            
        # Send message to WebSocket
        # print("send message to",self.channel_name,"in",self.room_group_name)
        self.send(text_data=json.dumps(event['delta']))





