from rest_framework import generics
from .models import Customer
from apps.account.models import UserProfile
from .pagination import CustomPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.customer.serializers import (CustomerSerializer, CustomerFilterSerializer, 
                                    AlternateContactSerializer, CustomerListSerializer,
                                    CustomerRetriveDestroySerializer)
from apps.customer.models import AlternateContact
import apps.customer.response_messages as resp_msg
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
import apps.customer.models as customer_models
User = get_user_model()


# Create your views here.
class CustomerListView(generics.ListAPIView):
    """ Paginated customer list. 
    
    Get list of Customer by user's organization with 
    pagination.
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerListSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    pagination_class.page_size=2

    def list(self, request, *args, **kwargs):
        organization = request.user.profile.organization
        queryset = Customer.objects.filter(organization=organization)
        serializer = self.serializer_class(queryset, many=True)
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page) 

class CustomerCreateView(generics.CreateAPIView):
    """create customer record. 
    
    create Customer and its alternate record.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, serializer):
        organization = serializer.user.profile.organization
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
            
        instance = Customer.objects.create(**serializer.data, user=serializer.user, 
                                        organization=organization)
        instance.save()

        if is_alternate_contact:
            alternate_obj = AlternateContact.objects.create(**alternate_contact, customer=instance)
            alternate_obj.save()
            alternate_serializer = AlternateContactSerializer(alternate_contact)
            serializer.data['alternate_contact'] = alternate_serializer.data

        return Response({'data':serializer.data},
                        status=status.HTTP_201_CREATED)

class RetrieveDeleteCustomer(generics.RetrieveDestroyAPIView):
    """Customer detail operations. 
    
    delete reterive view for a customer .
    """

    lookup_field = 'id'
    queryset = Customer.objects.all()
    serializer_class = CustomerRetriveDestroySerializer

class CustomerFilterView(APIView):

    serializer_class = CustomerFilterSerializer

    def get(self, request):
        q = request.query_params.get('q', None)
        queryset = Customer.objects.filter(full_name__contains=q)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

class DeleteMultipleCustomerView(APIView):
    """Customer delete operations. 
    
    Delete multiple customer at once.
    """
    def post(self, request):
        customer_list = request.data.get('customer_list',[])

        if len(customer_list) == 0:
            return Response({'detail':[resp_msg.CUSTOMER_DELETE_VALIDATION]},
                            status=status.HTTP_400_BAD_REQUEST)

        queryset = customer_models.Customer.objects.filter(pk__in=customer_list)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
