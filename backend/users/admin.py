from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class UserAdmin(UserAdmin):
    list_display = ('email', 'username',)
    list_editable = ('username',)
    search_fields = ('email', 'username',)
