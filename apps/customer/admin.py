from django.contrib import admin
from apps.customer.models import (
    Customer,
    AlternateContact
)


# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("full_name","is_active","created_on")


@admin.register(AlternateContact)
class AlternateContactAdmin(admin.ModelAdmin):
    list_display = ("alternate_email",)