import logging


from rest_framework import status
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter

from django.contrib.auth import get_user_model
from apps.customer import serializers

from apps.customer.serializers import (
    CustomerSerializer, CustomerFilterSerializer,
    AlternateContactSerializer, CustomerListSerializer,
    CustomerRetriveDestroySerializer,UpdateCustomerSerializer,
)
from apps.customer.models import AlternateContact
import apps.customer.response_messages as resp_msg

from .models import Customer
from apps.account.models import UserProfile
from .pagination import CustomPagination
import apps.customer.models as customer_models

User = get_user_model()
logger = logging.getLogger(__name__)

# Create your views here.
class CustomerListView(generics.ListAPIView):
    """ Paginated customer list.
    Get list of Customer by user's organization with 
    pagination.
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerListSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated)
    pagination_class.page_size = 2
    search_fields = ['full_name']
    filter_backends = (SearchFilter)


    def list(self, request, *args, **kwargs):
        params = request.GET
        organization = request.user.profile.organization
        queryset = Customer.objects.filter(organization=organization)
        if 'search' in params and params['search'] !='':
            queryset = queryset.filter(full_name__icontains=params['search'])

        if 'order_by' in params and params['order_by'] !='':
            queryset = queryset.order_by(params['order_by'])
        serializer = self.serializer_class(queryset, many=True)
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)

class CsvCustomerListView(APIView):
    """ Paginated customer list.
    Get list of Customer by user's organization with 
    pagination.
    """

    permission_classes = (IsAuthenticated, )

    def get(self, request):
        organization = request.user.profile.organization
        queryset = Customer.objects.filter(organization=organization)
        serializer = CustomerListSerializer(queryset, many=True)
        return Response({'data':serializer.data})


class CustomerCreateView(generics.CreateAPIView):
    """create customer record.
    create Customer and its alternate record.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = (IsAuthenticated)

    def create(self, serializer):
        params = serializer.data
        if params['customer_type'] == '':
            params['customer_type'] = 5
        if params['payments_term'] == '':
            params['payments_term'] = 7
        if params['payments_credit'] == '':
            params['payments_credit'] = 0
        organization = serializer.user.profile.organization
        is_alternate_contact = serializer.data.get('alternate_contact')

        is_email_exist = Customer.objects.filter(
            primary_email=serializer.data.get('primary_email'))
        if len(is_email_exist) > 0:
            return Response({
                'detail': [resp_msg.CUSTOMER_EMAIL_ALREADY_EXIST]
            },status=status.HTTP_400_BAD_REQUEST)

        is_phone_exist = Customer.objects.filter(
            primary_phone=serializer.data.get('primary_phone'))
        if len(is_phone_exist) > 0:
            return Response({
                'detail': [resp_msg.CUSTOMER_PHONE_ALREADY_EXIST]
            },status=status.HTTP_400_BAD_REQUEST)

        if serializer.data.get('alternate_contact') is not None:
            alternate_contact = serializer.data.pop('alternate_contact')
        
        instance = Customer.objects.create(
            **params, user=serializer.user,
            organization=organization
        )
        instance.save()
        if is_alternate_contact and alternate_contact['alternate_name'] != None or alternate_contact['alternate_role'] != None or alternate_contact['alternate_email'] != None or alternate_contact['alternate_phone'] != None:
            alternate_obj = AlternateContact.objects.create(
                **alternate_contact, customer=instance)
            alternate_obj.save()
            alternate_serializer = AlternateContactSerializer(alternate_contact)
            serializer.data['alternate_contact'] = alternate_serializer.data
        return Response({
            'data': serializer.data
        },status=status.HTTP_201_CREATED)


class UpdateCustomerView(APIView):
    ''' View for update customer details '''

    permission_classes = [IsAuthenticated]

    def post(self,request,pk):
        params = request.data
        data = {}
        if params['customer_type'] == '':
            params['customer_type'] = 5
        if params['payments_term'] == '':
            params['payments_term'] = 7
        if params['payments_credit'] == '':
            params['payments_credit'] = 0

        try:
            instance = Customer.objects.get(id=pk)
            serializer = UpdateCustomerSerializer(instance,data=params, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data['customer'] = serializer.data
            if hasattr(instance, 'customer'):
                alternative_serializer = AlternateContactSerializer(instance.customer,data=params['alternate_contact'], partial=True)
            else:
                params['alternate_contact']['customer'] = instance.id
                alternative_serializer = AlternateContactSerializer(data=params['alternate_contact'])
            alternative_serializer.is_valid(raise_exception=True)
            alternative_serializer.save()
            data['alternative_contact'] = alternative_serializer.data
            return Response({
                'data':data
            }, status=status.HTTP_200_OK)
        except Exception as error:
            logger.error(error)
            return Response({
                'detail': [error.args[0]]
            }, status=status.HTTP_400_BAD_REQUEST)


class RetrieveDeleteCustomer(generics.RetrieveDestroyAPIView):
    """Customer detail operations. 
    delete reterive view for a customer .
    """

    lookup_field = 'id'
    queryset = Customer.objects.all()
    serializer_class = CustomerRetriveDestroySerializer


class CustomerFilterView(APIView):
    ''' View Filter for customer list by customer name '''

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
        customer_list = request.data.get('customer_list', [])
        if len(customer_list) == 0:
            return Response({
                'detail': [resp_msg.CUSTOMER_DELETE_VALIDATION]
            },status=status.HTTP_400_BAD_REQUEST)
        queryset = customer_models.Customer.objects.filter(pk__in=customer_list)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)