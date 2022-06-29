from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField

from django.db import models
from .managers import UserManager
from .constants import USER_TYPE_CHOICES


# Create your models here.
class Organization(models.Model):
    """ Organiation or company of the user.
    Every user is associated with organization/company
    th models have basic details of the company.
    """

    code = models.CharField(max_length=10, null=True, blank=True,unique=True)
    company_name = models.CharField(max_length=254, null=False,blank=False, unique=True)
    email = models.EmailField(max_length=255, null=False, blank=False, unique=True, db_index=True)
    phone_number = models.CharField(max_length=10, null=True,blank=True, unique=True, db_index=True)
    industry = models.CharField(max_length=255, null=True, blank=True)
    annual_turnover = models.CharField(max_length=255, null=True, blank=True)
    accounting_software = models.CharField(max_length=255, null=True, blank=True)
    estimate_invoice_issue = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organization'
        ordering = ['-created_on']

    def __str__(self):
        return self.company_name


class User(AbstractUser):
    """ Custom User model for users.
    
    Its a custom user model for the users that have very
    basic info of the user.
    """
    username = None
    email = models.EmailField(unique=True, null=True, db_index=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'User'


class UserProfile(models.Model):
    """ User profile model.
    
    User profile is models for basic information for the user
    every user profile is unique.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE,primary_key=True, related_name="profile")
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email

class StaticContent(models.Model):
    industry = models.JSONField(default=dict)
