from django.contrib import admin

from . import models

admin.site.register(models.Subscribe)

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name',
    )