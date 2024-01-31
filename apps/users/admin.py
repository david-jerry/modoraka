from django.contrib import admin

# Register your models here.
from .models import User, TelegramGroup, GroupPinnedMessages, GroupOffenders, GroupAdmins, TelegramGroupMediaActions

admin.site.register(User)

admin.site.register(GroupPinnedMessages)

admin.site.register(GroupOffenders)

admin.site.register(GroupAdmins)

admin.site.register(TelegramGroup)

admin.site.register(TelegramGroupMediaActions)

