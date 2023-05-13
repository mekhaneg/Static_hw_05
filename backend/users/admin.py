from django.contrib import admin
from django.contrib.admin import register

from users import models


admin.site.register(models.Follow)


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
    list_filter = (
        'first_name', 'email',
    )
