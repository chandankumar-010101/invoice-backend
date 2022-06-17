from rest_framework import generics
from .models import Customer
from .pagination import CustomPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.customer.serializers import (CustomerSerializer, CustomerFilterSerializer, 
                                    AlternateContactSerializer)
from apps.customer.models import AlternateContact
import apps.customer.response_messages as resp_msg
from rest_framework import status


# Create your views here.
class CustomerListView(generics.ListAPIView, generics.RetrieveAPIView):

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    pagination_class = CustomPagination

class CustomerCreateView(generics.CreateAPIView):

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def create(self, serializer):
        is_alternate_contact = serializer.data.get('alternate_contact')

        is_email_exist = Customer.objects.filter(email=serializer.data.get('email'))
        if len(is_email_exist) > 0:
            return Response({'detail':[resp_msg.CUSTOMER_EMAIL_ALREADY_EXIST]}, 
            status=status.HTTP_400_BAD_REQUEST)
        
        is_phone_exist = Customer.objects.filter(phone=serializer.data.get('phone'))
        if len(is_phone_exist) > 0:
            return Response({'detail':[resp_msg.CUSTOMER_PHONE_ALREADY_EXIST]}, 
            status=status.HTTP_400_BAD_REQUEST)

        if serializer.data.get('alternate_contact') is not None:
            alternate_contact = serializer.data.pop('alternate_contact')
            
        instance = Customer.objects.create(**serializer.data)
        instance.save()

        if is_alternate_contact:
            alternate_obj = AlternateContact.objects.create(**alternate_contact, customer=instance)
            alternate_obj.save()
            alternate_serializer = AlternateContactSerializer(alternate_contact)
            serializer.data['alternate_contact'] = alternate_serializer.data

        return Response({'data':serializer.data},
                        status=status.HTTP_201_CREATED)

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
