import logging


from datetime import date  
from drf_yasg.utils import swagger_auto_schema

from django.template.loader import render_to_string


from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser

from django.db.models import Q,Sum
from rest_framework.viewsets import ModelViewSet


from .models import Invoice,InvoiceAttachment,InvoiceTransaction,PaymentMethods,PaymentReminder
from .serializer import (
    InvoiceSerializer,
    GetInvoiceSerializer,PaymentReminderSerializer,
    CardSerializer,GetPaymentSerializer
)

from .schema import  (
    email_invoice_schema,
    record_payment_schema,whats_invoice_schema,
    payment_method_schema,roles_permissions_schema,
    card_schema
)
from apps.utility.filters import InvoiceFilter,invoice_filter
from apps.customer.pagination import CustomPagination
from apps.customer.models import Customer

from apps.utility.helpers import SiteUrl,SendMail,GenerateLink
from apps.utility.twilio import send_message_on_whatsapp

from apps.utility.peach import PeachPay
logger = logging.getLogger(__name__)

# Create your views here.

class InvoiceListView(generics.ListAPIView):
    filter_class = InvoiceFilter
    pagination_class = CustomPagination
    pagination_class.page_size = 2
    serializer_class = GetInvoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    search_fields = ['customer__full_name',"invoice_number","invoice_id"]

    
    def get_queryset(self):
        admin_user = self.request.user.parent if self.request.user.parent else self.request.user

        customer_id = Customer.objects.filter(organization=admin_user.profile.organization).values_list('id', flat=True)
        queryset = Invoice.objects.filter(customer__id__in=list(customer_id)).exclude(invoice_status='PAYMENT_DONE')
        queryset = invoice_filter(self.request,queryset)
        params = self.request.GET
        if 'order_by' in params and params['order_by'] !='':
            queryset = queryset.order_by(params['order_by'])
        return queryset

    def list(self, request, *args, **kwargs):
        response = super(InvoiceListView, self).list(request, *args, **kwargs)
        admin_user = request.user.parent if request.user.parent else request.user

        customer_id = Customer.objects.filter(organization=admin_user.profile.organization).values_list('id', flat=True)
        queryset = Invoice.objects.filter(customer__id__in=list(customer_id))
        outstanding_invoice = queryset.filter(~Q(invoice_status='PAYMENT_DONE')).count()
        outstanding_balance = queryset.filter(~Q(invoice_status='PAYMENT_DONE')).aggregate(Sum('due_amount'))
        queryset = queryset.exclude(invoice_status='PAYMENT_DONE')
        current_amount = queryset.filter(due_date__gt = date.today()).aggregate(Sum('due_amount'))
        overdue_amount = queryset.filter(due_date__lt = date.today()).aggregate(Sum('due_amount'))
        q = self.get_queryset()
        total = q.aggregate(Sum('due_amount'))
        return Response({
            'message': "Data Fetched Successfully.",
            'data': response.data,
            'outstanding_invoice':outstanding_invoice,
            'outstanding_balance':outstanding_balance['due_amount__sum'] if outstanding_balance['due_amount__sum'] else 00,
            'current_amount':current_amount['due_amount__sum'] if current_amount['due_amount__sum'] else 00,
            'overdue_amount':overdue_amount['due_amount__sum'] if overdue_amount['due_amount__sum'] else 00,
            'total':total['due_amount__sum'] if total['due_amount__sum'] else 00
        }, status=status.HTTP_200_OK)

class DeleteInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,id):
        Invoice.objects.filter(id=id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class InvoiceCreateView(generics.CreateAPIView):

    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (FormParser, MultiPartParser)

    def get_serializer_context(self):
        return {'request': self.request}
        
    def create(self, request, *args, **kwargs):
        try:
            params = request.data
            if Invoice.objects.filter(invoice_number = params['invoice_number']).exists():
                return Response({
                    'detail': ["Invoice Number is already exists."]
                },status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(data=params)
            serializer.is_valid(raise_exception=True)
            invoice = serializer.save()
            if 'attachment' in request.FILES:
                for data in request.FILES.getlist('attachment'):
                    InvoiceAttachment.objects.create(
                        invoice = invoice,
                        attachment = data
                    )
            return Response({
                'id':invoice.id,
                'message': 'Invoice created successfully.',
            }, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({
                'detail': [error.args[0]]
            }, status=status.HTTP_400_BAD_REQUEST)


class InvoiceUpdateView(generics.UpdateAPIView):

    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (FormParser, MultiPartParser)

    def update(self, request,pk, *args, **kwargs):
        try:
            params = request.data
            instance = Invoice.objects.get(pk = pk)
            if instance.invoice_number != params['invoice_number'] and Invoice.objects.filter(invoice_number = params['invoice_number']).exists():
                return Response({
                    'detail': ["Invoice Number is already exists."]
                },status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(instance,data=params,partial=True)
            serializer.is_valid(raise_exception=True)
            invoice = serializer.save()
            if 'attachment' in request.FILES:
                for data in request.FILES.getlist('attachment'):
                    InvoiceAttachment.objects.create(
                        invoice = invoice,
                        attachment = data
                    )
            return Response({
                'id':invoice.id,
                'message': 'Invoice updated successfully.',
            }, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({
                'detail': [error.args[0]]
            }, status=status.HTTP_400_BAD_REQUEST)

class RetrieveInvoiceView(generics.RetrieveDestroyAPIView):
    """Customer detail operations. 

    delete reterive view for a customer.
    """

    lookup_field = 'id'
    queryset = Invoice.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GetInvoiceSerializer

class DeleteInvoiceAttachmentView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,id):
        InvoiceAttachment.objects.filter(id=id).delete()
        return Response({
            'message': 'Attachment deleted successfully.',
        },status=status.HTTP_204_NO_CONTENT)

class SendInvoiceEmailView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(request_body=email_invoice_schema, operation_description='Email Invoice')
    def post(self,request,id):
        params = request.data
        invoice = Invoice.objects.get(id=id)
        context = {
            'invoice':invoice,
            'subject':params['subject'],
            'body':params['body'],
            'site_url': str(SiteUrl.site_url(request)),
            'payment_schedule':GenerateLink.generate_invoice_link(invoice)
        }
        invoice.invoice_status = 'SENT'
        invoice.save()
        get_template = render_to_string(
            'email_template/invoice.html', context)
        SendMail.invoice(
            "You have an invoice from {} due on {}".format(invoice.customer.organization.company_name,invoice.due_date), invoice.customer.primary_email, get_template,params['cc'],invoice)
        return Response({
            'message': 'Message sent on email successfully.',
        },status=status.HTTP_200_OK)


class SendInvoiceWhatsView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=whats_invoice_schema, operation_description='Whatsapp Invoice')

    def post(self,request,id):
        params = request.data
        invoice = Invoice.objects.get(id=id)
        send_message_on_whatsapp(invoice,params)
        invoice.invoice_status = 'SENT'
        invoice.save()
        return Response({
            'message': 'Messgae sent on WhatsApp successfully.',
        },status=status.HTTP_200_OK)

class CsvInvoiceListView(APIView):
    """ Paginated customer list.
    Get list of Customer by user's organization with 
    pagination.
    """

    permission_classes = (IsAuthenticated, )

    def get(self, request):
        admin_user = request.user.parent if request.user.parent else request.user
        customer_id = Customer.objects.filter(organization=admin_user.profile.organization).values_list('id', flat=True)
        queryset = Invoice.objects.filter(customer__id__in=list(customer_id)).exclude(invoice_status='PAYMENT_DONE')
        serializer = GetInvoiceSerializer(queryset, many=True)
        return Response({'data':serializer.data})

class RecordPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(request_body=record_payment_schema, operation_description='Record Payment')
    def post(self,request,id):
        params = request.data
        try:
            invoice = Invoice.objects.get(id=id)
            InvoiceTransaction.objects.create(
                invoice = invoice,
                amount = params['amount'],
                payment_type = 'Manually',
                payment_mode = params['payment_mode']
            )
            if invoice.due_amount != float(params['amount']):
                invoice.invoice_status = 'PARTIALLY_DONE'
                invoice.due_amount -= float(params['amount'])
            else:
                invoice.due_amount = 0
                invoice.invoice_status = 'PAYMENT_DONE'
            invoice.save()
            return Response({
                'message': 'Payment Recorded successfully.',
            },status=status.HTTP_200_OK)
        except Exception as error:
            return Response({
                'detail': [error.args[0]]
            }, status=status.HTTP_400_BAD_REQUEST)

from apps.utility.peach import PeachPay

class SendReminderView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=email_invoice_schema, operation_description='Send Reminder Invoice')
    def post(self,request,id):
        from apps.utility.cron import send_email
        try:
            invoice = Invoice.objects.get(id=id)
            is_sucess, url = PeachPay().generate_payment_link(invoice)
            if is_sucess:
                context = {
                    'amount':invoice.due_amount,
                    'invoice':invoice,
                    'subject':params['subject'],
                    'body':params['body'],
                    'site_url': str(SiteUrl.site_url(request)),
                    'payment':url
                }
                get_template = render_to_string('email_template/reminder.html', context)
                SendMail.invoice(
                    "You have an invoice reminder from {} due on {}".format(invoice.customer.organization.company_name,invoice.due_date), invoice.customer.primary_email, get_template,[],invoice)
                invoice.invoice_status = 'SENT'
                invoice.reminders +=1
                invoice.save()
                return Response({
                    'message': 'Reminder sent successfully.',
                },status=status.HTTP_200_OK)
            return Response({
                'detail': [url]
            }, status=status.HTTP_400_BAD_REQUEST)   
        except Exception as error:
            return Response({
                'detail': [error.args[0]]
            }, status=status.HTTP_400_BAD_REQUEST)

        

class PaymentMethodeView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(request_body=payment_method_schema, operation_description='Payment Method')
    def post(self,request):
        params = request.data
        admin_user = request.user.parent if request.user.parent else request.user

        instance,_ = PaymentMethods.objects.get_or_create(user=admin_user)
        if 'is_bank_transfer' in params and params['is_bank_transfer'] != '':
            instance.is_bank_transfer = params['is_bank_transfer'].capitalize() 
        if 'is_card_payment' in params and params['is_card_payment'] != '':
            instance.is_card_payment = params['is_card_payment'].capitalize() 
        if 'is_mobile_money' in params and params['is_mobile_money'] != '':
            instance.is_mobile_money = params['is_mobile_money'].capitalize() 
        if 'auto_payment_reminder' in params and params['auto_payment_reminder'] != '':
            instance.auto_payment_reminder = params['auto_payment_reminder'].capitalize() 

        instance.save()
        return Response({
            'message': 'Payment method updated successfully.',
        },status=status.HTTP_200_OK)


class PaymentReminderView(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PaymentReminder.objects.all()
    serializer_class = PaymentReminderSerializer
    lookup_field='id'

    def get_queryset(self):
        admin_user = self.request.user.parent if self.request.user.parent else self.request.user

        return PaymentReminder.objects.filter(user=admin_user)
    
    def get_serializer_context(self):
        return {'request': self.request}

    def create(self, request, *args, **kwargs):
        instance = super(PaymentReminderView, self).create(request, *args, **kwargs)
        return Response({"message": "Reminder Create successfully", "data": instance.data})


    def list(self, request, *args, **kwargs):
        results = super(PaymentReminderView, self).list(
            request, *args, **kwargs)
        return Response({
            'data': results.data,
            'message': 'Data fetched successfully'
        }, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        results = super(PaymentReminderView, self).retrieve(
            request, *args, **kwargs)
        return Response({
            'data': results.data,
            'message': 'Particular Data fetched successfully'
        }, status=status.HTTP_200_OK)

    
    def update(self, request, *args, **kwargs):
       
        instance = super(PaymentReminderView, self).update(request, *args, **kwargs)
        return Response({"message": "Customer Update successfully", "data": instance.data})

    def destroy(self, request, *args, **kwargs):
        PaymentReminder.objects.filter(id=kwargs["id"]).delete()
        return Response({"message": "Customer delete successfully"})


class SchedulePaymentView(APIView):
    def get(self,request,uuid):
        try:
            invoice = GenerateLink.decode_invoice_link(uuid)
            is_sent,data = PeachPay().generate_payment_link(invoice)
            if is_sent:
                return Response({"message": "Payment schedule successfully"})
            return Response({
                "message": data
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            logger.error([error.args[0]])
            return Response({
                "detail": [error.args[0]]
            }, status=status.HTTP_400_BAD_REQUEST)

class UpdateRolesAndPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=roles_permissions_schema, operation_description='Roles and Permission')
    def post(self,request):
        params = request.data
        admin_user = request.user.parent if request.user.parent else request.user
        admin_user.roles_permission_user.roles = params['roles']
        admin_user.roles_permission_user.save()
        return Response({"message": "Roles and Permissions updated successfully"})

class BillingPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=card_schema, operation_description='Save Card Details')
    def post(self, request):
        params = request.data
        admin_user = request.user.parent if request.user.parent else request.user

        if hasattr(admin_user, 'card_details_user'):
            serializer = CardSerializer(admin_user.card_details_user,data=params,context={'request':request},partial=True)
        else:
            serializer = CardSerializer(data=params,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(serializer.errors)
        return Response({'detail':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PaymentListView(generics.ListAPIView):
    filter_class = InvoiceFilter
    pagination_class = CustomPagination
    pagination_class.page_size = 2
    serializer_class = GetPaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    search_fields = ['customer__full_name',"invoice_number","invoice_id"]

    
    def get_queryset(self):
        admin_user = self.request.user.parent if self.request.user.parent else self.request.user
        customer_id = Customer.objects.filter(organization=admin_user.profile.organization).values_list('id', flat=True)
        queryset = Invoice.objects.filter(customer__id__in=list(customer_id),invoice_status='PAYMENT_DONE')
        queryset = invoice_filter(self.request,queryset)
        params = self.request.GET
        
        if 'order_by' in params and params['order_by'] !='':
            if 'payment_method' in params['order_by'] or 'amount' in params['order_by']:
                pass
            else:
                queryset = queryset.order_by(params['order_by'])
        return queryset

    def list(self, request, *args, **kwargs):
        response = super(PaymentListView, self).list(request, *args, **kwargs)
        return Response({
            'message': "Data Fetched Successfully.",
            'data': response.data,
        }, status=status.HTTP_200_OK)


class CsvPaymentListView(APIView):
    """ Paginated customer list.
    Get list of Customer by user's organization with 
    pagination.
    """

    permission_classes = (IsAuthenticated, )

    def get(self, request):
        admin_user = request.user.parent if request.user.parent else request.user
        customer_id = Customer.objects.filter(organization=admin_user.profile.organization).values_list('id', flat=True)
        queryset = Invoice.objects.filter(customer__id__in=list(customer_id),invoice_status='PAYMENT_DONE')
        serializer = GetPaymentSerializer(queryset, many=True)
        return Response({'data':serializer.data})


class PeachWebhookView(APIView):
    def get(self,request):
        print(request.GET)
        return Response({
            "message": 'ok'
        }, status=status.HTTP_200_OK)


    def post(self,request):
        params = request.data
        print(params)
        print("#########TYPE",params['Event[type]'])
        return Response({
            "message": 'ok'
        }, status=status.HTTP_200_OK)

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
@csrf_exempt
@require_POST
def peach_webhook(request):
    jsondata = request.body
    data = json.loads(jsondata)
    print("data",data)
    return HttpResponse(status=200)