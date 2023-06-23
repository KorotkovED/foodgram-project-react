from django.contrib import admin
from .models import Subscribtion, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'first_name', 'last_name', 'email')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
    empty_value_display = "-пусто-"


class SubscribtionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')
    empty_value_display = "-пусто-"


admin.site.register(User, UserAdmin)
admin.site.register(Subscribtion, SubscribtionAdmin)
