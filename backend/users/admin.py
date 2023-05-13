from django.contrib import admin
from django.contrib.admin import register

from users import models


@register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'first_name', 'last_name', 'email',
    )
    fields = (
        ('username', 'email', ),
        ('first_name', 'last_name', ),
    )

    search_fields = (
        'username', 'email',
    )


@register(models.Follow)
class FollowAdmin(admin.ModelAdmin):
    search_fields = (
        'user__username',
        'user__email',
        'following__username',
        'following__email',
    )
