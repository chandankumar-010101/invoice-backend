from django.contrib import admin
from .models import Organization
from .models import User
from .models import UserProfile


# Register your models here.
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("code", "company_name", "created_on")

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("first_name", "email", "is_verified")