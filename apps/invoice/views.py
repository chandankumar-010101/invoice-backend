
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


from .models import Invoice,InvoiceAttachment
from .serializer import InvoiceSerializer,GetInvoiceSerializer

from .schema import  email_invoice_schema
from apps.utility.filters import InvoiceFilter,invoice_filter
from apps.customer.pagination import CustomPagination
from apps.customer.models import Customer

from apps.utility.helpers import SiteUrl,SendMail
from apps.utility.twilio import send_message_on_whatsapp


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
        customer_id = Customer.objects.filter(organization=self.request.user.profile.organization).values_list('id', flat=True)
        queryset = Invoice.objects.filter(customer__id__in=list(customer_id))
        queryset = invoice_filter(self.request,queryset)
        return queryset

    def list(self, request, *args, **kwargs):
        response = super(InvoiceListView, self).list(request, *args, **kwargs)
        customer_id = Customer.objects.filter(organization=request.user.profile.organization).values_list('id', flat=True)
        queryset = Invoice.objects.filter(customer__id__in=list(customer_id))
        total = queryset.aggregate(Sum('total_amount'))
        outstanding_invoice = queryset.filter(~Q(invoice_status='PAYMENT_DONE')).count()
        outstanding_balance = queryset.filter(~Q(invoice_status='PAYMENT_DONE')).aggregate(Sum('total_amount'))
        return Response({
            'message': "Data Fetched Successfully.",
            'data': response.data,
            'outstanding_invoice':outstanding_invoice['total_amount__sum'] if outstanding_invoice['total_amount__sum'] else 00,
            'outstanding_balance':outstanding_balance['total_amount__sum'] if outstanding_balance['total_amount__sum'] else 00,
            'current_amount':0,
            'overdue_amount':0,
            'total':total
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

    delete reterive view for a customer .
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
        }
        get_template = render_to_string(
            'email_template/invoice.html', context)
        SendMail.invoice(
            "Email Invoice From Jasiri", invoice.customer.primary_email, get_template,params['cc'])
        return Response({
            'message': 'Message sent on email successfully.',
        },status=status.HTTP_200_OK)


class SendInvoiceWhatsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,id):
        params = request.data
        invoice = Invoice.objects.get(id=id)
        send_message_on_whatsapp(invoice)
        return Response({
            'message': 'Messgae sent on whats app successfully.',
        },status=status.HTTP_200_OK)

class CsvInvoiceListView(APIView):
    """ Paginated customer list.
    Get list of Customer by user's organization with 
    pagination.
    """

    permission_classes = (IsAuthenticated, )

    def get(self, request):
        customer_id = Customer.objects.filter(organization=self.request.user.profile.organization).values_list('id', flat=True)
        queryset = Invoice.objects.filter(customer__id__in=list(customer_id))
        serializer = GetInvoiceSerializer(queryset, many=True)
        return Response({'data':serializer.data})
