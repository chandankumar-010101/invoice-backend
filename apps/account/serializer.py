from rest_framework import serializers
from .models import Organization 
from .models import UserProfile 
from django.contrib.auth import get_user_model
import apps.account.response_messages as resp_msg
User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ('code',)

class SignupSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=50)
    phone_number = serializers.IntegerField()
    company_name = serializers.CharField(max_length=100,required=False)
    industry = serializers.CharField(max_length=50)
    annual_turnover = serializers.CharField(max_length=100)
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
            raise serializers.ValidationError({'detail':resp_msg.EMAIL_DOES_NOT_EXIST})

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

class UserCreateSerializer(serializers.Serializer):

    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=50)
    phone_number = serializers.CharField(max_length=255)
    role = serializers.IntegerField()
    password = serializers.CharField(max_length=255)

    def validate_email(self, email):
        is_email_exist = User.objects.filter(email=email).exists()
        if is_email_exist:
            raise serializers.ValidationError(resp_msg.USER_ALREADY_EXISTS)

    def validate_phone(self, phone):
        is_phone_exist = UserProfile.objects.filter(phone=phone)
        if len(is_phone_exist) > 0:
            raise serializers.ValidationError(resp_msg.PHONE_ALREADY_EXISTS)

    def validate_role(self, role):
        if role < 1 or role > 6:
            raise serializers.ValidationError(resp_msg.INVALID_ROLE_SELECTED)

    def validate_password(self, password):
        if len(password) < 8:
            raise serializers.ValidationError(resp_msg.PASSWORD_VALIDATION)

        lower = any(letter.islower() for letter in password)
        upper = any(letter.isupper() for letter in password)
        if not upper:
            raise serializers.ValidationError(resp_msg.PASSWORD_VALIDATION)
        if not lower:
            raise serializers.ValidationError(resp_msg.PASSWORD_VALIDATION)
       
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id','email', 'user_type', )

class UserProfileListSerializer(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ('pk', 'full_name', 'email', 'organization', 'user')

class ProfileupdateSerializer(serializers.Serializer):

    user_name = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=50)
    company = serializers.CharField(max_length=100)
    role = serializers.CharField(max_length=100)
    status = serializers.BooleanField(default=True)

class PasswordchangeSerializer(serializers.Serializer):

    current_password = serializers.CharField(max_length=128,write_only=True)
    new_password = serializers.CharField(max_length=128,write_only=True)

    def validate_new_password(self, password):
        if len(password) < 8:
            raise serializers.ValidationError(resp_msg.PASSWORD_VALIDATION)

        lower = any(letter.islower() for letter in password)
        upper = any(letter.isupper() for letter in password)
        if not upper:
            raise serializers.ValidationError(resp_msg.PASSWORD_VALIDATION)
        if not lower:
            raise serializers.ValidationError(resp_msg.PASSWORD_VALIDATION)
