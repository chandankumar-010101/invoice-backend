from rest_framework import serializers

from .models import Invoice,InvoiceAttachment

from apps.utility.helpers import ordinal
class InvoiceAttachmentSerializer(serializers.ModelSerializer):

    attachment = serializers.SerializerMethodField()
    def get_attachment(self,obj):
        if obj.attachment:
            return obj.attachment.url
        return None

    class Meta:
        model = InvoiceAttachment
        fields = ('id','attachment')

class GetInvoiceSerializer(serializers.ModelSerializer):

    customer = serializers.SerializerMethodField()
    customer_email = serializers.SerializerMethodField()
    customer_id = serializers.SerializerMethodField()
    invoice_attachment = InvoiceAttachmentSerializer(many=True)
    reminder = serializers.SerializerMethodField()

    def get_reminder(self,obj):
        return 'Reminder Not Sent'
        # if obj.reminder == 0:
        #     return 'Reminder Not Sent'
        # return '{} Reminder Sent'.format(ordinal(obj.reminder))

    def get_customer_email(self,obj):
        return obj.customer.primary_email

    def get_customer(self,obj):
        return obj.customer.full_name

    def get_customer_id(self,obj):
        return obj.customer.id
        
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('customer','untaxed_amount','vat_amount','notes','curreny',)


class InvoiceSerializer(serializers.ModelSerializer):
    
    attachment = serializers.FileField(required=False)
    invoice_number = serializers.CharField(required=True)
    due_date = serializers.DateField(required=True)
    total_amount = serializers.FloatField(required=True)
    due_amount = serializers.FloatField(required=True)


    def create(self, validated_data):
        validated_data.pop('attachment')
        print(validated_data)

        instance = Invoice.objects.create(
            **validated_data
        )
        return instance

    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('untaxed_amount','vat_amount','notes','curreny')
