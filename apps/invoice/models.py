import uuid

from django.db import models
from apps.customer.models import Customer
from .constants import INVOICE_STATUS,PAYMENT_MODE,PAYMENT_TYPE,REMINDER_TYPE,PAYMENT_TYPE_CHOICES
from django.contrib.auth import get_user_model

User = get_user_model()

from apps.utility.helpers import filename_path

def invoice_attachment(instance, filename):
    return filename_path('invoice', instance, filename)


# Create your models here.
class Invoice(models.Model):
    invoice_id = models.UUIDField(default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,related_name="invoice")
    invoice_number = models.CharField(max_length=255, null=True, blank=True, unique=True)
    invoice_date = models.DateField()
    due_date = models.DateField()
    due_amount = models.FloatField(max_length=255, default=0.0, null=True, blank=True)
    invoice_status = models.CharField(max_length=255, choices=INVOICE_STATUS, default="UNSENT") 
    untaxed_amount = models.FloatField(max_length=255, default=0.0, null=True, blank=True)
    vat_amount = models.FloatField(max_length=255, default=0.0, null=True, blank=True)
    total_amount = models.FloatField(max_length=255, default=0.0, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)
    curreny = models.CharField(max_length=255, default='KES')
    reminders = models.IntegerField(null=True, blank=True, default=0)
    is_online_payment = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoice'
        ordering = ('-id',)
        

    def __str__(self):
        return self.invoice_number

class InvoiceAttachment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE,related_name="invoice_attachment")
    attachment = models.FileField(upload_to=invoice_attachment, blank=True, null=True) 

    class Meta:
        ordering = ('id',)


class InvoiceTransaction(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE,related_name="invoice_transaction")
    payment_type = models.CharField(max_length=255, choices=PAYMENT_TYPE, default="Manually") 
    payment_mode = models.CharField(max_length=255, choices=PAYMENT_MODE, default="Cash") 
    tx_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.FloatField(max_length=255, default=0.0, null=True, blank=True)
    payment_date = models.DateField(null=True,blank=True)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

class PaymentMethods(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="payment_method")
    is_bank_transfer = models.BooleanField(default=False)
    is_card_payment = models.BooleanField(default=False)
    is_mobile_money = models.BooleanField(default=False)
    auto_payment_reminder = models.BooleanField(default=False)

class PaymentReminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="reminder_user")
    days = models.IntegerField(null=True, blank=True, default=0)
    reminder_type = models.CharField(max_length=255, choices=REMINDER_TYPE, default="Due In") 
    subject = models.CharField(max_length=255, null=True, blank=True,)
    body = models.TextField(null=True,blank=True)
    is_sent_on_whatsapp = models.BooleanField(default=False)
    is_sent_on_email = models.BooleanField(default=False)

class RolesAndPermissions(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="roles_permission_user")
    roles = models.JSONField(default=dict)


class CardDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="card_details_user")
    payment_type = models.PositiveSmallIntegerField(choices=PAYMENT_TYPE_CHOICES)
    holder_name = models.CharField(max_length= 50, null=True, blank=False)
    card_number = models.CharField(max_length=16,null=True,blank=False)
    expiry_date = models.DateField()
    cvv_code = models.CharField(max_length=3,null=True,blank=False)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="notification_user")
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE,null=True,blank=True,related_name="notification_invoice")
    title = models.CharField(max_length= 150, null=True, blank=False)
    message = models.CharField(max_length= 255, null=True, blank=False)
    icon_class = models.CharField(max_length=150,null=True,blank=True,default='fa fa-clock-o')
    icon_colour = models.CharField(max_length=150,null=True,blank=True,default='red')
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('id',)