from pickle import TRUE
from statistics import mode
from django.db import models

# Create your models here.
class Organization(models.Model):

    name = models.CharField(max_length=254, null=False, blank=False)
    email = models.EmailField(max_length=30, null=False, blank=False, unique=True)
    address = models.TextField(max_length=30, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    country = models.CharField(max_length=30, null=False, blank=False)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organization'
        ordering = ['-created_on']

    def __str__(self):
        return self.name