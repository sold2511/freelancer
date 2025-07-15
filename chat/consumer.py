from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.contrib.auth import get_user_model


class ChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_user(self, user_id):

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
        print(
            f"Disconnected from room: {self.room_name}, close code: {close_code}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        username = self.user.username
        message = data.get('message')
        if message.strip().startswith("<a "):
            attachments = message
            content=''
        else:
            content = message
            attachments=None

        if not message:
            # If both message and attachments are empty, we do not send anything
            return
        # Prepare the full message

        # Save to DB

        await self.save_message(self.conversation, self.user, content,attachments)

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
    def save_message(self, conversation, sender, content,attachments):
        from jobs.models import Message
        return Message.objects.create(conversation=conversation, sender=sender, content=content,attachments=attachments)


class VideoChat(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive_json(self, content):
        if content['command'] == 'join_room':
            await self.channel_layer.group_add(content['room'], self.channel_name)

        elif content['command'] == 'join':
            await self.channel_layer.group_send(content['room'], {
                "type": "join.message",

            })
        elif content['command'] == 'offer':
            await self.channel_layer.group_send(content['room'], {
                "type": "offer.message",
                'offer': content['offer']

            })
        elif content['command'] == 'answer':
            await self.channel_layer.group_send(content['room'], {
                'type': "answer.message",
                'answer': content['answer']
            })
        elif content['command'] == 'candidate':
            await self.channel_layer.group_send(content['room'], {
                'type': "candidate.message",
                'candidate': content['candidate'],
                'isCreated': content['isCreated']
            })
        elif content['command'] == 'end':
            await self.channel_layer.group_send(content['room'], {
                'type': 'end.message',
                'is_closed':True
            })

    async def end_message(self, event):
        await self.send_json({
            'command': 'end'
        })

    async def join_message(self, event):
        await self.send_json({
            'command': 'join'
        })

    async def offer_message(self, event):
        await self.send_json({
            'command': 'offer',
            'offer': event['offer']
        })

    async def answer_message(self, event):
        await self.send_json({
            'command': 'answer',
            'answer': event['answer']
        })

    async def candidate_message(self, event):
        await self.send_json({
            'command': 'candidate',
            'candidate': event['candidate'],
            'isCreated': event['isCreated']
        })
