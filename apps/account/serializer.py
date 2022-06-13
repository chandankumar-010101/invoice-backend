from rest_framework import serializers
from .models import Organization 
from .models import UserProfile 
from .utils import generate_organization_code
from django.contrib.auth import get_user_model
import apps.account.response_messages as resp_msg
User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ('code',)

    def create(self, validated_data):
        """ Overrirde serializer save method.
        
        Override the method for saving organization code,
        organization code is auto-generated 10 charcter unique code
        for every organization.
        """
        validated_data['code'] = generate_organization_code()
        return super(OrganizationSerializer, self).create(validated_data)

class SignupSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=50)
    phone_number = serializers.IntegerField()
    company_name = serializers.CharField(max_length=100,required=False)
    industry = serializers.CharField(max_length=50)
    anuual_turnover = serializers.FloatField()
    accounting_software = serializers.CharField(max_length=100)
    invoice_issue_month = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=50)

    def validate_email(self, email):
        is_email_exist = User.objects.filter(email=email).exists()
        if is_email_exist:
            raise serializers.ValidationError(resp_msg.EMAIL_ALREADY_EXISTS)

    def validate_phone_number(self, phone_number):
        is_phone_exist = Organization.objects.filter(phone_number=phone_number)
        if len(is_phone_exist) > 0:
            raise serializers.ValidationError(resp_msg.PHONE_ALREADY_EXISTS)

    def validate_company_name(self, company_name):
        is_phone_exist = Organization.objects.filter(company_name=company_name)
        if len(is_phone_exist) > 0:
            raise serializers.ValidationError(resp_msg.COMPANY_ALREADY_EXISTS)

    def validate_password(self, password):
        if len(password) < 8:
            raise serializers.ValidationError(resp_msg.PASSWORD_VALIDATION)

        lower = any(letter.islower() for letter in password)
        upper = any(letter.isupper() for letter in password)
        if not upper:
            raise serializers.ValidationError(resp_msg.PASSWORD_VALIDATION)
        if not lower:
            raise serializers.ValidationError(resp_msg.PASSWORD_VALIDATION)

class LoginSerializers(serializers.Serializer):

    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)   

    def validate(self, validate_data):
        email = validate_data.get('email')
        is_email_exist = User.objects.filter(email=email).exists()
        if not is_email_exist:
            raise serializers.ValidationError(resp_msg.EMAIL_DOES_NOT_EXIST)

        is_user_active = User.objects.get(email=email).is_active
        if not is_user_active:
            raise serializers.ValidationError(resp_msg.USER_NOT_ACTIVE)

        if not is_user_active:
            raise serializers.ValidationError(resp_msg.USER_NOT_ACTIVE)

        return validate_data
       
class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = '__all__'
