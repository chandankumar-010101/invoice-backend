from django.contrib import admin
from .models import Organization
from .models import User
from .models import UserProfile,StaticContent


# Register your models here.

@admin.register(StaticContent)
class StaticContentAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("code", "company_name", "created_on")

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "is_verified")