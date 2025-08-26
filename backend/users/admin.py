from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('email', 'username',)
    list_editable = ('username',)
    search_fields = ('email', 'username',)
