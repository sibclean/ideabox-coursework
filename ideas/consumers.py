import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        if self.scope["user"].is_anonymous:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action_type = text_data_json.get('type')
        user = self.scope["user"]

        if action_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'user_typing', 'username': user.username, 'is_typing': text_data_json['is_typing']}
            )
        
        elif action_type == 'chat_message':
            message_text = text_data_json.get('message')
            if message_text:
                saved_message = await self.save_message(user, self.conversation_id, message_text)
                info = await self.get_user_meta(user)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message_id': saved_message.id,
                        'message': message_text,
                        'username': user.username,
                        'full_name': info['full_name'],
                        'avatar_url': info['avatar_url'],
                        'role': info['role'], # Передаем роль
                        'created_at': saved_message.created_at.strftime('%H:%M')
                    }
                )
        
        elif action_type == 'edit_message':
            message_id = text_data_json.get('message_id')
            new_text = text_data_json.get('new_text')
            if await self.edit_message_db(user, message_id, new_text):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {'type': 'message_edited', 'message_id': message_id, 'new_text': new_text}
                )

        elif action_type == 'delete_message':
            message_id = text_data_json.get('message_id')
            if await self.delete_message_db(user, message_id):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {'type': 'message_deleted', 'message_id': message_id}
                )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message', 'message_id': event['message_id'], 'message': event['message'],
            'username': event['username'], 'full_name': event['full_name'], 'avatar_url': event['avatar_url'],
            'role': event['role'], # Транслируем роль
            'created_at': event['created_at']
        }))

    async def chat_file_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message', 'message_id': event['message_id'], 'message': event['text'],
            'username': event['username'], 'full_name': event['full_name'], 'avatar_url': event['avatar_url'],
            'role': event['role'], # Транслируем роль
            'image_url': event['image_url'], 'file_url': event['file_url'],
            'created_at': event['created_at']
        }))

    async def user_typing(self, event):
        await self.send(text_data=json.dumps({'type': 'typing', 'username': event['username'], 'is_typing': event['is_typing']}))

    async def message_edited(self, event):
        await self.send(text_data=json.dumps({'type': 'message_edited', 'message_id': event['message_id'], 'new_text': event['new_text']}))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({'type': 'message_deleted', 'message_id': event['message_id']}))

    @database_sync_to_async
    def save_message(self, user, conversation_id, text):
        conversation = Conversation.objects.get(id=conversation_id)
        return Message.objects.create(conversation=conversation, sender=user, text=text)

    @database_sync_to_async
    def get_user_meta(self, user):
        profile = user.profile
        full_name = f"{profile.last_name or ''} {profile.first_name or ''}".strip() or user.username
        avatar_url = profile.avatar.url if profile.avatar else None
        return {'full_name': full_name, 'avatar_url': avatar_url, 'role': profile.role}

    @database_sync_to_async
    def edit_message_db(self, user, message_id, new_text):
        try:
            msg = Message.objects.get(id=message_id, sender=user)
            msg.text = new_text
            msg.save()
            return True
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def delete_message_db(self, user, message_id):
        try:
            Message.objects.get(id=message_id, sender=user).delete()
            return True
        except Message.DoesNotExist:
            return False
