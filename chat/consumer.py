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
        print(f"Connected to room: {self.room_name}")
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope["user"]
        print(">>> WebSocket user:", self.user)
        if not self.user.is_authenticated:
            await self.close()
            return

       
       
        self.conversation = await self.get_conversation(self.room_name)
        client, freelancer = await self.get_participants(self.conversation)
        print("Client:", client)
        print("Freelancer:", freelancer)
        print("Current User:", self.user)
        print("Client repr:", repr(client))
        print("Freelancer repr:", repr(freelancer))
        print("Current User repr:", repr(self.user))
        if self.user != client and self.user != freelancer:
            print("User is not a participant in this conversation.")
            await self.close()
            return
        # if self.user not in [client.id, freelancer.id]:
            
        #     await self.close()  # Reject connection
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
    def get_conversation(self, room_name):
        from jobs.models import Conversation
        return Conversation.objects.get(id=room_name)
    
    @database_sync_to_async
    def get_participants(self, conversation):
        return (conversation.client, conversation.freelancer)


    @database_sync_to_async
    def save_message(self, conversation, sender, content):
        from jobs.models import Message
        return Message.objects.create(conversation=conversation, sender=sender, content=content)
