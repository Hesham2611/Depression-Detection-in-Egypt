from django.contrib import admin
from .models import Chat, Room
from .models import DepressedMessage

admin.site.register(Chat)
admin.site.register(Room)
admin.site.register(DepressedMessage)
