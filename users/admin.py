from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import PasswordReset, User

@admin.register(User)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'id']


admin.site.register(PasswordReset)