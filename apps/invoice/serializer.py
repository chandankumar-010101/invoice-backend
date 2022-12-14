from rest_framework import serializers
from django.db.models import Q,Sum

from apps.customer.models import Customer


from .models import (
    Invoice,InvoiceAttachment,
    PaymentReminder,CardDetail,
    InvoiceTransaction,Notification,
    Subscription

)
from apps.utility.helpers import ordinal


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = "__all__"

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
    days = serializers.SerializerMethodField()
    
    def get_payments_term(self,obj):
        try:
            payments_term = obj.customer.get_payments_term_display().split(" ")
            return payments_term[1]
        except:
            return None

    def get_days(self,obj):
        from datetime import date  
        td = date.today()
        if (td-obj.due_date).days == 0:
            return "Due Today"
        elif (td-obj.due_date).days > 1:
            return "Overdue by {} days".format(abs((td-obj.due_date).days))
        elif abs((td-obj.due_date).days) == 1:
            return "Due Tomorrow"
        return "Due in {} days".format(abs((td-obj.due_date).days))

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
    
    # payment_type = serializers.CharField(max_length=255)
    holder_name = serializers.CharField(max_length=255)
    card_number = serializers.CharField()
    expiry_month= serializers.CharField()
    expiry_year= serializers.CharField()
    card_type = serializers.CharField()
    cvv_code  = serializers.CharField()
    m_pesa  = serializers.CharField(required=False)
    is_auto_subscription = serializers.BooleanField(required=False)

    def create(self,validated_data):
        request = self.context.get('request')
        params = request.data
        admin_user = request.user.parent if request.user.parent else request.user

        return CardDetail.objects.create(
            user=admin_user,
            # payment_type = params['payment_type'],
            holder_name = params['holder_name'],
            card_number = params['card_number'],
            expiry_month = params['expiry_month'],
            expiry_year = params['expiry_year'],
            cvv_code = params['cvv_code'],
            card_type = params['card_type']
        )
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        params = request.data
        # instance.payment_type = params['payment_type']
        instance.holder_name = params['holder_name']
        instance.card_number = params['card_number']
        instance.expiry_month = params['expiry_month']
        instance.expiry_year = params['expiry_year']
        instance.card_type = params['card_type']
        instance.cvv_code = params['cvv_code']

        instance.save()
        return instance

    
    def validate_card_number(self, card_number):
        if len(card_number) != 16:
            raise serializers.ValidationError("Card No must be 16 digits.")

    # def validate_expiry_date(self, expiry_date):
    #     from datetime import date  
    #     if (expiry_date-date.today()).days < 1:
    #         raise serializers.ValidationError("Expiry date should be future date.")

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
        fields = "__all__"


class GetAgeingReportsSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    not_overdue = serializers.SerializerMethodField()
    not_overdue_invoices = serializers.SerializerMethodField()
    thirty_or_less = serializers.SerializerMethodField()
    thirty_one_to_sixty = serializers.SerializerMethodField()
    sixty_to_ninty = serializers.SerializerMethodField()
    ninty_or_more = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    total_invoices = serializers.SerializerMethodField()

    def get_customer(self,obj):
        return obj.full_name

    def get_not_overdue(self,obj):
        request = self.context.get('request')
        from datetime import date  
        queryset = obj.invoice.all().exclude(invoice_status='PAYMENT_DONE')
        if 'date' in request.GET and request.GET['date'] !='':
            queryset = queryset.filter(invoice_date__lte = request.GET['date'])
        else:
            queryset = queryset.filter(invoice_date__lte = date.today())
        current_amount = queryset.filter(due_date__gt = date.today()).aggregate(Sum('due_amount'))
        return current_amount['due_amount__sum'] if current_amount['due_amount__sum'] else 00

    def get_not_overdue_invoices(self,obj):
        from datetime import date
        request = self.context.get('request')
        queryset = obj.invoice.all().exclude(invoice_status='PAYMENT_DONE')
        if 'date' in request.GET and request.GET['date'] !='':
            queryset = queryset.filter(invoice_date__lte = request.GET['date'])
        else:
            queryset = queryset.filter(invoice_date__lte = date.today())
        return queryset.filter(due_date__gt = date.today()).count()

    def get_thirty_or_less(self,obj):
        from datetime import date,timedelta
        request = self.context.get('request')
        queryset = obj.invoice.all().exclude(invoice_status='PAYMENT_DONE')
        if 'date' in request.GET and request.GET['date'] !='':
            queryset = queryset.filter(invoice_date__lte = request.GET['date'])
        else:
            queryset = queryset.filter(invoice_date__lte = date.today())
        one_to_thirty_days = queryset.filter(
            due_date__range = [date.today() - timedelta(days=30),date.today() - timedelta(days=2)]
        ).aggregate(Sum('due_amount'))
        
        return one_to_thirty_days['due_amount__sum'] if one_to_thirty_days['due_amount__sum'] else 00

    def get_thirty_one_to_sixty(self,obj):
        from datetime import date,timedelta
        request = self.context.get('request')
        queryset = obj.invoice.all().exclude(invoice_status='PAYMENT_DONE')
        if 'date' in request.GET and request.GET['date'] !='':
            queryset = queryset.filter(invoice_date__lte = request.GET['date'])
        else:
            queryset = queryset.filter(invoice_date__lte = date.today())
        thirty_to_sixty_days = queryset.filter(
            due_date__range = [date.today() - timedelta(days=60),date.today()- timedelta(days=30)]
        ).aggregate(Sum('due_amount'))
        
        return thirty_to_sixty_days['due_amount__sum'] if thirty_to_sixty_days['due_amount__sum'] else 00

    def get_sixty_to_ninty(self,obj):
        from datetime import date,timedelta
        request = self.context.get('request')
        queryset = obj.invoice.all().exclude(invoice_status='PAYMENT_DONE')
        if 'date' in request.GET and request.GET['date'] !='':
            queryset = queryset.filter(invoice_date__lte = request.GET['date'])
        else:
            queryset = queryset.filter(invoice_date__lte = date.today())
        sixty_to_ninty_days = queryset.filter(
            due_date__range = [date.today() - timedelta(days=90),date.today()- timedelta(days=60)]
        ).aggregate(Sum('due_amount'))
        return sixty_to_ninty_days['due_amount__sum'] if sixty_to_ninty_days['due_amount__sum'] else 00

    def get_ninty_or_more(self,obj):
        from datetime import date,timedelta
        request = self.context.get('request')
        queryset = obj.invoice.all().exclude(invoice_status='PAYMENT_DONE')
        if 'date' in request.GET and request.GET['date'] !='':
            queryset = queryset.filter(invoice_date__lte = request.GET['date'])
        else:
            queryset = queryset.filter(invoice_date__lte = date.today())
        ninty_plus_days = queryset.filter(
            due_date__lt = date.today()- timedelta(days=90)
        ).aggregate(Sum('due_amount'))
        return ninty_plus_days['due_amount__sum'] if ninty_plus_days['due_amount__sum'] else 00

    def get_total_amount(self,obj):
        from datetime import date  
        request = self.context.get('request')
        queryset = obj.invoice.all().exclude(invoice_status='PAYMENT_DONE')
        if 'date' in request.GET and request.GET['date'] !='':
            queryset = queryset.filter(invoice_date__lte = request.GET['date'])
        else:
            queryset = queryset.filter(invoice_date__lte = date.today())
        current_amount = queryset.aggregate(Sum('due_amount'))
        return current_amount['due_amount__sum'] if current_amount['due_amount__sum'] else 00

    def get_total_invoices(self,obj):
        from datetime import date  
        request = self.context.get('request')
        queryset = obj.invoice.all().exclude(invoice_status='PAYMENT_DONE')
        if 'date' in request.GET and request.GET['date'] !='':
            queryset = queryset.filter(invoice_date__lte = request.GET['date'])
        else:
            queryset = queryset.filter(invoice_date__lte = date.today())
        return queryset.count()

    class Meta:
        model = Customer
        fields = (
            "customer",
            "not_overdue","not_overdue_invoices",
            "thirty_or_less","thirty_one_to_sixty","sixty_to_ninty",
            "ninty_or_more","total_amount","total_invoices"
        )

class GetCustomerStatementSerializer(serializers.ModelSerializer):
    invoice_amount = serializers.SerializerMethodField()
    amount_paid = serializers.SerializerMethodField()
    amount_due = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()

    def get_balance(self,obj):
        request = self.context.get('request')
        queryset = Invoice.objects.filter(customer=obj.customer).exclude(invoice_status='PAYMENT_DONE')
        current_amount = queryset.filter(due_date__gt = request.GET['date']).aggregate(Sum('due_amount'))
        overdue_amount = queryset.filter(due_date__lt = request.GET['date']).aggregate(Sum('due_amount'))
        return {
            'current_amount':current_amount['due_amount__sum'] if current_amount['due_amount__sum'] else 00,
            'overdue_amount':overdue_amount['due_amount__sum'] if overdue_amount['due_amount__sum'] else 00,
        }

    def get_invoice_amount(self,obj):
        paid = obj.invoice_transaction.all().aggregate(Sum('amount'))
        return obj.due_amount + paid['amount__sum'] if paid['amount__sum'] else obj.due_amount
    
    def get_amount_paid(self,obj):
        paid = obj.invoice_transaction.all().aggregate(Sum('amount'))
        return paid['amount__sum'] if paid['amount__sum'] else 00

    def get_amount_due(self,obj):
        return obj.due_amount

    class Meta:
        model = Invoice
        fields = (
            "invoice_number",
            "invoice_date","due_date",
            "invoice_amount","amount_paid","amount_paid",
            "amount_due","balance"
        )