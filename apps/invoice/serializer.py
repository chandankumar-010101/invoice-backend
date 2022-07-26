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
    reminders = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    additional_email = serializers.SerializerMethodField()
    due_date_status = serializers.SerializerMethodField()


    def get_due_date_status(self,obj):
        from datetime import date  
        td = date.today()
        if (td-obj.due_date).days > 1:
            return "Due in {} days".format((td-obj.due_date).days)
        return "Overdue by {} days".format(abs((td-obj.due_date).days))

        

    def get_additional_email(self,obj):
        if hasattr(obj.customer, 'customer'):
            return obj.customer.customer.alternate_email
        return None

    def get_organization(self,obj):
        return obj.customer.organization.company_name

    def get_reminders(self,obj):
        if obj.reminders == 0:
            return 'Reminder Not Sent'
        return '{} Reminder Sent'.format(ordinal(obj.reminders))

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
        instance = Invoice.objects.create(
            **validated_data
        )
        return instance

    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('untaxed_amount','vat_amount','notes','curreny')




