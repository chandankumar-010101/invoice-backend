import email
from rest_framework import generics
from .models import Organization
from .serializer import OrganizationSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializer import SignupSerializer
from .serializer import LoginSerializers
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from .models import Organization
import apps.account.user_service as user_service


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
        email = request.data.get('email_address')
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        
        serializer = SignupSerializer(data = request.data)
        if serializer.is_valid():

            # # create Organization
            # org = user_service.create_organization(request)

            # #create user
            # user = user_service.create_admin_user(request)

            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
       

        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):

     def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        serializer = LoginSerializers(data = request.data)
        if serializer.is_valid():
            user = authenticate(username=email, password=password)
            print(user)
            return Response({"status": "success", "data": serializer.data}, 
                        status=status.HTTP_200_OK)
      



