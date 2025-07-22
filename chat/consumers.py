import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from chat.models import rooms, messages
from django.db.models import Q
from members.models import WorkSchedules

class memberschat(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.sender_id = self.scope['url_route']['kwargs']['sender_id']
        self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']

        self.room_name = await self.get_or_create_room()

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data):

        data = json.loads(text_data)
        print(data)
        message = data['message']

        if message != '':
            print("Saving...")
            await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_name,
            {
            'type':'send_message',
            'message':message,
            'sender':self.sender_id,
            'receiver':self.receiver_id
            }
        )

    async def send_message(self, event):
        print(self.sender_id,self.receiver_id, event['sender'],event['receiver'])
        message = event['message']
        is_mine = True if self.sender_id==event['sender'] else False
        print(is_mine)
        await self.send(json.dumps({
            'message':message,
            'is_mine':is_mine
            }))
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    @sync_to_async
    def get_or_create_room(self):
        sender = self.sender_id
        receiver = self.receiver_id
        try:
            room_obj = rooms.objects.get(Q(sender_id=sender, receiver_id=receiver) | Q(sender_id=receiver, receiver_id=sender))
            return room_obj.room_name
        except:
            room_name = f'chat_room_{min(sender, receiver)}_{max(sender, receiver)}'
            room_obj = rooms(room_name=room_name, sender_id=sender, receiver_id=receiver)
            room_obj.save()
            return room_obj.room_name

    @sync_to_async
    def save_message(self, message):
        room_obj = rooms.objects.get(room_name=self.room_name)
        messages.objects.create(room=room_obj, sender_id=self.sender_id, reciever_id=self.receiver_id, message=message)

    @sync_to_async
    def get_all_messages(self):
        data = messages.objects.filter(id__contains='1').values_list('')




class TaskDashboard(AsyncWebsocketConsumer):
    
    async def connect(self):

        self.room_name = self.scope['url_route']['kwargs']['dashboard_name']
        print(self.room_name)
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        payload = json.loads(text_data)["payload"]
        print("saving to db returns task obj...")
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "send_message",
                "task_data": payload,
            }
        )


    async def send_message(self, event):
        task_data = event['task_data']
        await self.send(json.dumps({
            'task':task_data,
            }))
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

class LiveDataDashboard(AsyncWebsocketConsumer):
    
    async def connect(self):

        self.room_name = "LiveDataDashboard"
        print(self.room_name)
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()
        all_tasks = await self.get_all_tasks()
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "send_message",
                "task_data": all_tasks,
            }
        )

    async def send_message(self, event):
        task_data = event['task_data']
        await self.send(json.dumps({"task_data":task_data}))
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
    @sync_to_async
    def get_all_tasks(self):
        objs = WorkSchedules.objects.filter(is_active=True).order_by('created_at')
        data = [
            {
            "id":instance.id,
            "user": instance.ward_member.get_user_name().title(),
            "block": instance.room.floor.block.block_name,
            "floor": instance.room.floor.floor_number,
            "room": instance.room.room_number,
            "date": str(instance.date),
            "session": instance.session
        } for instance in objs
        ]
        return data
