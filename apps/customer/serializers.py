from datetime import date  

from rest_framework import serializers

from django.db.models import Q,Sum

from apps.customer.models import (
    Customer,
    AlternateContact,
)
import apps.customer.response_messages as resp_msg


class AlternateContactSerializer(serializers.ModelSerializer):
    """ Alternate contact serializer for customer. """

    class Meta:
        model = AlternateContact
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    """ Customer model serializer. """

    alternate_contact = AlternateContactSerializer()

    class Meta:
        model = Customer
        fields = '__all__' 
        read_only_fields = ('user', 'organization', 'point',)

    def validate_email(self, email):
        is_email_exist = Customer.objects.filter(email=email)
        if len(is_email_exist) > 0:
            raise serializers.ValidationError(resp_msg.CUSTOMER_EMAIL_ALREADY_EXIST)


class UpdateCustomerSerializer(serializers.ModelSerializer):
    """ Customer model serializer. """
    # industry_name = serializers.CharField(max_length=50,required=False)

    class Meta:
        model = Customer
        fields = '__all__' 
    
   
class CustomerFilterSerializer(serializers.ModelSerializer):
    ''' Serializer for customer filter list '''

    class Meta:
        model = Customer
        fields = ('id','full_name','email',)

class CustomerListSerializer(serializers.ModelSerializer):
    """ List of Customer serializer. """
    full_name = serializers.SerializerMethodField()
    outstanding_invoices = serializers.SerializerMethodField()
    open_balance = serializers.SerializerMethodField()
    overdue_balance = serializers.SerializerMethodField()

    def get_full_name(self,obj):
        return obj.full_name.title()

    def get_outstanding_invoices(self,obj):
        return obj.invoice.filter(~Q(invoice_status='PAYMENT_DONE')).count()

    def get_open_balance(self,obj):
        queryset = obj.invoice.all().exclude(invoice_status='PAYMENT_DONE')
        # .filter(due_date__gt = date.today())
        current_amount = queryset.aggregate(Sum('due_amount'))
        return current_amount['due_amount__sum'] if current_amount['due_amount__sum'] else 00


    def get_overdue_balance(self,obj):
        queryset = obj.invoice.all().exclude(invoice_status='PAYMENT_DONE')
        current_amount = queryset.filter(due_date__lt = date.today()).aggregate(Sum('due_amount'))
        return current_amount['due_amount__sum'] if current_amount['due_amount__sum'] else 00

    class Meta:
        model = Customer
        fields = ('pk','full_name','outstanding_invoices',
                'open_balance','overdue_balance') 

class CustomerRetriveDestroySerializer(serializers.ModelSerializer):
    """ Reterive and delete Customer record serializer. """
    # customer_type = serializers.CharField(source='get_customer_type_display')
    # payments_term = serializers.CharField(source='get_payments_term_display')

    class Meta:
        model = Customer
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            queryset = AlternateContact.objects.get(customer=instance)
            serializer = AlternateContactSerializer(queryset)
            representation['alternate_contact'] = serializer.data
        except Exception as e:
            representation['alternate_contact'] = None
        return representation