from rest_framework import generics
from .models import Customer
from .pagination import CustomPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.customer.serializers import CustomerSerializer, CustomerFilterSerializer


# Create your views here.
class CustomerListView(generics.ListAPIView, generics.RetrieveAPIView):

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    pagination_class = CustomPagination

class CustomerCreateView(generics.CreateAPIView):

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class RetrieveUpdateDeleteCustomer(generics.RetrieveUpdateDestroyAPIView):

    lookup_field = 'id'
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class CustomerFilterView(APIView):

    serializer_class = CustomerFilterSerializer

    def get(self, request):
        q = request.query_params.get('q', None)
        queryset = Customer.objects.filter(full_name__contains=q)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
