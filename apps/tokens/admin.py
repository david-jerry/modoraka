from django.contrib import admin

# Register your models here.
from .models import Tokens, WatchToken, WatchAddress

admin.site.register(Tokens)

admin.site.register(WatchToken)

admin.site.register(WatchAddress)
