import base64
import os
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import User
from .models import Message
from django.core.files.base import ContentFile

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender_username = data['sender']
        receiver_username = data['receiver']
        message = data.get('message', '')
        file_data = data.get('file')
        file_name = data.get('file_name')

        sender = await sync_to_async(User.objects.get)(username=sender_username)
        receiver = await sync_to_async(User.objects.get)(username=receiver_username)

        file_instance = None
        if file_data and file_name:
            format, file_str = file_data.split(';base64,')
            decoded_file = ContentFile(base64.b64decode(file_str), name=file_name)
            msg = Message.objects.create(sender=sender, receiver=receiver, room_name=self.room_name, content=message, file=decoded_file)
        else:
            msg = Message.objects.create(sender=sender, receiver=receiver, room_name=self.room_name, content=message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg.content,
                'sender': sender.username,
                'file_url': msg.file.url if msg.file else '',
                'file_name': msg.file.name.split('/')[-1] if msg.file else '',
                'seen': msg.seen,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
