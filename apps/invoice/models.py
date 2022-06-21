from django.db import models
from apps.customer.models import Customer
from .constants import INVOICE_STATUS


# Create your models here.
class Invoice(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    po_number = models.CharField(max_length=255, null=True,blank=True, unique=True)
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
    curreny = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoice'

    def __str__(self):
        return self.invoice_number