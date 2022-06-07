from django.contrib import admin
from apps.customer.models import Customer

# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", 
            "is_active","created_on")