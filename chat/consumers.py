from chat.models import Chat, Room
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async, async_to_sync
import re
import os
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras import backend as K
from numpy import argmax
import gc
from users.models import Profile
from django.shortcuts import get_object_or_404
from notification.models import Notification

# Create your views here.
static_files_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/emotion_classifier/savedModels/')


def read_pkl_object(file_path):
    with open(file_path, 'rb') as file:
        pickle_obj = pickle.load(file)
    return pickle_obj


tokenizer = read_pkl_object(static_files_path + 'tokenizer.pkl')
classifier = load_model(static_files_path)
print("EMOTION IS LOADED")


def clean(text):
    text = re.sub(r'[^a-zA-Z ]', '', text)
    text = text.lower()
    return text


def tokenize(text):
    sequence = tokenizer.texts_to_sequences([text])
    tokens = pad_sequences(sequence, maxlen=257, truncating='pre')
    return tokens


def detect(text):
    cleaned_text = clean(text)
    tokens = tokenize(cleaned_text)
    classification_result = classifier(tokens).numpy()[0][0]
    is_depression = classification_result >= 0.5
    probability = classification_result * 100
    K.clear_session()

    return is_depression


@sync_to_async
def create_new_message(me, friend, message, room_id):
    get_room = Room.objects.filter(room_id=room_id)[0]
    author_user = User.objects.filter(username=me)[0]
    friend_user = User.objects.filter(username=get_room.friend)[0]
    new_chat = Chat.objects.create(
        author=author_user,
        friend=friend_user,
        room_id=get_room,
        text=message)


@sync_to_async
def update_depression(me, room_id, is_depressed):
    if is_depressed:
        user = User.objects.filter(username=me)[0]
        profile = get_object_or_404(Profile, user=user)
        profile.is_depressed = True
        profile.save()
        get_room = Room.objects.filter(room_id=room_id)[0]
        friend_user = User.objects.filter(username=get_room.friend)[0]
        for x in profile.following_relatives.all():
            notify = Notification(sender=user, user=x, notification_type=8)
            notify.save()


class ChatRoomConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.depressive_count = 0
        self.depressed_messages = []

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        user_image = text_data_json['user_image']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chatroom_message',
                'message': message,
                'username': username,
                'user_image': user_image,
            }
        )

    async def chatroom_message(self, event):
        message = event['message']
        username = event['username']
        user_image = event['user_image']
        is_depressed = detect(message)

        await create_new_message(me=self.scope["user"], friend=username, message=message, room_id=self.room_name)

        if is_depressed:
            self.depressive_count += 1
            self.depressed_messages.append(message)

        if self.depressive_count >= 10:
            await update_depression(me=self.scope["user"], room_id=self.room_name, is_depressed=True)
            user = User.objects.filter(username=self.scope["user"])[0]
            profile = get_object_or_404(Profile, user=user)
            for x in profile.following_relatives.all():
                notify = Notification(sender=user, user=x, notification_type=8)
                notify.save()
            self.depressive_count = 0
            self.depressed_messages.clear()
        else:
            await update_depression(me=self.scope["user"], room_id=self.room_name, is_depressed=False)

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'user_image': user_image,
        }))