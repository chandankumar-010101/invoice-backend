from django.contrib import admin
from .models import Invoice

# Register your models here.
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = ("invoice_number", "po_number", "get_customer_name",
                    "invoice_date", "due_date", "due_amount",
                    "total_amount")


    @admin.display(description='Customer Name')
    def get_customer_name(self, obj):
        return obj.customer.full_name
