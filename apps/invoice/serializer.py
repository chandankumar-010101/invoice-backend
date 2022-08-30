from rest_framework import serializers
from django.db.models import Q,Sum


from .models import Invoice,InvoiceAttachment,PaymentReminder,CardDetail,InvoiceTransaction,Notification
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
    additional_phone = serializers.SerializerMethodField()
    primary_phone = serializers.SerializerMethodField()
    additional_phone = serializers.SerializerMethodField()
    due_date_status = serializers.SerializerMethodField()
    payments_term = serializers.SerializerMethodField()
    
    def get_payments_term(self,obj):
        try:
            payments_term = obj.customer.get_payments_term_display().split(" ")
            return payments_term[1]
        except:
            return None

    def get_due_date_status(self,obj):
        from datetime import date  
        td = date.today()
        if (td-obj.due_date).days == 0:
            return {
                'color':'#000000',
                'days':"Due Today"
            }
            
        elif (td-obj.due_date).days > 1:
            return {
                'color':'#FE6867',
                'days':"Overdue by {} days".format(abs((td-obj.due_date).days))
            }
        elif abs((td-obj.due_date).days) == 1:
            return {
                'color':'#000000',
                'days':"Due Tomorrow"
            }
        return {
            'color':'#000000',
            'days':"Due in {} days".format(abs((td-obj.due_date).days))
        }

    def get_primary_phone(self,obj):
        return str(obj.customer.primary_phone)

    def get_additional_phone(self,obj):
        if hasattr(obj.customer, 'customer'):
            return str(obj.customer.customer.alternate_phone)
        return None


    def get_additional_email(self,obj):
        if hasattr(obj.customer, 'customer'):
            return obj.customer.customer.alternate_email
        return None

    def get_organization(self,obj):
        return obj.customer.organization.company_name

    def get_reminders(self,obj):
        if obj.reminders == 0:
            return 'No Reminder Sent'
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
    is_online_payment = serializers.BooleanField(required=True)

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



class PaymentReminderSerializer(serializers.ModelSerializer):

    def create(self,validated_data):
        request = self.context.get('request')
        admin_user = request.user.parent if request.user.parent else request.user
        instance = PaymentReminder.objects.create(
            user = admin_user,
            **validated_data
        )
        return instance


    class Meta:
        model = PaymentReminder
        fields = '__all__'
        read_only_fields = ('user',)

class CardSerializer(serializers.Serializer):
    
    payment_type = serializers.CharField(max_length=255)
    holder_name = serializers.CharField(max_length=255)
    card_number = serializers.CharField()
    expiry_date= serializers.DateField()
    cvv_code  = serializers.CharField()


    def create(self,validated_data):
        request = self.context.get('request')
        params = request.data
        admin_user = request.user.parent if request.user.parent else request.user

        return CardDetail.objects.create(
            user=admin_user,
            payment_type = params['payment_type'],
            holder_name = params['holder_name'],
            card_number = params['card_number'],
            expiry_date = params['expiry_date'],
            cvv_code = params['cvv_code'],
        )
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        params = request.data
        instance.payment_type = params['payment_type']
        instance.holder_name = params['holder_name']
        instance.card_number = params['card_number']
        instance.expiry_date = params['expiry_date']
        instance.cvv_code = params['cvv_code']
        instance.save()
        return instance

    
    def validate_card_number(self, card_number):
        if len(card_number) != 16:
            raise serializers.ValidationError("Card No must be 16 digits.")

    def validate_expiry_date(self, expiry_date):
        from datetime import date  
        if (expiry_date-date.today()).days < 1:
            raise serializers.ValidationError("Expiry date should be future date.")

    def validate_cvv_code(self, cvv_code):
        if len(cvv_code) != 3:
            raise serializers.ValidationError("Cvv No must be 3 digits.")

class GetPaymentSerializer(serializers.ModelSerializer):

    # amount = serializers.SerializerMethodField()

    # def get_amount(self,obj):
    #     total = obj.invoice_transaction.all().aggregate(Sum('amount'))
    #     return total['amount__sum'] if total['amount__sum'] else 00
    
    
    payment_method = serializers.SerializerMethodField()
    def get_payment_method(self,obj):
        return obj.payment_mode

    invoice_number = serializers.SerializerMethodField()
    def get_invoice_number(self,obj):
        return obj.invoice.invoice_number
    
    due_date = serializers.SerializerMethodField()
    def get_due_date(self,obj):
        return obj.invoice.due_date

    customer = serializers.SerializerMethodField()
    def get_customer(self,obj):
        return obj.invoice.customer.full_name

        
    class Meta:
        model = InvoiceTransaction
        fields = ("customer","invoice_number","updated_on","due_date","payment_method","amount")


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ('id','message',"title",'is_seen','invoice')