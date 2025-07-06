from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.contrib.auth import get_user_model



class ChatConsumer(AsyncWebsocketConsumer):
    
    @database_sync_to_async
    def get_user(self, user_id):
        from jobs.models import Conversation, Message
        User = get_user_model()  # ✅ safe now
        return User.objects.get(id=user_id)
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        self.user = self.scope["user"]
        self.conversation = await self.get_conversation(self.room_name)

        if self.user not in [self.conversation.client, self.conversation.freelancer]:
            await self.close()  # Reject connection
        else:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = self.user.username

        # Save to DB
        await self.save_message(self.conversation, self.user, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
        }))

    @database_sync_to_async
    def get_conversation(self, pk):
        from jobs.models import Conversation
        return Conversation.objects.get(pk=pk)

    @database_sync_to_async
    def save_message(self, conversation, sender, content):
        from jobs.models import Message
        return Message.objects.create(conversation=conversation, sender=sender, content=content)
