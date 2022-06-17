from rest_framework import serializers
from apps.customer.models import Customer 
from apps.customer.models import AlternateContact
import apps.customer.response_messages as resp_msg


class AlternateContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = AlternateContact
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):

    alternate_contact = AlternateContactSerializer()

    class Meta:
        model = Customer
        fields = '__all__' 

    def validate_email(self, email):
        is_email_exist = Customer.objects.filter(email=email)
        if len(is_email_exist) > 0:
            raise serializers.ValidationError(resp_msg.CUSTOMER_EMAIL_ALREADY_EXIST)

class CustomerFilterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ('id','full_name','email',)

class CustomerListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ('pk','full_name','outstanding_invoices',
                'open_balance','overdue_balance') 