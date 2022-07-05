
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser

from .models import Invoice,InvoiceAttachment
from .serializer import InvoiceSerializer,GetInvoiceSerializer

from apps.utility.filters import InvoiceFilter,invoice_filter
from apps.customer.pagination import CustomPagination

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
        queryset = Invoice.objects.all()

        queryset = invoice_filter(self.request,queryset)
        return queryset


    def list(self, request, *args, **kwargs):
        response = super(InvoiceListView, self).list(
            request, *args, **kwargs)
        return Response({
            'message': "Data Fetched Successfully.",
            'data': response.data,
        }, status=status.HTTP_200_OK)
    

class InvoiceCreateView(generics.CreateAPIView):

    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated,]
    parser_classes = (FormParser, MultiPartParser)

    def get_serializer_context(self):
        return {'request': self.request}

    def post(self, request, *args, **kwargs):
        try:
            params = request.data
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
                'message': 'Invoice created successfully.',
            }, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({
                'detail': [error.args[0]]
            }, status=status.HTTP_400_BAD_REQUEST)