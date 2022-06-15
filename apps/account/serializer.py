from rest_framework import serializers
from .models import Organization 
from .utils import generate_organization_code


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
    email_address = serializers.CharField(max_length=50)
    phone_number = serializers.IntegerField()
    company_name = serializers.CharField(max_length=100,required=False)
    industry = serializers.CharField(max_length=50)
    anuual_turnover = serializers.FloatField()
    accounting_software = serializers.CharField(max_length=100)
    invoice_issue_month = serializers.IntegerField()
    password = serializers.CharField(max_length=100)

class LoginSerializers(serializers.Serializer):

     email = serializers.CharField(max_length=255)
     password = serializers.CharField(max_length=128, write_only=True)  


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


