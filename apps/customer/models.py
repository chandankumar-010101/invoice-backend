from django.db import models
from apps.account.models import Organization
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField

from .constants import (
    CUSTOMER_TYPE_CHOICE,
    PAYMENT_TERM_CHOICE
)

User = get_user_model()

class Customer(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='org', default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='customer', default=None)
    customer_type = models.PositiveSmallIntegerField(choices = CUSTOMER_TYPE_CHOICE,default=4)
    full_name = models.CharField(max_length=30, null=False, blank=False)
    pin_number = models.CharField(max_length=30, null=True, blank=True)
    industry_name = models.CharField(max_length=255, null=True, blank=True,default='')
    postal_address = models.TextField(max_length=254, null=True, blank=True)
    postal_city = models.CharField(max_length=30, null=True, blank=True)
    postal_country = models.CharField(max_length=30, null=True, blank=True)
    shipping_address = models.TextField(max_length=254, null=True, blank=True)
    shipping_city = models.CharField(max_length=30, null=True, blank=True)
    shipping_country = models.CharField(max_length=30, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)
    payments_term = models.PositiveSmallIntegerField(choices = PAYMENT_TERM_CHOICE,default=6)
    payments_credit = models.IntegerField(null=True, blank=True,default=0)
    is_active = models.BooleanField(default=True)
    outstanding_invoices = models.IntegerField(null=True, blank=True, default=0)
    open_balance = models.FloatField(null=True, blank=True, default=0.0)
    overdue_balance = models.FloatField(null=True, blank=True, default=0.0)
    primary_name = models.CharField(max_length=30, null=True, blank=True)
    primary_role = models.CharField(max_length=30, null=True, blank=True)
    primary_email = models.EmailField(max_length=254,unique=True)
    # primary_phone = models.CharField(max_length=30,null=True, blank=True,unique=True)
    primary_phone = PhoneNumberField(null=True, blank=True,)


    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customer'
        ordering = ['-created_on']

    def __str__(self):
        return self.full_name

class AlternateContact(models.Model):
    """ Alternate contact for the customer."""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE,related_name='customer', default=None)
    alternate_name = models.CharField(max_length=30, null=True, blank=True)
    alternate_role = models.CharField(max_length=30, null=True, blank=True)
    alternate_email = models.EmailField(max_length=254,null=True, blank=True)
    alternate_phone = PhoneNumberField(null=True, blank=True,)

