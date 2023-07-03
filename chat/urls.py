from django.urls import path
from .views import room_enroll, room_choice, room, depressed_messages

urlpatterns = [
    path('', room_enroll, name='room-enroll'),
    path('chat/<int:friend_id>', room_choice, name='room-choice'),
    path('room/<int:room_name>-<int:friend_id>', room, name='room'),
    path('depressed/', depressed_messages, name='depressed_messages'),]