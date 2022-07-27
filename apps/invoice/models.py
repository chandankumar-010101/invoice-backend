import uuid

from django.db import models
from apps.customer.models import Customer
from .constants import INVOICE_STATUS,PAYMENT_MODE


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
    payment_mode = models.CharField(max_length=255, choices=PAYMENT_MODE, default="Manually") 
    tx_id = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)