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
import apps.account.user_service as user_service
from .models import Organization
import apps.account.response_messages as resp_msg


# Create your views here.
class OrganizationListView(generics.ListAPIView):

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

class OrganizationCreateView(generics.CreateAPIView):

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

class SignupView(APIView):
    
    def post(self, request, *args, **kwargs):

        serializer = SignupSerializer(data = request.data)
        if serializer.is_valid():

            # create Organization
            org = user_service.create_organization(request)
            
            #create user
            try:
                user = user_service.create_admin_user(request)
            except Exception as e:
                return Response({'status':'error','error':resp_msg.USER_CREATION_UNSUCCESSFULL}, 
                status=status.HTTP_400_BAD_REQUEST)

            #create profile
            profile = user_service.create_user_profile(request, user, org)
            if (org is not None and 
                user is not None and 
                profile is not None):
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       

        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):

     def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        serializer = LoginSerializers(data = request.data)
        if serializer.is_valid():
            user = authenticate(username=email, password=password)
            return Response({"status": "success", "data": serializer.data}, 
                        status=status.HTTP_200_OK)
      



