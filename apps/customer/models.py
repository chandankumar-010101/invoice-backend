from statistics import mode
from django.db import models
from .constants import CUSTOMER_TYPE_CHOICE
from .constants import PAYMENT_TERM_CHOICE


class Customer(models.Model):

    customer_type = models.PositiveSmallIntegerField(choices = CUSTOMER_TYPE_CHOICE,
                                                    default=4)
    full_name = models.CharField(max_length=30, null=False, blank=False)
    pin_number = models.CharField(max_length=30, null=True, blank=True)
    industry_name = models.CharField(max_length=30, null=False, blank=False)
    billing_address = models.TextField(max_length=254, null=False, blank=False)
    billing_city = models.CharField(max_length=30, null=False, blank=False)
    billing_country = models.CharField(max_length=30, null=False, blank=False)
    shipping_address = models.TextField(max_length=254, null=False, blank=False)
    shipping_city = models.CharField(max_length=30, null=False, blank=False)
    shipping_country = models.CharField(max_length=30, null=False, blank=False)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)
    primary_name = models.CharField(max_length=30, null=True, blank=True)
    primary_role = models.PositiveSmallIntegerField(choices = CUSTOMER_TYPE_CHOICE, default=4)
    email = models.EmailField(max_length=254, unique=True)
    phone = models.CharField(max_length=30,null=True, blank=True, unique=True)
    payments_term = models.PositiveSmallIntegerField(choices = PAYMENT_TERM_CHOICE,
                                                    default=6)
    payments_credit = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customer'
        ordering = ['-created_on']

    def __str__(self):
        return self.full_name

class AlternateContact(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, 
                                        related_name='customer', default=None)
    alternate_name = models.CharField(max_length=30, null=True, blank=True)
    alternate_role = models.PositiveSmallIntegerField(choices = CUSTOMER_TYPE_CHOICE, 
                                                default=4)
    alternate_email = models.EmailField(max_length=254, unique=True)
    alternate_phone = models.CharField(max_length=30,null=True, blank=True)
