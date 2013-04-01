from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from models import DacUser

# Define inline admin descriptor for DacUser
class DacUserInline(admin.StackedInline):
    model = DacUser
    can_delete_ = False
    verbose_name_plural = 'Profile Information'

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (DacUserInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
