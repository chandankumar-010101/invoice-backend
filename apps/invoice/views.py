from rest_framework import generics
from .models import Invoice
from .serializer import InvoiceSerializer


# Create your views here.
class InvoiceListView(generics.ListAPIView):

    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

class InvoiceCreateView(generics.CreateAPIView):

    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
