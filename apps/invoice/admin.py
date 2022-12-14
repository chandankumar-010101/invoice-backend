from django.contrib import admin
from .models import (
    Invoice,
    InvoiceAttachment,
    InvoiceTransaction,RolesAndPermissions,
    PaymentReminder,CardDetail,Notification,
    Subscription,UserSubscriptionTransaction,UserSubscription
)

# Register your models here.
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = (
        "invoice_number","get_customer_name","invoice_status","invoice_date", "due_date", "due_amount","total_amount"
    )

    @admin.display(description='Customer Name')
    def get_customer_name(self, obj):
        return obj.customer.full_name


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):

    list_display = (
        "id","name","no_of_users","storage","amount"
    )


@admin.register(PaymentReminder)
class PaymentReminderAdmin(admin.ModelAdmin):

    list_display = (
        "id","user","is_sent_on_email","is_sent_on_whatsapp"
    )


@admin.register(CardDetail)
class CardDetailAdmin(admin.ModelAdmin):

    list_display = (
        "id",
    )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
    )


@admin.register(UserSubscriptionTransaction)
class UserSubscriptionTransactionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "id","user","is_seen"
    )


@admin.register(InvoiceAttachment)
class InvoiceAttachmentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
    )


@admin.register(RolesAndPermissions)
class RolesAndPermissionsAdmin(admin.ModelAdmin):

    list_display = (
        "id",'user'
    )

@admin.register(InvoiceTransaction)
class InvoiceTransactionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
    )