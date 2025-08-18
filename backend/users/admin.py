from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username',)
    list_editable = ('email', 'username')
    search_fields = ('email', 'username',)
