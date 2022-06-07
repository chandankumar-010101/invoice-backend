from statistics import mode
from django.db import models


class Customer(models.Model):

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
    primary_role = models.CharField(max_length=30, null=True, blank=True) #change later
    email = models.EmailField(max_length=254, unique=True)
    phone = models.CharField(max_length=30, null=True, blank=True, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customer'
        ordering = ['-created_on']

    def __str__(self):
        return self.full_name