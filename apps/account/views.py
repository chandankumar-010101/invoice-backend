from cmath import log
import email
from django.forms import PasswordInput
from rest_framework import generics
from .models import Organization
from .serializer import OrganizationSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializer import SignupSerializer
from .serializer import LoginSerializers
from django.contrib.auth import authenticate, login


# Create your views here.
class OrganizationListView(generics.ListAPIView):

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

class OrganizationCreateView(generics.CreateAPIView):

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

class SignupView(APIView):
    
    def post(self, request, *args, **kwargs):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email_address = request.data.get('email_address')
        phone_number = request.data.get('phone_number')
        company_name =  request.data.get('company_name')
        industry = request.data.get('industry')
        annual_turnover = request.data.get('annual_turnover')
        accounting_software = request.data.get('accounting_software')
        invoice_issue_month = request.data.get('invoice_issue_month')
        password = request.data.get('password')
        
        serializer = SignupSerializer(data = request.data)
        if serializer.is_valid():
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
       

        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):

     def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        print(email)
        print(password)
        
        serializer = LoginSerializers(data = request.data)
        if serializer.is_valid():
            return Response({"status": "success", "data": serializer.data}, 
                        status=status.HTTP_200_OK)
      



